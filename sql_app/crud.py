from sqlalchemy.orm import Session
from . import models, schemas
from pydantic import parse_obj_as
from typing import List 

def get_player(db: Session, nickname: str):
    db_player = db.query(models.Player).filter(models.Player.nickname == nickname).first()
    if db_player is None:
        return None
    return schemas.Player.from_orm(db_player)

def get_players(db: Session, skip: int = 0, limit: int = 100):
     return parse_obj_as(schemas.List[schemas.Player], db.query(models.Player).offset(skip).limit(limit).all())

def get_room_by_roomcode(db:Session, room_code: str):
    db_room = db.query(models.Room).filter(models.Room.code == room_code).first()
    if db_room is None:
        return None
    return schemas.Room.from_orm(db_room)

def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return parse_obj_as(schemas.List[schemas.Room], db.query(models.Room).offset(skip).limit(limit).all())

def get_cur_player_num(db:Session, room_code: str):
    return db.query(models.Player).filter(models.Player.room_code == room_code).count()

def create_player(db: Session, nickname: str):
    db_player = models.Player(nickname=nickname)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return schemas.Player.from_orm(db_player)

def create_room(db: Session, code: str, title: str, deck: List[int], player_num: int):
    db_room = models.Room(code=code, title=title, turninfo=0, deck=deck, player_num=player_num)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return schemas.Room.from_orm(db_room)

def update_player_room(db: Session, nickname: str, room_code: str):
    db_room = db.query(models.Room).filter(models.Room.code == room_code)
    db_player = db.query(models.Player).filter(models.Player.nickname == nickname)

    room = db_room.first()
    room.players.append(db_player.first())
    db_player.update({
        'room_code': room_code
    })
    db.commit()
    db.refresh(db_player.first())
    db.refresh(db_room.first())
    return schemas.Player.from_orm(db_player.first())

def update_player_card(db: Session, card_num: int, num: int, nickname: str, room_code: str):
    db_room = db.query(models.Room).filter(models.Room.code == room_code)
    db_player = db.query(models.Player).filter(models.Player.nickname == nickname)
    if num == 0:          # 카드 구매
        cards = db_player.first().cards
        cards.append(card_num)
        db_player.update({'cards':cards})
        deck = db_room.first().deck
        deck.remove(card_num)
        db_room.update({'deck':deck})
    elif num == 1:        # 카드 버림
        cards = db_player.first().cards
        cards.remove(card_num)
        db_player.update({'cards':cards})
    else:
        pass
    db.commit()
    db.refresh(db_player.first())
    db.refresh(db_room.first())
    return schemas.Player.from_orm(db_player.first())

def update_turndend(db: Session, room_code: str):
    db_room = db.query(models.Room).filter(models.Room.code == room_code)
    db_room.update({
        # turninfo 증가 
        "turninfo": db_room.first().turninfo + 1
    })
    db.commit()
    db.refresh(db_room.first())
    return schemas.Room.from_orm(db_room.first())

def delete_room(db: Session, room_code: str):
    db_room = db.query(models.Room).filter(models.Room.code == room_code)
    db_players = db.query(models.Player).filter(models.Player.room_code == room_code)
    db_players.update({
        "room_code" : 0,
        "cards" : []
    })
    db_room.delete()
    db.commit()

def delete_player(db: Session, nickname: str):
    db_player = db.query(models.Player).filter(models.Player.nickname == nickname)
    db_player.delete()
    db.commit()