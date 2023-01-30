from sqlalchemy.orm import Session

from . import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

"""                          e x                          """

def get_player_by_id(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def get_player(db: Session, nickname: str):
    return db.query(models.Player).filter(models.Player.nickname == nickname).first()

def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_room(db: Session, nickname: str):
    return db.query(models.Player).filter(models.Player.nickname == nickname).first()
# ? 플레이어의 room code에 접근하는 법

def get_room_by_roomcode(db:Session, room_code: str):
    return db.query(models.Room).filter(models.Room.code == room_code).first()

def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()

def create_player(db: Session, player: schemas.PlayerCreate, room_code: str):
    db_player = models.Player(nickname=player.nickname, room_code=room_code)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def update_player_room(db: Session, nickname: str, room_code: str):
    db_player = get_player(db, nickname)
    db_room = get_room_by_roomcode(db, room_code=room_code)
    db_player.update({
        "room_code" : room_code
    })
    db.commit()
    db.refresh(db_player)
    db.refresh(db_room)
    return db_player

def update_turndend(db: Session, room_code: str):
    db_room = get_room_by_roomcode(db, room_code=room_code)
    db_room.update({
        # turninfo 증가 
    })
    db.commit()
    db.refresh(db_room)
    return db_room