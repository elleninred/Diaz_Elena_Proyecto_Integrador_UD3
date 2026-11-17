from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.configuracion import obtener_url_bd


engine = create_engine(
    obtener_url_bd(),
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=True,
    expire_on_commit=False,
)
