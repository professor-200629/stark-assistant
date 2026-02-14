# Configuration file for Stark Assistant
# Application Settings
APP_NAME = "Stark Assistant"
APP_VERSION = "1.0.0"
DEBUG_MODE = True

# User Settings
DEFAULT_USER_ID = "user_001"
TIMEZONE = "UTC"

# Task Manager Settings
MAX_TASKS_PER_USER = 1000
TASK_REMINDER_LEAD_TIME = 3600

# Communication Settings
MAX_MESSAGES_PER_USER = 10000
MESSAGE_RETENTION_DAYS = 30
NOTIFICATION_TYPES = ["text", "notification", "reminder", "alert"]

# Memory Settings
MEMORY_CATEGORIES = ["preferences", "conversation", "learned", "personal"]
MAX_MEMORY_ITEMS_PER_CATEGORY = 5000
MEMORY_AUTO_CLEANUP_DAYS = 90

# API Settings
API_HOST = "127.0.0.1"
API_PORT = 5000
API_DEBUG = True
API_ALLOW_CORS = True

# Database Settings
DATABASE_TYPE = "sqlite"
DATABASE_NAME = "stark_assistant.db"
DATABASE_HOST = "localhost"
DATABASE_PORT = 5432

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FILE = "stark_assistant.log"
LOG_MAX_SIZE = 10485760
LOG_BACKUP_COUNT = 5

# Security Settings
ENABLE_AUTHENTICATION = True
SESSION_TIMEOUT = 3600
PASSWORD_MIN_LENGTH = 8

# UI Settings
UI_THEME = "dark"
UI_LANGUAGE = "en"
UI_AUTO_REFRESH_INTERVAL = 5000

# Response Format
POLITENESS_LEVEL = "high"
RESPONSE_FORMAT = "text"
INCLUDE_TIMESTAMP = True

# Feature Flags
ENABLE_VOICE_COMMANDS = False
ENABLE_NOTIFICATIONS = True
ENABLE_LEARNING = True
ENABLE_ANALYTICS = True