import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


class Emailer:
    def __init__(self, email_user, email_password) -> None:
        self.email_user = email_user
        self.email_password = email_password
        

strTo = 'to@example.com'

def send_pickup_email():

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Your print is ready for pickup!'
    msgRoot['From'] = email_from
    msgRoot['To'] = strTo
    msgRoot.preamble = 'Collect your print from the pickup boxes outside the makerspace.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>Nifty!', 'html')
    msgAlternative.attach(msgText)

    # This example assumes the image is in the current directory
    fp = open('test.jpg', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    smtp.starttls()
    # Authentication
    smtp.login("***REMOVED***", "***REMOVED***")
    # message to be sent
    message = "Test email"
    # sending the mail
    smtp.sendmail("***REMOVED***", "kuklasj@clarkson.edu", message)
    # terminating the session
    smtp.quit()