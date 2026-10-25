import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

# Récupère le header HTTP Authorization: Bearer <token>
security_scheme = HTTPBearer()


def decode_access_token(token: str) -> str:
    """Décode le token JWT et extrait l'ID utilisateur ('sub')."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user_id: str | None = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide : claim 'sub' manquant",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider le token de sécurité",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> str:
    """Dépendance FastAPI injectable dans les routes pour récupérer l'ID de l'utilisateur authentifié."""
    return decode_access_token(credentials.credentials)