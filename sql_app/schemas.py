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
        
class RoomBase(BaseModel): 
    deck: List[int] = []
    code: str
    player_num: int
    turninfo: int
      
class RoomCreate(RoomBase): 
    pass

class Room(RoomBase): 
    players: List[Player] = []
    class Config:
        orm_mode = True


