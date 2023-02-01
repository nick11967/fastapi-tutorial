from sqlalchemy.orm import Session

from . import models, schemas

from pydantic import parse_obj_as

def get_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    return schemas.User.from_orm(db_user)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return parse_obj_as(schemas.List[schemas.User], db.query(models.User).offset(skip).limit(limit).all())

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return schemas.User.from_orm(db_user)

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return parse_obj_as(schemas.List[schemas.Item],db.query(models.Item).offset(skip).limit(limit).all())

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return schemas.Item.from_orm(db_item)

"""                          e x                          """

def get_player_by_id(db: Session, player_id: int):
    db_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if db_player is None:
        return None
    return schemas.Player.from_orm(db_player)

def get_player(db: Session, nickname: str):
    db_player = db.query(models.Player).filter(models.Player.nickname == nickname).first()
    if db_player is None:
        return None
    return schemas.Player.from_orm(db_player)

def get_players(db: Session, skip: int = 0, limit: int = 100):
     return parse_obj_as(schemas.List[schemas.Player], db.query(models.Player).offset(skip).limit(limit).all())

def get_room_by_roomcode(db:Session, room_code: str):
    db_room = db.db.query(models.Room).filter(models.Room.code == room_code).first()
    if db_room is None:
        return None
    return schemas.Room.from_orm(db_room)

def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return parse_obj_as(schemas.List[schemas.Room], db.query(models.Room).offset(skip).limit(limit).all())

def create_player(db: Session, player: schemas.PlayerCreate, room_code: str):
    db_player = models.Player(nickname=player.nickname, room_code=room_code)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return schemas.Player.from_orm(db_player)

def update_player_room(db: Session, nickname: str, room_code: str):
    db_player = get_player(db, nickname)
    db_room = get_room_by_roomcode(db, room_code=room_code)
    db_player.update({
        "room_code" : room_code
    })
    db.commit()
    db.refresh(db_player)
    db.refresh(db_room)
    return schemas.Player.from_orm(db_player)

def update_turndend(db: Session, room_code: str):
    db_room = get_room_by_roomcode(db, room_code=room_code)
    db_room.update({
        # turninfo 증가 
        "turninfo": db_room.turninfo + 1 # ?
    })
    db.commit()
    db.refresh(db_room)
    return schemas.Room.from_orm(db_room)