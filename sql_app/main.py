from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# TODO: 방과 생성 플레이어 받아 방 추가 + 방 코드 생성 + 덱 생성        
# 방 생성, 최초 플레이어는 플레이어 생성 함수 가져옴, 덱 생성하는 함수?
@app.post("/rooms/", response_model=schemas.Room) # response_model: 반환 데이터 타입
def create_room_and_first_player(
    room: schemas.RoomCreate, first_player: schemas.PlayerCreate, db: Session = Depends(get_db)
    ):
    # room 생성
    room_code = "" # 방 코드 생성하는 함수
    db_player = player_to_room(nickname=first_player.nickname, room_code=room_code, db=db) # ? 메인의 함수 호출
    return {"room_code": room_code}

# TODO: 플레이어 정보 받아 추가 + 닉네임 중복 검사
@app.post("/players/", response_model=schemas.Player) 
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, nickname=player.nickname)
    if db_player:
        raise HTTPException(status_code=400, detail="nickname already registered")
    return crud.create_player(db=db, player=player)


# 현재 열려 있는 모든 방 정보 주기 
@app.get("/rooms/", response_model=List[schemas.Room])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms

# 방 코드 반환
@app.get("/rooms/players/{nickname}")
def read_roomcode(nickname: str, db: Session = Depends(get_db)):
    player = crud.get_player(db, nickname=nickname)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
        # return None
    return player.room_code

# 현재 턴 정보 반환
@app.get("/rooms/turninfo/")
def read_turninfo(room_code: str, db: Session = Depends(get_db)):
    current_room = crud.get_room_by_roomcode(db,room_code=room_code)
    turninfo = current_room.turninfo
    return turninfo

# 플레이어 정보 {닉네임, 카드, room 코드} 반환
@app.get("/rooms/players/{nickname}")
def read_profile(nickname: str, db: Session = Depends(get_db)):
    player = crud.get_player(db, nickname=nickname)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
        # return None
    return {
        "nickname": player.nickname,
        "cards": player.cards,
        "room_code" : player.room_code
        # "id": player.id
        # room_id = Column(Integer, ForeignKey("rooms.id"))
    }

# Room 정보 {room 코드, 덱, 턴 정보, 플레이어 번호} 반환
@app.get("/rooms/{code}")
def read_room(room_code: str, db: Session = Depends(get_db)):
    room = crud.get_room_by_roomcode(db, room_code=room_code)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
        # return None
    return {
        "code": room.code,
        "deck": room.deck,
        "turninfo": room.turninfo, 
        "player_num": room.player_num
        # "id": room.id
    }

# 코드와 맞는 방에 사용자 추가하기
@app.put("/rooms/{code}", response_model=schemas.Room)
def player_to_room(nickname: str, room_code: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, nickname=nickname)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    # 해당 사용자의 룸코드 정보 변경
    db_player=crud.update_player_room(db, nickname=nickname, room_code=room_code)
    return {"room_code":room_code} 
    

# 턴 종료 처리
@app.put("/rooms/{code}/turnend/", response_model=schemas.Room)
def make_turnend(room_code: str, db: Session = Depends(get_db)):
    db_room = crud.update_turndend(db, room_code=room_code)
    return db_room

# TODO
# put(”/players/{player_id}/cards/”) //  플레이어 카드 처리 (구매, 폐기)

# delete(”/rooms/{code}”) // 방 지우기

# delete(”/players/{player_id}”) // 플레이어 지우기