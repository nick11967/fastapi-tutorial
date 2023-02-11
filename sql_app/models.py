from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from typing import List

from .database import Base

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

class Room(Base):
    __tablename__ = "rooms"
    
    code = Column(String, primary_key=True, index=True) # 플레이어들이 코드를 입력해서 방에 들어옴
    title = Column(String, default="Room Title") # 방 제목. 방을 구분하기 쉽게 해줌.
    deck = Column(MutableList.as_mutable(PickleType), default=[])
    turninfo = Column(Integer, default=0)
    # id = Column(Integer, unique=True, index=True)
    
    players = relationship("Player", back_populates="room")

class Player(Base):
    __tablename__ = "players"
    
    nickname = Column(String, primary_key=True)
    cards = Column(MutableList.as_mutable(PickleType), default=[])
    room_code = Column(String, ForeignKey("rooms.code"), default=0)
    # id = Column(Integer, unique=True, index=True)
    # room_id = Column(Integer, ForeignKey("rooms.id"))
    
    room = relationship("Room", back_populates="players")
    