import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class Emailer:
    def __init__(self, email_user, email_password) -> None:
        self.email_user = email_user
        self.email_password = email_password

    def send_pickup_email(self, to: str, print_number):
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

        # HTML part
        msgText = MIMEText('Hi Maker!<br><br>Thank you for submitting a 3D print to the Makerspace. The print you submitted has finished printing, and can now be picked up from the boxes outside the Makerspace.<br><br>Use this QR code to unlock your box:<br><img src="cid:qrcode">', 'html')
        msgAlternative.attach(msgText)

        # This example assumes the image is in the current directory
        fp = open('test.jpg', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID as referenced above and attach it
        msgImage.add_header('Content-ID', '<qrcode>')
        msgRoot.attach(msgImage)

        # Make a connection, send the email, then close the connection
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(self.email_user, self.email_password)
        smtp.sendmail(self.email_user, to, msgRoot.as_string())
        smtp.quit()