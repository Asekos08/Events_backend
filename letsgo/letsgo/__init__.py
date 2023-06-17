from celery_app import app as celery_app

__all__ = ('celery_app', )
# Чтобы celery стартанула вместе с нашим приложением
