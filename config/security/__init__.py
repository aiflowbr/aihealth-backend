# auth
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import hashlib

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/users/authenticate")
PWD_CONTEXT = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
SECRET_KEY = "s3cr3t@@^"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 240


# Função para gerar o hash SHA256 da concatenação de username e password
def hash_password(password: str):
    # Gerar o hash SHA256
    hashed_password = PWD_CONTEXT.hash(password)
    return hashed_password


# Function to verify password. try plain sha256 before sha256_crypt
def verify_password(plain_password, hashed_password):
    shadigest = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    check = shadigest == hashed_password.encode("utf-8")
    if not check:
        # try new algo sha256_crypt
        check = PWD_CONTEXT.verify(plain_password, hashed_password)
    return check
