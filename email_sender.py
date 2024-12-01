import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


sender_email = "finderbotweb@gmail.com"
receiver_email = "frickkun@gmail.com"
password = "wgvy smou iens bkup"


subject = "FinderBot Alert"
body = "Your missing person was detected."  # add time, date

message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
