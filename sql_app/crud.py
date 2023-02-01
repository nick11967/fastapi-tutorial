from sqlalchemy.orm import Session

from . import models, schemas

from pydantic import parse_obj_as

def get_player(db: Session, nickname: str):
    db_player = db.query(models.Player).filter(models.Player.nickname == nickname).first()
    if db_player is None:
        return None
    return schemas.Player.from_orm(db_player)

'''
def get_player_by_id(db: Session, player_id: int):
    db_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if db_player is None:
        return None
    return schemas.Player.from_orm(db_player)
'''
def get_players_in_room(db: Session, room_code: str):
     return parse_obj_as(schemas.List[schemas.Player], db.query(models.Player).filter(models.Player.room_code == room_code).all())

def get_players(db: Session, skip: int = 0, limit: int = 100):
     return parse_obj_as(schemas.List[schemas.Player], db.query(models.Player).offset(skip).limit(limit).all())

def get_room_by_roomcode(db:Session, room_code: str):
    db_room = db.query(models.Room).filter(models.Room.code == room_code).first()
    if db_room is None:
        return None
    return schemas.Room.from_orm(db_room)

def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return parse_obj_as(schemas.List[schemas.Room], db.query(models.Room).offset(skip).limit(limit).all())

def create_player(db: Session, nickname: str):
    db_player = models.Player(nickname=nickname)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return schemas.Player.from_orm(db_player)

def create_room(db: Session, code: str, deck: int, player_num: int):
    db_room = models.Room(code=code, deck=deck, turninfo=0, player_num=player_num)
    db.commit()
    db.refresh(db_room)
    return schemas.Room.from_orm(db_room)

def update_player_room(db: Session, nickname: str, room_code: str):
    db_room = get_room_by_roomcode(db, room_code=room_code)
    db_player = get_player(db, nickname)
    
    db_room.first().players.append(db_player)
    db_player.first().room.append(db_room)
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
        "turninfo": db_room.turninfo + 1
    })
    db.commit()
    db.refresh(db_room)
    return schemas.Room.from_orm(db_room)

def delete_room(db: Session, room_code: str):
    db_room = get_room_by_roomcode(db, room_code=room_code)
    db_players = get_players_in_room(db, room_code=room_code)
    for player in db_players:
        player.update({
            "room_code": None,
            "cards": None,
            "room": None
        })
    db_room.delete()
    db.commit()
    db.refresh(db_players)
