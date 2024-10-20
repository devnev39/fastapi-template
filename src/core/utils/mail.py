from fastapi_mail import FastMail, MessageSchema
from src.config.mail_config import mail_config


async def send_mail(
    emails: list[str], cc: list[str], subject: str, body, template_name: str
):
    try:
        message = MessageSchema(
            subject=subject, recipients=emails, template_body=body, subtype="html"
        )
        fm = FastMail(mail_config)
        await fm.send_message(message, template_name=template_name)
        return True
    except Exception as ex:
        raise ex
