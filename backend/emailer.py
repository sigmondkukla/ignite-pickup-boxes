import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import qrcode
import io


class Emailer:
    """
    Email sender for Ignite Pickup Boxes.
    Uses Clarkson internal SMTP relay: intmx.clarkson.edu
    """

    def __init__(self, email_user, smtp_host="intmx.clarkson.edu", smtp_port=25):
        self.email_user = email_user
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def _validate_recipient(self, to):
        """Ensure emails only go to Clarkson addresses."""
        if not to.lower().endswith("@clarkson.edu"):
            raise ValueError(
                f"Refusing to send email to non-clarkson address: {to}"
            )

    def _build_qr_message(self, to: str, subject: str, text_body: str, html_body: str, code: int):
        msgRoot = MIMEMultipart("related")
        msgRoot["Subject"] = subject
        msgRoot["From"] = f"Ignite Makerspace <{self.email_user}>"
        msgRoot["Sender"] = self.email_user
        msgRoot["Reply-To"] = "makerspace@clarkson.edu"
        msgRoot["To"] = to
        msgRoot.preamble = "Use this QR code to unlock your pickup box!"

        msgAlternative = MIMEMultipart("alternative")
        msgRoot.attach(msgAlternative)
        msgAlternative.attach(MIMEText(text_body, "plain"))

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data(str(code))
        qr.make(fit=True)

        qr_image = qr.make_image(
            fill_color=(255, 205, 0),
            back_color=(0, 78, 66)
        )

        qr_bytes = io.BytesIO()
        qr_image.save(qr_bytes, format="PNG")

        msgImage = MIMEImage(qr_bytes.getvalue(), _subtype="png")
        msgImage.add_header("Content-ID", "<qrcode>")
        msgImage.add_header("Content-Disposition", "inline", filename="qrcode.png")
        msgRoot.attach(msgImage)

        qr_bytes.close()

        msgAlternative.attach(MIMEText(html_body, "html"))
        return msgRoot

    def _send_message(self, to: str, message):
        smtp = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15)
        try:
            smtp.ehlo()
            smtp.sendmail(self.email_user, [to], message.as_string())
            print("Email sent to", to)
        finally:
            smtp.quit()

    def send_pickup_email(self, to: str, code: int, name: str):
        self._validate_recipient(to)

        text_body = (
            f"Hi {name},\n\n"
            "Your print is ready for pickup.\n\n"
            "Scan the QR code in this email to unlock your pickup box.\n\n"
            "If you cannot view the QR code, please ask a Maker Mentor."
        )

        html_body = f"""
        <html>
          <body>
            <p>Hi {name},</p>

            <p>Your 3D print is finished and ready for pickup.</p>

            <p>Scan this QR code to unlock your pickup box:</p>

            <p><img src="cid:qrcode" alt="Pickup QR Code"></p>

            <p>If you need help, ask a Maker Mentor.</p>

            <p>Thanks,<br>
            Ignite Makerspace Team</p>
          </body>
        </html>
        """

        msg = self._build_qr_message(
            to=to,
            subject="Your print is ready for pickup!",
            text_body=text_body,
            html_body=html_body,
            code=code,
        )
        self._send_message(to, msg)

    def send_reminder_email(self, to: str, code: int, name: str):
        self._validate_recipient(to)

        text_body = (
            f"Hi {name},\n\n"
            "This is a reminder that your print is still waiting for pickup.\n\n"
            "Please scan the QR code in this email to unlock your pickup box.\n\n"
            "If your item is not picked up soon, it may be marked as abandoned.\n\n"
            "If you need help, please ask a Maker Mentor."
        )

        html_body = f"""
        <html>
          <body>
            <p>Hi {name},</p>

            <p>This is a reminder that your 3D print is still waiting for pickup.</p>

            <p>Scan this QR code to unlock your pickup box:</p>

            <p><img src="cid:qrcode" alt="Pickup QR Code"></p>

            <p>If your item is not picked up soon, it may be marked as abandoned.</p>

            <p>If you need help, ask a Maker Mentor.</p>

            <p>Thanks,<br>
            Ignite Makerspace Team</p>
          </body>
        </html>
        """

        msg = self._build_qr_message(
            to=to,
            subject="Reminder: your print is still waiting for pickup",
            text_body=text_body,
            html_body=html_body,
            code=code,
        )
        self._send_message(to, msg)


if __name__ == "__main__":
    import os
    import sys
    from dotenv import load_dotenv

    load_dotenv()

    if len(sys.argv) != 4:
        print('Usage: python3 emailer.py <recipient@clarkson.edu> <pickup_code> "<name>"')
        sys.exit(1)

    recipient = sys.argv[1]
    pickup_code = int(sys.argv[2])
    recipient_name = sys.argv[3]

    emailer = Emailer(
        email_user=os.getenv("EMAIL_USER", "makerspace-pickup@clarkson.edu"),
        smtp_host=os.getenv("SMTP_HOST", "intmx.clarkson.edu"),
        smtp_port=int(os.getenv("SMTP_PORT", "25")),
    )

    emailer.send_pickup_email(recipient, pickup_code, recipient_name)
