import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings  # où tu stockes SECRET_KEY

def generate_test_token(user_id="test-user", role="user", days=365):
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=days)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
