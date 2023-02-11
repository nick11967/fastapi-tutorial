from typing import List, Union

from pydantic import BaseModel
        
class PlayerBase(BaseModel): # 인스턴스를 생성할 때나 읽을 때 공통으로 필요한 속성
    # id: int
    nickname: str 
    room_code: str
    # room_id: int
    
class PlayerCreate(PlayerBase): # 인스턴스를 생성할 때에만 필요하고 읽을 때는 필요 없는 속성
    pass
    
class Player(PlayerBase): # 인스턴스를 읽을 때에만 표시되고 생성할 때에는 없어도 되는 속성
    cards: List[int] = []

    class Config:
        orm_mode = True
        
class RoomBase(BaseModel): # 생성, 읽기 공통
    deck: List[int] = []
    code: str
    title: str
    player_num: int
    turninfo: int
      
class RoomCreate(RoomBase): # 생성
    pass

class Room(RoomBase): # 읽기
    players: List[Player] = [] 

    class Config:
        orm_mode = True


