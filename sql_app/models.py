from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from typing import List

from .database import Base

class Room(Base):
    __tablename__ = "rooms"
    
    code = Column(String, primary_key=True, index=True) # 플레이어들이 코드를 입력해서 방에 들어옴
    # id = Column(Integer, unique=True, index=True) # 방 번호
    deck = Column(List[int]) # ?
    turninfo = Column(Integer) 
    player_num = Column(Integer)
    
    players = relationship("Player", back_populates="room")

class Player(Base):
    __tablename__ = "players"
    
    nickname = Column(String, primary_key=True)
    # id = Column(Integer, unique=True, index=True)
    cards = Column(List[int]) # ?
    # room_id = Column(Integer, ForeignKey("rooms.id"))
    room_code = Column(String, ForeignKey("rooms.code"))
    
    room = relationship("Room", back_populates="players")
    