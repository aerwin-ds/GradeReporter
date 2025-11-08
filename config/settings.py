"""
Centralized configuration management for GradeReporter.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.parent

# Database Configuration
DB_PATH = os.getenv('DB_PATH', 'data/school_system.db')
AFTER_HOURS_DB_PATH = os.getenv('AFTER_HOURS_DB_PATH', 'data/after_hours.db')

# Convert to absolute paths
DB_PATH = ROOT_DIR / DB_PATH
AFTER_HOURS_DB_PATH = ROOT_DIR / AFTER_HOURS_DB_PATH

# Application Settings
APP_NAME = os.getenv('APP_NAME', 'GradeReporter')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Session Configuration
SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))

# Timezone Settings
DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'UTC')

# Feature Flags
FEATURES = {
    'authentication': os.getenv('FEATURE_AUTHENTICATION', 'True').lower() == 'true',
    'announcements': os.getenv('FEATURE_ANNOUNCEMENTS', 'True').lower() == 'true',
    'parent_engagement': os.getenv('FEATURE_PARENT_ENGAGEMENT', 'True').lower() == 'true',
    'after_hours': os.getenv('FEATURE_AFTER_HOURS', 'True').lower() == 'true',
    'feature_5': os.getenv('FEATURE_5', 'False').lower() == 'true',
    'feature_6': os.getenv('FEATURE_6', 'False').lower() == 'true',
    'feature_7': os.getenv('FEATURE_7', 'False').lower() == 'true',
    'feature_8': os.getenv('FEATURE_8', 'False').lower() == 'true',
}

# User Roles
ROLES = {
    'STUDENT': 'student',
    'PARENT': 'parent',
    'TEACHER': 'teacher',
    'ADMIN': 'admin',
}

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled."""
    return FEATURES.get(feature_name, False)
