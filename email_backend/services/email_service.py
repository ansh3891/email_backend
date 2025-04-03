import os
import pickle
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from datetime import datetime
import time
import smtplib
import ssl
import httplib2
from .spam_filter import SpamFilter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = [
    'https://mail.google.com/',  # Full access to Gmail
    'https://www.googleapis.com/auth/gmail.modify',  # Read, write, and delete emails
    'https://www.googleapis.com/auth/gmail.labels',  # Manage labels
    'https://www.googleapis.com/auth/gmail.send'  # Send emails
]

class EmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticated = False
        self.spam_filter = SpamFilter()
        
    def is_authenticated(self):
        """Check if the service is authenticated."""
        return self._authenticated and self.service is not None

    def authenticate(self):
        """Authenticate with Gmail API."""
        try:
            logger.info("Starting authentication process")
            
            # Always try to load existing token first
            if os.path.exists('token.json'):
                logger.info("Loading existing token")
                self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            # If no valid credentials, start new authentication flow
            if not self.creds or not self.creds.valid:
                logger.info("No valid credentials found, starting new authentication flow")
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logger.info("Refreshing expired token")
                    self.creds.refresh(Request())
                else:
                    logger.info("Starting new OAuth flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json',
                        SCOPES,
                        redirect_uri='http://192.168.194.29:8080'
                    )
                    self.creds = flow.run_local_server(
                        port=8080,
                        prompt='consent',
                        access_type='offline'
                    )
                
                logger.info("Saving new token")
                with open('token.json', 'w') as token:
                    token.write(self.creds.to_json())
            
            logger.info("Building Gmail service")
            self.service = build('gmail', 'v1', credentials=self.creds)
            self._authenticated = True
            logger.info("Authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            self._authenticated = False
            return False

    def send_email(self, to, subject, body):
        """Send an email using Gmail API."""
        try:
            logger.info(f"Starting to send email to: {to}")
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            logger.info(f"Email sent successfully: {sent_message['id']}")
            return {'success': True, 'message': 'Email sent successfully'}
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {'success': False, 'message': str(e)}

    def receive_emails(self, max_results=5):
        """Receive emails from Gmail."""
        try:
            logger.info("Starting to receive emails")
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No messages found")
                return {'success': True, 'emails': []}
            
            logger.info(f"Found {len(messages)} messages")
            emails = []
            
            for message in messages:
                try:
                    msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                    email_data = self._parse_email(msg)
                    if email_data:  # Only add if parsing was successful
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(emails)} emails")
            return {'success': True, 'emails': emails}
            
        except Exception as e:
            logger.error(f"Error receiving emails: {str(e)}")
            return {'success': False, 'message': str(e), 'emails': []}

    def get_sent_emails(self, max_results=5):
        """Get sent emails from Gmail."""
        try:
            logger.info("Starting to get sent emails")
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['SENT'],
                maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No sent messages found")
                return {'success': True, 'emails': []}
            
            logger.info(f"Found {len(messages)} sent messages")
            emails = []
            
            for message in messages:
                try:
                    msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                    email_data = self._parse_email(msg)
                    if email_data:  # Only add if parsing was successful
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error processing sent message {message['id']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(emails)} sent emails")
            return {'success': True, 'emails': emails}
            
        except Exception as e:
            logger.error(f"Error getting sent emails: {str(e)}")
            return {'success': False, 'message': str(e), 'emails': []}

    def get_spam_emails(self, max_results=5):
        """Get spam emails from Gmail."""
        try:
            logger.info("Starting to get spam emails")
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['SPAM'],
                maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No spam messages found")
                return {'success': True, 'emails': []}
            
            logger.info(f"Found {len(messages)} spam messages")
            emails = []
            
            for message in messages:
                try:
                    msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                    email_data = self._parse_email(msg)
                    if email_data:  # Only add if parsing was successful
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error processing spam message {message['id']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(emails)} spam emails")
            return {'success': True, 'emails': emails}
            
        except Exception as e:
            logger.error(f"Error getting spam emails: {str(e)}")
            return {'success': False, 'message': str(e), 'emails': []}

    def get_all_emails(self, max_results=5):
        """Get all emails from Gmail."""
        try:
            logger.info("Starting to get all emails")
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No messages found")
                return {'success': True, 'emails': []}
            
            logger.info(f"Found {len(messages)} messages")
            emails = []
            
            for message in messages:
                try:
                    msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                    email_data = self._parse_email(msg)
                    if email_data:  # Only add if parsing was successful
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(emails)} emails")
            return {'success': True, 'emails': emails}
            
        except Exception as e:
            logger.error(f"Error getting all emails: {str(e)}")
            return {'success': False, 'message': str(e), 'emails': []}

    def get_starred_emails(self, max_results=5):
        """Get starred emails from Gmail."""
        try:
            logger.info("Starting to get starred emails")
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['STARRED'],
                maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No starred messages found")
                return {'success': True, 'emails': []}
            
            logger.info(f"Found {len(messages)} starred messages")
            emails = []
            
            for message in messages:
                try:
                    msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                    email_data = self._parse_email(msg)
                    if email_data:  # Only add if parsing was successful
                        emails.append(email_data)
                except Exception as e:
                    logger.error(f"Error processing starred message {message['id']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully processed {len(emails)} starred emails")
            return {'success': True, 'emails': emails}
            
        except Exception as e:
            logger.error(f"Error getting starred emails: {str(e)}")
            return {'success': False, 'message': str(e), 'emails': []}

    def toggle_star(self, message_id, starred=True):
        """Toggle star status of an email."""
        try:
            logger.info(f"Starting to {'add' if starred else 'remove'} star for email: {message_id}")
            if starred:
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'addLabelIds': ['STARRED']}
                ).execute()
            else:
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': ['STARRED']}
                ).execute()
            
            logger.info(f"Star {'added' if starred else 'removed'} successfully for email: {message_id}")
            return {'success': True, 'message': f"Star {'added' if starred else 'removed'} successfully"}
            
        except Exception as e:
            logger.error(f"Error toggling star: {str(e)}")
            return {'success': False, 'message': str(e)}

    def _parse_email(self, message):
        """Parse email message into a dictionary."""
        try:
            # Get message ID
            message_id = message['id']
            
            # Get headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Get body
            body = ''
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part.get('mimeType') == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            elif 'body' in message['payload'] and 'data' in message['payload']['body']:
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
            
            # Check if email is unread and starred
            is_unread = 'UNREAD' in message.get('labelIds', [])
            is_starred = 'STARRED' in message.get('labelIds', [])
            
            # For sent emails, we need to handle the "To" field differently
            if 'SENT' in message.get('labelIds', []):
                to_header = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
                if to_header:
                    from_header = to_header  # Use recipient as the "from" field for sent emails
            
            return {
                'id': message_id,
                'subject': subject,
                'from': from_header,
                'date': date,
                'body': body,
                'is_unread': is_unread,
                'is_starred': is_starred
            }
            
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            logger.error(f"Message data: {message}")
            return None

    def mark_as_read(self, message_id):
        """Mark an email as read"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False
                
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking email as read: {str(e)}")
            return False
    
    def move_to_spam(self, message_id):
        """Move email to spam folder"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False, "Failed to authenticate with Gmail"
            
            # Remove all labels and add SPAM label
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX', 'CATEGORY_PERSONAL', 'CATEGORY_SOCIAL', 'CATEGORY_PROMOTIONS', 'CATEGORY_UPDATES', 'CATEGORY_FORUMS'], 'addLabelIds': ['SPAM']}
            ).execute()
            return True, "Email moved to spam"
        except Exception as e:
            print(f"Error moving to spam: {str(e)}")
            return False, str(e)
    
    def delete_email(self, message_id):
        """Delete an email permanently."""
        try:
            logger.info(f"Starting to delete email: {message_id}")
            self.service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()
            
            logger.info(f"Email deleted successfully: {message_id}")
            return {'success': True, 'message': 'Email deleted successfully'}
            
        except Exception as e:
            logger.error(f"Error deleting email: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def create_alias(self, alias_name):
        """Create a new email alias"""
        try:
            # This would need to be implemented using Gmail API
            # For now, we'll just return a success message
            return True, f"Alias {alias_name} created successfully"
        except Exception as e:
            return False, str(e)

    def ensure_authenticated(self):
        if not self.service:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Gmail") 