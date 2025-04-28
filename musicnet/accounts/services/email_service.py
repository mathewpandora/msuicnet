import os
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def send_verification_email(user):
    try:
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f'http://127.0.0.1:8000/account/verify-email/?uid={uidb64}&token={token}'

        send_mail(
            'Подтверждение электронной почты',
            f'Перейдите по ссылке для подтверждения: {verification_link}',
            os.getenv('DEFAULT_FROM_EMAIL'),  # Используем из настроек
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Ошибка при отправке email: {str(e)}")
