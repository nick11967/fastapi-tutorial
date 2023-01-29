from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from typing import List

from .database import Base

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True) # id와 code의 차이는?
    deck = Column(List[int]) # ?
    turninfo = Column(Integer) 
    
    players = relationship("Player", back_populates="room")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True)
    cards = Column(List[int]) # ?
    room_id = Column(Integer, ForeignKey("rooms.id"))
    
    room = relationship("Room", back_populates="players")
    