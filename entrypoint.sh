set -e

flask db upgrade || true

python3 /app/playground.py || true

exec "$@"
