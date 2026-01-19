from fastapi_mail import ConnectionConfig

from src.config.settings import settings

if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
    mail_config = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_USERNAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_HOST,
        MAIL_FROM_NAME=settings.PROJECT_NAME,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER="src/templates",
    )
else:
    mail_config = None
