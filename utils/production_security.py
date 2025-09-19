"""
Production Security Enhancements for School Management System
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
import streamlit as st

class ProductionSecurity:
    """Enhanced security for production deployment"""
    
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT", 3600))  # 1 hour
    
    def hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash password with salt"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, hash_str: str, salt: str) -> bool:
        """Verify password against hash"""
        test_hash, _ = self.hash_password(password, salt)
        return test_hash == hash_str
    
    def check_session_timeout(self) -> bool:
        """Check if user session has timed out"""
        if "last_activity" in st.session_state:
            last_activity = st.session_state["last_activity"]
            if datetime.now() - last_activity > timedelta(seconds=self.session_timeout):
                # Session expired
                st.session_state.clear()
                return True
        
        # Update last activity
        st.session_state["last_activity"] = datetime.now()
        return False
    
    def get_client_ip(self) -> str:
        """Get client IP address (for logging)"""
        # This works with most cloud platforms
        return st.experimental_get_query_params().get("client_ip", ["unknown"])[0]
    
    def log_security_event(self, event_type: str, user_id: str = None, details: str = None):
        """Log security events for monitoring"""
        timestamp = datetime.now().isoformat()
        client_ip = self.get_client_ip()
        
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user_id": user_id,
            "client_ip": client_ip,
            "details": details
        }
        
        # In production, send to logging service
        print(f"SECURITY_LOG: {log_entry}")

# Initialize security
security = ProductionSecurity()