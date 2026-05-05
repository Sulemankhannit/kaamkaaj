import smtplib
import ssl
from email.message import EmailMessage
from core.config import smtp_email, smtp_password

def send_otp_email(receiver_email: str, otp_code: str):
    """
    Sends a beautifully formatted OTP email via Gmail's SMTP server.
    This function is synchronous, so we will pass it to FastAPI's BackgroundTasks.
    """
    subject = "Your KaamKaaj Verification Code"
    body = f"""
    Hello Khiladi,
    
    Your verification code is: {otp_code}
    
    This code will expire in 10 minutes. If you did not request this, please ignore this email.
    
    Prepare for Tapasya,
    The KaamKaaj Engine
    """

    # 1. Construct the Email Object
    em = EmailMessage()
    em['From'] = smtp_email
    em['To'] = receiver_email
    em['Subject'] = subject
    em.set_content(body)

    # 2. Establish a Secure SSL Context
    context = ssl.create_default_context()

    # 3. Connect, Login, and Send (Port 465 is the secure SSL port for Gmail)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(smtp_email, smtp_password)
            smtp.sendmail(smtp_email, receiver_email, em.as_string())
            print(f" OTP Email successfully sent to {receiver_email}")
    except Exception as e:
        print(f" Failed to send email: {e}")


    