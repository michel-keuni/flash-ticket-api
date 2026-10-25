from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# 1. Création du moteur asynchrone SQLAlchemy
# On convertit le PostgresDsn de Pydantic en string pour SQLAlchemy
async_engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.IS_DEV,  # Affiche les requêtes SQL en dev si True
    future=True,
    pool_size=20,          # Nombre de connexions maintenues dans le pool
    max_overflow=10,       # Connexions supplémentaires autorisées en cas de pic
)

# 2. Fabrique de sessions asynchrones
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# 3. Classe de base pour nos modèles ORM
class Base(DeclarativeBase):
    pass

# 4. Dépendance FastAPI pour injecter la session dans les routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()