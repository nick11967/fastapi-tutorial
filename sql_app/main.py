from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

import string, random

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 방 코드 생성하는 함수: 알파벳 대문자 자음 + 모음 조합. ex) PANEMI, BOZAKI
def generate_code(db: Session = Depends(get_db)):
    vowel = 'AEIOU'
    cons = []
    for char in string.ascii_uppercase:
        if char not in vowel:
            cons.append(char)
    while True:
        temp = ''
        for i in range(3):
            temp += random.choice(cons)
            temp += random.choice(vowel)
        db_room = crud.get_room_by_roomcode(db=db, room_code=temp)
        if db_room:
            continue
        else:
            return temp
        
# 덱 생성하는 함수: 앞의 두 자리: 단계, 뒤의 두 자리: 카드 번호
def generate_deck():
    deck = []
    num = [0, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7] # 카드 단계별 장 수
    for level in range(1, len(num)): # 1~15 각 단계마다
        level_deck = list(range(1, num[level]+1)) # 단계별 카드 리스트
        random.shuffle(level_deck)
        level_deck = [level*100 + v for v in level_deck]
        for value in level_deck: 
            deck.append(value)
    return deck

# 방 생성, 생성된 방 코드 반환      
@app.post("/rooms/{player_num}") # response_model: 반환 데이터 타입
def create_room(player_num, db: Session = Depends(get_db)):
    room_code = generate_code(db) 
    deck = generate_deck()
    db_room = crud.create_room(db, code=room_code, deck=deck, player_num=player_num)
    return {"room_code": db_room.code}    

# 닉네임 중복 검사
@app.get("/players/")  
def check_nickname_exists(nickname: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, nickname)
    if db_player:
        return True
    else:
        return False    
        
# 플레이어 닉네임 받아 생성
@app.post("/players/") 
def create_player(nickname: str, db: Session = Depends(get_db)):
    if(check_nickname_exists(nickname, db)):
        raise HTTPException(status_code=404, detail="Nickname already registered")
    else:
        return crud.create_player(db=db, nickname=nickname)

# 현재 열려 있는 모든 방 반환 
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
    return {"room_code": player.room_code}


# 방이 다 찼는지 알려주기
@app.get("/rooms/{room_code}/player_num/") 
def check_full(room_code: str, db: Session = Depends(get_db)):
    db_room = crud.get_room_by_roomcode(db, room_code=room_code)
    cur_num = crud.get_player_num(db, room_code=room_code)
    if(cur_num < db_room.player_num):
        return False
    else:
        return True

# 현재 턴 정보 반환
@app.get("/rooms/turninfo/")
def read_turninfo(room_code: str, db: Session = Depends(get_db)):
    current_room = crud.get_room_by_roomcode(db, room_code=room_code)
    if current_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    turninfo = current_room.turninfo
    return {"turninfo": turninfo} 

# 플레이어 정보 {닉네임, 카드, room 코드} 반환
@app.get("/rooms/players/{nickname}")
def read_profile(nickname: str, db: Session = Depends(get_db)):
    player = crud.get_player(db, nickname=nickname)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
        # return None
    return {
        "nickname" : player.nickname,
        "cards" : player.cards,
        "room_code" : player.room_code
    }

# Room 정보 {room 코드, 덱, 턴 정보, 플레이어 번호} 반환
@app.get("/rooms/{room_code}")
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
    }

# 코드와 맞는 방에 사용자 추가
@app.put("/rooms/{room_code}")
def player_to_room(nickname: str, room_code: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, nickname=nickname)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    if check_full(room_code, db):
        raise HTTPException(status_code=404, detail="Room is full")
    else:
        # 해당 사용자의 룸코드 정보 변경
        db_player = crud.update_player_room(db, nickname=nickname, room_code=room_code)
    return {"room_code": room_code} 
    
# 플레이어 카드 처리. 0이면 구매, 1이면 버림
@app.put("/players/{nickname}/cards/", response_model=schemas.Player)
def buy_card(behavior: int, card_num: int, nickname: str, room_code: str, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, nickname=nickname)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    db_player = crud.update_player_card(db, card_num=card_num, num=behavior, nickname=nickname, room_code=room_code)
    return db_player
   
# 턴 종료 처리
@app.put("/rooms/{room_code}/turnend/", response_model=schemas.Room)
def make_turnend(room_code: str, db: Session = Depends(get_db)):
    db_room = crud.get_room_by_roomcode(db, room_code=room_code)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    db_room = crud.update_turndend(db, room_code=room_code)
    return db_room

# 방 삭제, 플레이어 정보 닉네임 제외하고 삭제
@app.delete("/rooms/{room_code}")
def delete_room(room_code: str, db: Session = Depends(get_db)):
    db_room = crud.get_room_by_roomcode(db, room_code=room_code)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    crud.delete_room(db, room_code=room_code)
    db.commit()  
    
    