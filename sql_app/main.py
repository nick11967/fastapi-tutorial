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
"""                          e x                          """
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
        
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)

@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

"""                          e x                          """

# 방과 생성 플레이어 받아 방 추가 + 방 코드 생성 + 덱 생성        
# 방 생성, 최초 플레이어는 플레이어 생성 함수 가져옴, 덱 생성하는 함수?
@app.post("/rooms/", response_model=schemas.Room) # response_model: 반환 데이터 타입
def create_room_and_first_player(
    room: schemas.RoomCreate, first_player: schemas.PlayerCreate, db: Session = Depends(get_db)
    ):
    # room 생성
    room_code = "" # 방 코드 생성하는 함수
    db_player = player_to_room(nickname=first_player.nickname, room_code=room_code, db=db) # ? 메인의 함수 호출
    return {"room_code": room_code}

# 플레이어 정보 받아 추가 + 닉네임 중복 검사
@app.post("/players/", response_model=schemas.Player) 
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player_by_nickname(db, nickname=player.nickname)
    if db_player:
        raise HTTPException(status_code=400, detail="nickname already registered")
    return crud.create_player(db=db, player=player)


# 현재 열려 있는 모든 방 정보 주기 
@app.get("/rooms/", response_model=List[schemas.Room])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = crud.get_rooms(db, skip=skip, limit=limit)
    return rooms

# 방 코드 알려주기 
@app.get("/rooms/players/{nickname}", response_model=schemas.Room)
def read_room(nickname: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, nickname=nickname)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    room_code = crud.get_room(db, nickname = nickname) 
    return {"room_code":room_code} 

# 코드와 맞는 방에 사용자 추가하기
@app.put("/rooms/{code}", response_model=schemas.Room)
def player_to_room(nickname: str, room_code: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, nickname=nickname)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    # 해당 사용자의 룸코드 정보 변경
    db_player=crud.update_player_room(db, nickname=nickname, room_code=room_code)
    return {"room_code":room_code} 
    
# 현재 턴 정보 알려주기
@app.get("/rooms/turninfo/")
def read_turninfo(room_code: str, db: Session = Depends(get_db)):
    current_room = crud.get_room_by_roomcode(db,room_code=room_code)
    turninfo = current_room.turninfo # ?
    return turninfo

# 턴 종료 처리
@app.put("/rooms/{code}/turnend/", response_model=schemas.Room)
def make_turnend(room_code: str, db: Session = Depends(get_db)):
    db_room = crud.update_turndend(db, room_code=room_code)
    return db_room


# put(”/players/{player_id}/cards/”) //  플레이어 카드 처리 (구매, 폐기)

# delete(”/rooms/{code}”) // 방 지우기

# delete(”/players/{player_id}”) // 플레이어 지우기