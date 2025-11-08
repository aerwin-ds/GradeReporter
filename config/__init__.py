"""Configuration module for GradeReporter."""
from config.settings import *
from config.database import db_manager

__all__ = ['db_manager', 'settings', 'database']
