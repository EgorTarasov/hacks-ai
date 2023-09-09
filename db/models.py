from sqlalchemy import Integer, String, Boolean, ForeignKey, Table, Column, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from db import Base


class User(Base):
    """
        id	Integer	Unique identifier for this user or bot. This number may have more than 32 significant bits and some programming languages may have difficulty/silent defects in interpreting it. But it has at most 52 significant bits, so a 64-bit integer or double-precision float type are safe for storing this identifier.
        is_bot	Boolean	True, if this user is a bot
        first_name	String	User's or bot's first name
        last_name	String	Optional. User's or bot's last name
        username	String	Optional. User's or bot's username
        language_code	String	Optional. IETF language tag of the user's language
        is_premium	True	Optional. True, if this user is a Telegram Premium user
        added_to_attachment_menu	True	Optional. True, if this user added the bot to the attachment menu
        can_join_groups	Boolean	Optional. True, if the bot can be invited to groups. Returned only in getMe.
        can_read_all_group_messages	Boolean	Optional. True, if privacy mode is disabled for the bot. Returned only in getMe.
        supports_inline_queries	Boolean	Optional. True, if the bot supports inline queries. Returned only in getMe.
    """
    __tablename__ = "tg_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, index=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    first_name: Mapped[str] = mapped_column(String(256))
    last_name: Mapped[str] = mapped_column(String(256), nullable=True)
    username: Mapped[str] = mapped_column(String(256), nullable=True)
    language_code: Mapped[str] = mapped_column(String(20))
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=True)

    state: Mapped["UserState"] = relationship(
        "UserState", primaryjoin="User.id == UserState.user_id", back_populates="user"
    )


class UserState(Base):
    __tablename__ = "user_state"

    user_id: Mapped[int] = mapped_column(ForeignKey("tg_users.id"), primary_key=True)
    state: Mapped[str] = mapped_column(String(256))
    train: Mapped[str] = mapped_column(String(256), nullable=True)
    text: Mapped[str] = mapped_column(String(256), nullable=True)
    voice_file: Mapped[str] = mapped_column(String(256), nullable=True)
    index: Mapped[int] = mapped_column(Integer, default=0)
    last_recognized_text: Mapped[str]= mapped_column(String(2048), nullable=True)
    response_one: Mapped[str] = mapped_column(String(2048), nullable=True)
    response_two: Mapped[str] = mapped_column(String(2048), nullable=True)
    response_three: Mapped[str] = mapped_column(String(2048), nullable=True)

    user: Mapped["User"] = relationship(
        "User", primaryjoin="UserState.user_id == User.id", back_populates="state"
    )

    def __repr__(self):
        return f"<UserState state:{self.state}, train:{self.train}>"


