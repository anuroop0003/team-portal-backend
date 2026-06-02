# Constants for auth package

# Token types
TOKEN_TYPE_VERIFICATION = "verification"
TOKEN_TYPE_INVITATION = "invitation"

# Expiration configurations
VERIFICATION_TOKEN_EXPIRE_MINUTES = 15
INVITATION_TOKEN_EXPIRE_HOURS = 24

# Roles
ROLE_OWNER = "OWNER"

# Default names
DEFAULT_INVITER_NAME = "Administrator"

# Audit Log actions
AUDIT_SIGN_IN = "SIGN_IN"
AUDIT_RESET_PASSWORD = "RESET_PASSWORD"

# Error Details and Messages
ERR_EMAIL_ALREADY_REGISTERED = "Email already registered"
ERR_REGISTRATION_FAILED_PREFIX = "Registration failed"
ERR_USER_NOT_FOUND = "User not found"
ERR_INVALID_TOKEN = "Invalid token"
ERR_INVALID_EXPIRED_VERIFICATION_TOKEN = "Invalid or expired verification token"
ERR_INVALID_EXPIRED_RESET_TOKEN = "Invalid or expired reset token"

# Auth Credentials Error Keys/Messages
ERR_CODE_INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
ERR_MSG_INVALID_CREDENTIALS = "Incorrect email or password"

ERR_CODE_ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED"
ERR_MSG_ACCOUNT_DEACTIVATED = "Account is deactivated"

ERR_CODE_EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"
ERR_MSG_EMAIL_NOT_VERIFIED = "Email not verified"

# Success / Info API Messages
MSG_EMAIL_VERIFIED_SUCCESS = "Email verified successfully"
MSG_VERIFICATION_SENT_FALLBACK = "If an account exists, a verification link was sent"
MSG_EMAIL_ALREADY_VERIFIED = "Email is already verified"
MSG_VERIFICATION_LINK_GENERATED = "Verification link generated"
MSG_RESET_LINK_GENERATED = "Reset link generated"
MSG_RESET_SENT_FALLBACK = "If an account exists, a reset link was sent"
MSG_PASSWORD_RESET_SUCCESS = "Password reset successfully"
