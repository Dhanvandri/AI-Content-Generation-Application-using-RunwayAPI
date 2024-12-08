import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

DB_PATH = r"/home/devil/Documents/python/flaskproject/app/database/content.db"
SMTP_SERVER = "smtp.gmail.com"  
SMTP_PORT = 587
SENDER_EMAIL = "user77516@gmail.com"  
SENDER_PASSWORD = "52p5kvbx"  

def send_email_notification(to_email, user_id, content_link):
    """
    Sends an email notification to the user with the generated content link.
    """
    subject = "Your Generated Content is Ready!"
    body = f"""
    Hi {user_id},

    Your requested content has been successfully generated. 
    Click the link below to view your content:

    {content_link}

    Thank you for using our service!

    Best regards,
    Content Generator Team
    """

    # Setup the email message
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, message.as_string())
            print(f"Email sent successfully to {to_email} for user {user_id}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")

def notify_users():
    """
    Fetches users with completed content from the database and sends notifications.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id, status FROM content_generation WHERE status = 'Completed'")
            completed_users = cur.fetchall()

            for user in completed_users:
                user_id = user[0]
                user_email = f"{user_id}@example.com"  # modify this to users email
                content_link = f"http://127.0.0.1:5000/gallery/{user_id}"  # Link to user's gallery
                send_email_notification(user_email, user_id, content_link)

                print(f"Notification sent for user: {user_id}")

    except sqlite3.Error as e:
        print(f"Database error while notifying users: {e}")

if __name__ == "__main__":
    notify_users()
