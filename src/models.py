from datetime import date, datetime, time

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import false, func

from src.constants import Role


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(nullable=True)
    is_disabled: Mapped[bool] = mapped_column(server_default=false())
    role: Mapped[int] = mapped_column(server_default=str(Role.GUEST.value))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    event_date: Mapped[date] = mapped_column(nullable=False)
    event_time: Mapped[time] = mapped_column(nullable=False)
    sale_time: Mapped[datetime] = mapped_column(nullable=False)
    sale_end_time: Mapped[datetime] = mapped_column(nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    organizer: Mapped[str] = mapped_column(String(255), nullable=False)
    on_sale: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class EventPicture(Base):
    __tablename__ = "event_pictures"

    picture_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id", ondelete="CASCADE"))
    picture_url: Mapped[str] = mapped_column(String(255), nullable=True)
    picture_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    picture_order: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class EventTicketType(Base):
    __tablename__ = "event_ticket_types"

    ticket_type_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.event_id", ondelete="CASCADE"))
    ticket_name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. VIP, 一般票
    max_purchase_limit: Mapped[int | None] = mapped_column(nullable=True)  # null 表示不限
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
