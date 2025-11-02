"""
Invitation-based signup service
Sends email to admin for approval
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local', override=True)

ADMIN_EMAIL = "shivganga25shingatwar@gmail.com"

class InvitationService:
    """Manage invitation-based signups"""
    
    def __init__(self):
        self.admin_email = ADMIN_EMAIL
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
    
    def send_signup_notification(self, email: str, name: Optional[str] = None):
        """Send email to admin when someone tries to sign up"""
        
        subject = f"🔔 New Signup Request: {email}"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #20B2AA;">New Signup Request</h2>
            
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Name:</strong> {name or 'Not provided'}</p>
                <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <h3>Action Required:</h3>
            <p>To approve this user:</p>
            <ol>
                <li>Go to <a href="https://console.firebase.google.com/project/productivityai-mvp/authentication/users">Firebase Console</a></li>
                <li>Find user: {email}</li>
                <li>Enable/Disable as needed</li>
            </ol>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This is an automated notification from AI Productivity App
            </p>
        </body>
        </html>
        """
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_user or "noreply@aiproductivity.app"
            msg['To'] = self.admin_email
            
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Send email
            if self.smtp_user and self.smtp_password:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                
                print(f"✅ Signup notification sent to {self.admin_email}")
            else:
                print(f"⚠️  SMTP not configured. Would send email to: {self.admin_email}")
                print(f"   Subject: {subject}")
                print(f"   User: {email}")
        
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            # Don't fail signup if email fails
            pass


# Singleton
_invitation_service = None

def get_invitation_service() -> InvitationService:
    global _invitation_service
    if _invitation_service is None:
        _invitation_service = InvitationService()
    return _invitation_service

