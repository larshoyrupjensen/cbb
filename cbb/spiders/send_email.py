# Sends email message through Google's smtp.gmail.com using Lars' account
# Note that an App Password is used

import smtplib
from email.mime.text import MIMEText

SERVER="smtp.gmail.com"
PORT=587
USER="lars.hoyrup.jensen@gmail.com"
APP_PASSWORD="ibeayijtefhvjqzj"


def send_email(recipient=None, subject=None, content=None):
    msg = MIMEText(content, 'html')
    msg["Subject"]=subject
    msg["From"]=USER
    msg["To"]=recipient
    server = smtplib.SMTP(host=SERVER, port=587)
    server.starttls()
    server.login(USER, APP_PASSWORD)
    server.send_message(msg)
    server.quit()
    
if __name__=="__main__":
    msg="This is a test message"
    print("Sending test message [{0}] to {1}".format(msg, USER))
    send_email(recipient=USER, content=msg, subject="Test subject")