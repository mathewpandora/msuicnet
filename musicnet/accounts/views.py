import logging
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from .models import User
from accounts.serializers import UserRegisterSerializer, UserLoginSerializer, ChangePasswordSerializer, UserUpdateSerializer, UserProfileSerializer


logger = logging.getLogger(__name__)

class RegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        username = request.data.get('username')

        logger.info(f"Попытка регистрации: email={email}, username={username}")

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if user_by_email and user_by_email.username != username:
            logger.warning(f"Ошибка регистрации: аккаунт с таким email {email} уже существует.")
            return Response(
                {"detail": "Аккаунт с таким email уже существует. Используйте правильный username."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user_by_username and user_by_username.email != email:
            logger.warning(f"Ошибка регистрации: username {username} уже занят.")
            return Response(
                {"detail": "Username уже занят другим пользователем."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_by_email and user_by_email.username == username:
            if user_by_email.is_email_verified:
                logger.info(f"Пользователь с email {email} уже зарегистрирован.")
                return Response(
                    {"detail": "Вы уже зарегистрированы. Можете войти в аккаунт."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                self.get_serializer().send_verification_email(user_by_email)
                logger.info(f"Отправлено повторное письмо для подтверждения email для пользователя {email}.")
                return Response(
                    {"detail": "Аккаунт существует, но email не подтверждён. Письмо отправлено повторно."},
                    status=status.HTTP_200_OK
                )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        serializer.send_verification_email(user)

        logger.info(f"Пользователь с email {email} успешно зарегистрирован.")
        return Response(
            {"detail": "Пользователь успешно зарегистрирован. Письмо с подтверждением отправлено на email."},
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logger.info("Попытка входа пользователя.")
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f"Пользователь {user.username} вошел в систему с токеном {token.key}.")
        return Response({'token': token.key})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info(f"Выход пользователя {request.user.username}.")
        request.user.auth_token.delete()
        logout(request)
        return Response({"detail": "Вы успешно вышли из системы"}, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.info(f"Попытка смены пароля для пользователя {request.user.username}.")
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            logger.warning(f"Неверный старый пароль для пользователя {user.username}.")
            return Response({"detail": "Неверный старый пароль"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        logger.info(f"Пароль пользователя {user.username} успешно обновлен.")
        return Response({"detail": "Пароль успешно обновлён"}, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        logger.info(f"Удаление аккаунта пользователя {request.user.username}.")
        request.user.delete()
        return Response({"detail": "Аккаунт удалён"}, status=status.HTTP_204_NO_CONTENT)


class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        logger.info(f"Попытка подписки на пользователя с ID {user_id}.")
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(f"Пользователь с ID {user_id} не найден.")
            return Response({'error': 'Пользователь не найден.'}, status=status.HTTP_404_NOT_FOUND)

        if target_user == request.user:
            logger.warning(f"Пользователь {request.user.username} попытался подписаться на самого себя.")
            return Response({'error': 'Нельзя подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.followers.add(target_user)
        logger.info(f"Пользователь {request.user.username} подписался на {target_user.username}.")
        return Response({'success': f'Вы подписались на {target_user.username}.'}, status=status.HTTP_200_OK)


def verify_email(request):
    uidb64 = request.GET.get('uid')
    token = request.GET.get('token')

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        logger.error(f"Ошибка при подтверждении email: пользователь не найден или ссылка некорректна.")
        return HttpResponse('Ссылка недействительна или устарела.', status=400)

    if user is not None and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.save()
        logger.info(f"Email пользователя {user.username} успешно подтвержден.")
        return HttpResponse('Email успешно подтверждён!')
    else:
        logger.error(f"Неудачная попытка подтверждения email для пользователя {user.username}.")
        return HttpResponse('Ссылка недействительна или устарела.', status=400)
