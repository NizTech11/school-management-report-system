import streamlit as st
import yaml
from pathlib import Path
import streamlit_authenticator as stauth
import bcrypt

CONFIG_PATH = Path('.streamlit/auth.yaml')

def _hash_password(plain: str) -> str:
    # bcrypt returns bytes; decode to utf-8 for YAML
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

_default_config = {
    'credentials': {
        'usernames': {
            'teacher1': {
                'name': 'Teacher One',
                'password': _hash_password('teacher123')
            }
        }
    },
    'cookie': {
        'name': 'student-report-auth',
        'key': 'supersecret',
        'expiry_days': 30
    },
    'preauthorized': {
        'emails': []
    }
}

def load_auth_config() -> dict:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'w') as f:
            yaml.safe_dump(_default_config, f)
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def login():
    config = load_auth_config()
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    name, auth_status, username = authenticator.login(
        fields={'Form name': 'Login'},
        location='main'
    )
    if auth_status:
        st.session_state['user'] = {'name': name, 'username': username}
        authenticator.logout('Logout', 'sidebar')
        return True
    elif auth_status is False:
        st.error('Username/password is incorrect')
    return False
