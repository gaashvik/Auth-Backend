from jose import jwt, jwk
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
import requests, os
from dotenv import load_dotenv

load_dotenv()
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS = ["RS256"]

token_auth_scheme = HTTPBearer()

jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
jwks = requests.get(jwks_url).json()["keys"]

def verify_jwt(token: str):
    header = jwt.get_unverified_header(token)
    # pick the correct JWK
    key_data = next(k for k in jwks if k["kid"] == header["kid"])
    # build a key object
    rsa_key = jwk.construct(key_data)
    # decode
    payload = jwt.decode(
        token,
        rsa_key,
        algorithms=ALGORITHMS,
        audience=API_AUDIENCE,
        issuer=f"https://{AUTH0_DOMAIN}/",
    )
    return payload

async def get_current_user(token: str = Security(token_auth_scheme)):
    try:
        return verify_jwt(token.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
