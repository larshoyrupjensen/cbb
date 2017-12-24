# Sends email message through Googles smtp.gmail.com using Lars' account
# Note that an App Password is used

import smtplib
from email.mime.text import MIMEText

html_table = '<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n      <th></th>\n      <th>brand</th>\n      <th>model</th>\n      <th>price</th>\n      <th>storage</th>\n      <th>timestamp</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th>0</th>\n      <td>Huawei</td>\n      <td>P10 Lite</td>\n      <td>799</td>\n      <td>32 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n    <tr>\n      <th>1</th>\n      <td>Huawei</td>\n      <td>P8 Lite</td>\n      <td>999</td>\n      <td>16 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n    <tr>\n      <th>2</th>\n      <td>Huawei</td>\n      <td>P9 Lite</td>\n      <td>1499</td>\n      <td>16 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n    <tr>\n      <th>3</th>\n      <td>Nokia</td>\n      <td>8</td>\n      <td>3299</td>\n      <td>64 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n    <tr>\n      <th>4</th>\n      <td>Samsung</td>\n      <td>Galaxy S7</td>\n      <td>3699</td>\n      <td>32 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n    <tr>\n      <th>5</th>\n      <td>Samsung</td>\n      <td>Galaxy S7 Edge</td>\n      <td>4499</td>\n      <td>32 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n    <tr>\n      <th>6</th>\n      <td>Samsung</td>\n      <td>Galaxy S8+</td>\n      <td>5599</td>\n      <td>64 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n    <tr>\n      <th>7</th>\n      <td>Sony</td>\n      <td>Xperia XA</td>\n      <td>1896</td>\n      <td>16 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n    <tr>\n      <th>8</th>\n      <td>Sony</td>\n      <td>Xperia XZ1</td>\n      <td>4499</td>\n      <td>64 GB</td>\n      <td>2019-11-18 08:41:02</td>\n    </tr>\n  </tbody>\n</table>'

SERVER="smtp.gmail.com"
PORT=587
USER="lars.hoyrup.jensen@gmail.com"
APP_PASSWORD="ibeayijtefhvjqzj"


def send_email(recipient=None, subject=None, content=None):
    msg = MIMEText(content, 'html')
    #msg = EmailMessage()
    #msg.add_header('Content-Type','text/html')
    #msg.set_content(content)
    msg["Subject"]=subject
    msg["From"]=USER
    msg["To"]=recipient
    server = smtplib.SMTP(host=SERVER, port=587)
    server.starttls()
    server.login(USER, APP_PASSWORD)
    server.send_message(msg)
    server.quit()
    
if __name__=="__main__":
    #msg="This is a test message"
    msg=html_table
    print("Sending test message [{0}] to {1}".format(msg, USER))
    send_email(recipient=USER, content=msg, subject="Test subject")