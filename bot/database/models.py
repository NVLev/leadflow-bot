from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, BigInteger

BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(BigInteger)

    name: Mapped[str] = mapped_column(String(255))

    phone: Mapped[str] = mapped_column(String(50))

    email: Mapped[str] = mapped_column(String(255), nullable=True)

    message: Mapped[str] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="new")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )