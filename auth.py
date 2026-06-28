import os
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError

# Environment માંથી સિક્રેટ કી મેળવશે, નહીંતર ફોલબેક કી વાપરશે
SECRET_KEY = os.getenv("JWT_SECRET", "your-fallback-secure-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # ટોકન એક્સપાયરી ટાઈમ (1 કલાક)

def create_access_token(data: dict) -> str:
    """
    યુઝર લૉગિન થાય ત્યારે તેના ડેટા (ઈમેલ/sub) સાથે સિક્યોર JWT ટોકન જનરેટ કરે છે.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    """
    રિક્વેસ્ટ વખતે આવતા ઓથોરાઈઝેશન ટોકનને ડીકોડ અને વેરીફાય કરે છે.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None