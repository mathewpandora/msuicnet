#!/bin/bash
# wait-for-mysql.sh

set -e

host="$MYSQL_HOST"

until mysqladmin ping -h "$host" --silent; do
  >&2 echo "⏳ Ждём, пока MySQL будет готов к подключениям..."
  sleep 1
done

>&2 echo "✅ MySQL готов!"

exec "$@"
