import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import qrcode
import io

class Emailer:
    def __init__(self, email_user, email_password) -> None:
        self.email_user = email_user
        self.email_password = email_password

    def send_pickup_email(self, to: str, code: int) -> None:
        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = 'Your print is ready for pickup!'
        msgRoot['From'] = self.email_user
        msgRoot['To'] = to
        msgRoot.preamble = 'Use this QR code to unlock your pickup box!'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        # Plain text part
        msgText = MIMEText('This email client does not support HTML emails. Please ask a Maker Mentor to unlock your box for you.', 'plain')
        msgAlternative.attach(msgText)

        # Generate QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(str(code))
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color=(255,205,0), back_color=(0,78,66))
        qr_bytes = io.BytesIO()
        qr_image.save(qr_bytes, format='PNG')

        # Attach the QR code image
        msgImage = MIMEImage(qr_bytes.getvalue())
        msgImage.add_header('Content-ID', '<qrcode>')
        msgRoot.attach(msgImage)

        qr_bytes.close()

        # HTML part
        msgText = MIMEText(f'<p>Hi Maker!</p><p>Thank you for submitting a 3D print to the Makerspace. The print you submitted has finished printing, and can now be picked up from the boxes outside the Makerspace.</p><p>Use this QR code to unlock your box:<br><img src="cid:qrcode"><br>Need help retrieving your print? Ask a Maker Mentor for assistance!</p><p>Thanks,<br>The Makerspace Team</p><p><a href="https://linktr.ee/ignite_dorf_makerspace">Learn more about the Makerspace!</a><br>Open hours: Sun-Thu 1-6PM</p>', 'html')
        msgAlternative.attach(msgText)

        # Make a connection, send the email, then close the connection
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(self.email_user, self.email_password)
        smtp.sendmail(self.email_user, to, msgRoot.as_string())
        smtp.quit()

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    emailer = Emailer(email_user=os.getenv("EMAIL_USER"), email_password=os.getenv("EMAIL_PASSWORD"))
    emailer.send_pickup_email("kuklasj@clarkson.edu", 333333)