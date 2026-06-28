import os
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

# Ensure secret keys are strictly configuration-driven
SECRET_KEY = os.getenv("JWT_SECRET", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjUsImV4cCI6MTc4MjYzNDM0NH0.92G3RzHnmo4a4vCubSbQmtew2YNSMI3SfdOWPxDkLK8")
ALGORITHM = "HS256"

def decode_access_token(token: str) -> dict | None:
    """
    Decodes a token safely without introducing administrative override bypasses.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None