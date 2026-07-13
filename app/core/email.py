# app/core/email.py
"""
Sends transactional emails (currently just OTP codes) via Brevo's
transactional email HTTP API (https://api.brevo.com/v3/smtp/email).

We deliberately do NOT use raw SMTP here. Render's free tier blocks all
outbound traffic on SMTP ports (25, 465, 587) as of Sept 2025, so a plain
smtplib connection to any mail server (Gmail included) will hang and then
time out, no matter how correct the credentials are. Brevo's API runs over
plain HTTPS (port 443), which Render cannot block without breaking the
app's own ability to serve web traffic -- so this works reliably in
production.

Setup (one-time):
    1. Create a free account at https://www.brevo.com (300 emails/day free,
       no credit card required).
    2. Settings -> Senders, Domains, IPs -> Senders -> Add a sender.
       Use any email address you own (a plain Gmail address is fine) and
       verify it via the confirmation email/code Brevo sends you. No
       custom domain is required.
    3. Account menu -> SMTP & API -> API Keys -> Generate a new API key.
    4. Set these environment variables (locally in .env, and on Render's
       dashboard for the deployed service):
           BREVO_API_KEY=xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
           BREVO_SENDER_EMAIL=the-address-you-verified@gmail.com
           BREVO_SENDER_NAME=Road Damage AI

If BREVO_API_KEY / BREVO_SENDER_EMAIL are left blank (e.g. local dev with
no email setup done yet), the OTP is logged to the console instead of
emailed, so registration still works without any mail setup.
"""
import requests

from app.core.config import settings
from app.core.logging import logger
from app.exceptions.custom import AppException

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


class EmailManager:
    @staticmethod
    def _build_otp_bodies(to_email: str, otp_code: str) -> tuple[str, str]:
        from_name = settings.BREVO_SENDER_NAME

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
        return text_body, html_body

    @staticmethod
    def send_otp_email(to_email: str, otp_code: str) -> None:
        # Local/dev fallback: no Brevo credentials configured -> just log
        # it, so local testing never gets blocked on real email.
        if not settings.BREVO_API_KEY or not settings.BREVO_SENDER_EMAIL:
            logger.warning(
                f"[DEV MODE - no Brevo credentials set] OTP for {to_email}: {otp_code}"
            )
            return

        text_body, html_body = EmailManager._build_otp_bodies(to_email, otp_code)

        payload = {
            "sender": {
                "name": settings.BREVO_SENDER_NAME,
                "email": settings.BREVO_SENDER_EMAIL,
            },
            "to": [{"email": to_email}],
            "subject": f"{otp_code} is your {settings.BREVO_SENDER_NAME} verification code",
            "htmlContent": html_body,
            "textContent": text_body,
        }
        headers = {
            "api-key": settings.BREVO_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=15)
        except requests.RequestException as e:
            # DNS failure, connection refused, timeout, etc.
            logger.error(f"Brevo API request failed sending to {to_email}: {e}")
            raise AppException(
                status_code=502,
                detail="Could not send the verification email right now. Please try again in a moment.",
            ) from e

        if response.status_code >= 400:
            logger.error(
                f"Brevo API rejected OTP email to {to_email}: "
                f"{response.status_code} {response.text}"
            )
            if response.status_code in (401, 403):
                raise AppException(
                    status_code=502,
                    detail="Email service is misconfigured (invalid Brevo API key or unverified sender). Please contact support.",
                )
            raise AppException(
                status_code=502,
                detail="Could not send the verification email right now. Please try again in a moment.",
            )

        logger.info(f"OTP email dispatched to {to_email} via Brevo")


email_manager = EmailManager()
