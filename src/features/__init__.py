# features/__init__.py - Features package initialization
"""
Features Package - Các chức năng chính của Lappy Lab
"""

# Import các tính năng Cursor chính
from .reset_machine_id import reset_machine_id
from .disable_auto_update import disable_auto_update
from .reset_full_cursor import reset_full_cursor
from .bypass_version_check import bypass_version_check
from .bypass_token_limit import bypass_token_limit
from .show_config import show_config

# Import tính năng Email với error handling
try:
    from .email_generator import generate_extended_email, generate_multiple_emails
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# Import tính năng TempMail API với error handling
try:
    from .tempmail_api import TempMailAPI
    TEMPMAIL_AVAILABLE = True
except ImportError:
    TEMPMAIL_AVAILABLE = False

# Import các tính năng Augment Code với error handling
try:
    from .augment_utils import (
        check_jetbrains_installation,
        check_vscode_installation
    )
    from .augment_reset_ids import (
        reset_jetbrains_ids,
        reset_vscode_ids,
        reset_all_ids
    )
    from .augment_clean_database import clean_vscode_database, clean_telemetry_entries
    from .augment_terminate_ides import terminate_ides
    AUGMENT_AVAILABLE = True
except ImportError:
    AUGMENT_AVAILABLE = False

__all__ = [
    'reset_machine_id',
    'disable_auto_update',
    'reset_full_cursor',
    'bypass_version_check',
    'bypass_token_limit',
    'show_config'
]

# Thêm Email functions nếu có
if EMAIL_AVAILABLE:
    __all__.extend([
        'generate_extended_email',
        'generate_multiple_emails'
    ])

# Thêm TempMail API nếu có
if TEMPMAIL_AVAILABLE:
    __all__.extend([
        'TempMailAPI'
    ])

# Thêm Augment functions nếu có
if AUGMENT_AVAILABLE:
    __all__.extend([
        'check_jetbrains_installation',
        'check_vscode_installation',
        'reset_jetbrains_ids',
        'reset_vscode_ids',
        'reset_all_ids',
        'clean_vscode_database',
        'clean_telemetry_entries',
        'terminate_ides'
    ])
