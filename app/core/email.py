# app/core/email.py
"""
Sends transactional emails (currently just OTP codes) over Gmail's SMTP
relay. No third-party email API/SDK is required — Gmail lets any account
send mail through smtp.gmail.com once you generate an "App Password":

    1. Turn on 2-Step Verification on the Gmail account you want to send from.
    2. Go to https://myaccount.google.com/apppasswords
    3. Create an app password (name it e.g. "RoadDamageAI") and copy the
       16-character code.
    4. Put that code (NOT your normal Gmail password) in SMTP_PASSWORD in
       your .env, and the Gmail address itself in SMTP_USER.

If SMTP_USER / SMTP_PASSWORD are left blank (e.g. in local dev), the OTP is
logged to the console instead of emailed, so registration still works
without any mail setup.
"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.logging import logger
from app.exceptions.custom import AppException


class EmailManager:
    @staticmethod
    def _build_otp_message(to_email: str, otp_code: str) -> MIMEMultipart:
        from_name = settings.SMTP_FROM_NAME
        from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER

        message = MIMEMultipart("alternative")
        message["Subject"] = f"{otp_code} is your {from_name} verification code"
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = to_email

        text_body = (
            f"Your {from_name} verification code is: {otp_code}\n\n"
            f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes. "
            f"If you didn't request this, you can safely ignore this email."
        )

        html_body = f"""\
<html>
  <body style="margin:0;padding:0;background-color:#0f172a;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f172a;padding:32px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="420" cellpadding="0" cellspacing="0"
                 style="background-color:#0b1220;border:1px solid #1e293b;border-radius:16px;overflow:hidden;">
            <tr>
              <td style="padding:28px 32px 8px 32px;text-align:center;">
                <div style="font-size:13px;font-weight:800;letter-spacing:1px;color:#38bdf8;text-transform:uppercase;">
                  {from_name}
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding:8px 32px 0 32px;text-align:center;">
                <p style="color:#94a3b8;font-size:13px;margin:0 0 20px 0;">
                  Use the code below to verify {to_email}
                </p>
                <div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:18px 0;margin-bottom:20px;">
                  <span style="font-size:32px;font-weight:800;letter-spacing:10px;color:#f8fafc;">
                    {otp_code}
                  </span>
                </div>
                <p style="color:#64748b;font-size:12px;margin:0 0 24px 0;">
                  This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.
                  Didn't request this? You can safely ignore this email.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

        message.attach(MIMEText(text_body, "plain"))
        message.attach(MIMEText(html_body, "html"))
        return message

    @staticmethod
    def send_otp_email(to_email: str, otp_code: str) -> None:
        # Local/dev fallback: no SMTP credentials configured -> just log it,
        # so `npm run dev` / local testing never gets blocked on real email.
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning(
                f"[DEV MODE - no SMTP credentials set] OTP for {to_email}: {otp_code}"
            )
            return

        message = EmailManager._build_otp_message(to_email, otp_code)
        context = ssl.create_default_context()

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                server.starttls(context=context)
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(
                    settings.SMTP_FROM_EMAIL or settings.SMTP_USER,
                    to_email,
                    message.as_string(),
                )
            logger.info(f"OTP email dispatched to {to_email}")
        except smtplib.SMTPAuthenticationError as e:
            # Wrong SMTP_USER / SMTP_PASSWORD (or using a normal Gmail
            # password instead of a 16-char App Password).
            logger.error(f"SMTP auth failed sending to {to_email}: {e}")
            raise AppException(
                status_code=502,
                detail="Email service is misconfigured (SMTP authentication failed). Please contact support.",
            ) from e
        except (smtplib.SMTPException, TimeoutError, OSError) as e:
            # Any other SMTP/network-level failure talking to Gmail.
            logger.error(f"Failed to send OTP email to {to_email}: {e}")
            raise AppException(
                status_code=502,
                detail="Could not send the verification email right now. Please try again in a moment.",
            ) from e


email_manager = EmailManager()