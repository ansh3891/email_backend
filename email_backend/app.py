from flask import Flask, request, jsonify
from flask_cors import CORS
from services.email_service import EmailService
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize email service
email_service = EmailService()

def ensure_authenticated():
    """Ensure the email service is authenticated before processing requests."""
    try:
        if not email_service.is_authenticated():
            logger.info("Re-authenticating email service...")
            if not email_service.authenticate():
                raise Exception("Failed to authenticate with Gmail")
            logger.info("Email service re-authenticated successfully")
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        ensure_authenticated()
        data = request.get_json()
        logger.info(f"Received send email request: {data}")
        
        result = email_service.send_email(
            to=data['to'],
            subject=data['subject'],
            body=data['body']
        )
        logger.info(f"Send email result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to send email: {str(e)}'
        }), 500

@app.route('/api/emails/inbox', methods=['GET'])
def receive_emails():
    try:
        ensure_authenticated()
        logger.info("Received receive emails request")
        
        result = email_service.receive_emails()
        logger.info(f"Receive emails result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error receiving emails: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to receive emails: {str(e)}',
            'emails': []
        }), 500

@app.route('/api/emails/sent', methods=['GET'])
def get_sent_emails():
    try:
        ensure_authenticated()
        logger.info("Received get sent emails request")
        
        result = email_service.get_sent_emails()
        logger.info(f"Get sent emails result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting sent emails: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to get sent emails: {str(e)}',
            'emails': []
        }), 500

@app.route('/api/emails/spam', methods=['GET'])
def get_spam_emails():
    try:
        ensure_authenticated()
        logger.info("Received get spam emails request")
        
        result = email_service.get_spam_emails()
        logger.info(f"Get spam emails result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting spam emails: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to get spam emails: {str(e)}',
            'emails': []
        }), 500

@app.route('/api/emails/<message_id>', methods=['DELETE'])
def delete_email(message_id):
    try:
        ensure_authenticated()
        logger.info(f"Received delete email request for message ID: {message_id}")
        
        result = email_service.delete_email(message_id)
        logger.info(f"Delete email result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error deleting email: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to delete email: {str(e)}'
        }), 500

@app.route('/api/test-spam', methods=['POST'])
def test_spam():
    try:
        ensure_authenticated()
        data = request.get_json()
        logger.info(f"Received test spam request: {data}")
        
        result = email_service.test_spam(data['email'])
        logger.info(f"Test spam result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error testing spam: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to test spam: {str(e)}'
        }), 500

@app.route('/api/emails/all', methods=['GET'])
def get_all_emails():
    """Get all emails."""
    try:
        ensure_authenticated()
        result = email_service.get_all_emails()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/emails/starred', methods=['GET'])
def get_starred_emails():
    """Get starred emails."""
    try:
        ensure_authenticated()
        result = email_service.get_starred_emails()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/emails/<message_id>/star', methods=['POST'])
def toggle_star(message_id):
    """Toggle star status of an email."""
    try:
        ensure_authenticated()
        starred = request.json.get('starred', True)
        result = email_service.toggle_star(message_id, starred)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def initialize_app():
    """Initialize the application and force authentication."""
    try:
        logger.info("Starting application initialization")
        
        # Ensure credentials file exists
        if not os.path.exists('credentials.json'):
            logger.error("credentials.json not found. Please ensure it exists in the email_backend directory.")
            return False
        
        # Force authentication
        logger.info("Forcing initial authentication")
        if not email_service.authenticate():
            logger.error("Failed to authenticate with Gmail")
            return False
        
        logger.info("Application initialization successful")
        return True
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        return False

if __name__ == '__main__':
    # Initialize the application
    if not initialize_app():
        logger.error("Failed to initialize application. Exiting...")
        exit(1)
    
    # Get port from environment variable for Render
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False) 