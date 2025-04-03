import re
from typing import List, Dict
from datetime import datetime

class SpamFilter:
    def __init__(self):
        self.spam_keywords = [
            # Common spam keywords
            'viagra', 'lottery', 'winner', 'inheritance', 'prince',
            'urgent', 'account suspended', 'verify account', 'unusual activity',
            'congratulations', 'claim prize', 'million dollars', 'bank transfer',
            'bitcoin', 'crypto', 'investment opportunity', 'urgent action required',
            'account compromised', 'security alert', 'verify your identity',
            'unclaimed funds', 'inheritance money', 'lottery prize', 'claim now',
            'limited time offer', 'exclusive offer', 'special promotion',
            'account verification', 'password expired', 'account locked',
            'unusual login attempt', 'suspicious activity', 'verify your account',
            'confirm your identity', 'account security', 'unusual sign-in',
            'verify your email', 'confirm your email', 'account access',
            'unusual activity detected', 'account status', 'verify your details'
        ]
        
        self.spam_patterns = [
            r'\b[A-Z]{2,}\b',  # Excessive capitalization
            r'\b\d{6,}\b',     # Long numbers
            r'[!]{2,}',        # Multiple exclamation marks
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',  # Email addresses
            r'\b(?:USD|EUR|GBP|BTC|ETH)\s*\d+[.,]\d{2}',  # Currency amounts
            r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:million|billion|trillion)\b',  # Large numbers
            r'https?://(?:www\.)?(?:bit\.ly|goo\.gl|tinyurl\.com)/\w+',  # Short URLs
            r'\b(?:urgent|important|action required|verify|confirm|security|alert)\b',  # Urgency words
            r'\b(?:winner|prize|lottery|inheritance|unclaimed|funds)\b',  # Prize words
            r'\b(?:account|password|security|verify|confirm)\b',  # Account-related words
        ]
    
    def check_spam(self, subject: str, body: str) -> bool:
        """
        Check if an email is spam based on subject and body content
        Returns True if spam, False otherwise
        """
        # Convert to lowercase for case-insensitive matching
        subject_lower = subject.lower()
        body_lower = body.lower()
        
        # Check for spam keywords
        for keyword in self.spam_keywords:
            if keyword in subject_lower or keyword in body_lower:
                return True
        
        # Check for spam patterns
        for pattern in self.spam_patterns:
            if re.search(pattern, subject) or re.search(pattern, body):
                return True
        
        # Check for suspicious characteristics
        if self._has_suspicious_characteristics(subject, body):
            return True
        
        return False
    
    def _has_suspicious_characteristics(self, subject: str, body: str) -> bool:
        """Check for suspicious characteristics in the email"""
        # Check for excessive punctuation
        if subject.count('!') > 2 or body.count('!') > 5:
            return True
        
        # Check for excessive capitalization
        if sum(1 for c in subject if c.isupper()) > len(subject) * 0.7:
            return True
        
        # Check for excessive numbers
        if len(re.findall(r'\d+', subject)) > 3 or len(re.findall(r'\d+', body)) > 5:
            return True
        
        # Check for multiple email addresses
        if len(re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', body)) > 3:
            return True
        
        # Check for multiple currency symbols
        if len(re.findall(r'[$€£]', subject + body)) > 2:
            return True
        
        # Check for multiple URLs
        if len(re.findall(r'https?://\S+', body)) > 3:
            return True
        
        # Check for excessive special characters
        if len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', subject)) > 5:
            return True
        
        return False
    
    def update_spam_keywords(self, new_keywords: List[str]):
        """Update the list of spam keywords"""
        self.spam_keywords.extend(new_keywords)
    
    def update_spam_patterns(self, new_patterns: List[str]):
        """Update the list of spam patterns"""
        self.spam_patterns.extend(new_patterns)

    def generate_test_spam(self) -> Dict[str, str]:
        """Generate a sample spam email for testing"""
        return {
            'subject': 'URGENT: Your Account Security Alert! 🔒',
            'body': '''
IMPORTANT NOTICE: Your account has been compromised!

Dear valued customer,

We have detected UNUSUAL ACTIVITY on your account. Your account will be SUSPENDED unless you verify your identity immediately.

CLICK HERE to verify your account: https://bit.ly/verify-now

This is a LIMITED TIME OFFER to secure your account. We have detected multiple failed login attempts from:
- IP: 192.168.1.1
- Location: Unknown
- Time: 2024-03-20 15:30:00

To prevent account suspension, please verify your details NOW!

Best regards,
Security Team
'''
        } 