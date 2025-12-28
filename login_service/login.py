"""Module for the login service"""

import json
import os
import aio_pika
from fastapi import FastAPI, HTTPException, status, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from .database import engine, SessionLocal
from .models import Base, AccountDB
from .schemas import (
    AccountCreate, AccountLogin, AccountRead, AccountPartialUpdate
)

app = FastAPI()
Base.metadata.create_all(bind=engine)

#Rabbit MQ
EXCHANGE_NAME = "just_feed_exchange"
RABBIT_URL = os.getenv("RABBIT_URL")

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_exchange():
    """
    Open a connection, create a channel and declare a topic exchange.
    Returns (connection, channel, exchange).
    """
    conn = await aio_pika.connect_robust(RABBIT_URL)
    ch = await conn.channel()
    ex = await ch.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC)
    return conn, ch, ex

def get_db():
    """Opens and closes db connection for endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/login/view/{account_id}", response_model=AccountRead)
def get_account_details_by_id(account_id: int, db: Session = Depends(get_db)):
    """Returns user details using an id as an AccountRead"""
    account = db.get(AccountDB, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="bank account not found")
    return account

@app.get("/api/login/view", response_model=list[AccountRead])
def get_all_bank_accounts(db: Session = Depends(get_db)):
    """Method for getting all accounts"""
    stmt = select(AccountDB).order_by(AccountDB.id)
    result = db.execute(stmt)
    account_list = result.scalars().all()
    return account_list

@app.post("/api/login/sign-up", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def add_user(payload: AccountCreate, db: Session = Depends(get_db)):
    """Sign In method to create an account"""
    account = AccountDB(**payload.model_dump())
    db.add(account)
    conn, ch, ex = await get_exchange()

    try:
        db.commit()
        db.refresh(account)
    except IntegrityError:
        db.rollback()
        msg = aio_pika.Message(body=json.dumps("Account couldn't be created successfully").encode())
        await ex.publish(msg, routing_key="account.create")
        await conn.close()
        raise HTTPException(status_code=409, detail="Account already exists")

    msg = aio_pika.Message(body=json.dumps("Account created successfully").encode())
    await ex.publish(msg, routing_key="account.create")
    await conn.close()
    return account

@app.post("/api/login/sign-in")
def get_user_login(payload: AccountLogin, db: Session = Depends(get_db)):
    """Login checks if user exists in database and if passwords match"""
    payload_data = AccountDB(**payload.model_dump())
    stmt = select(AccountDB).where(AccountDB.email == payload_data.email)
    account = db.execute(stmt).scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Incorrect Email")
    if payload_data.password == account.password:
        return {"id": account.id, "response": "login Successful"}
    raise HTTPException(status_code=400, detail="Incorrect Password")

@app.delete("/api/login/delete/{account_id}")
async def delete_user_login(account_id: int, db: Session = Depends(get_db)) -> Response:
    """Deletes a user from the database"""
    account = db.get(AccountDB, account_id)
    conn, ch, ex = await get_exchange()

    if not account:
        msg = aio_pika.Message(body=json.dumps("Account couldn't be deleted successfully").encode())
        await ex.publish(msg, routing_key="account.delete")
        await conn.close()
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()

    msg = aio_pika.Message(body=json.dumps("Account deleted successfully").encode())
    await ex.publish(msg, routing_key="account.delete")
    await conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/api/login/patch/{account_id}", response_model=AccountRead)
async def partial_edit_login_details(account_id: int, payload: AccountPartialUpdate, db: Session = Depends(get_db)):
    """Edit email, username, or password"""
    account = db.query(AccountDB).filter(AccountDB.id == account_id).first()
    conn, ch, ex = await get_exchange()

    if not account:
        msg = aio_pika.Message(body=json.dumps("Account couldn't be edited successfully").encode())
        await ex.publish(msg, routing_key="account.edit")
        await conn.close()
        raise HTTPException(status_code=404, detail="Account not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
    try:
        db.add(account)
        db.commit()
        db.refresh(account)
    except IntegrityError:
        db.rollback()
        msg = aio_pika.Message(body=json.dumps("Account couldn't be edited successfully").encode())
        await ex.publish(msg, routing_key="account.edit")
        await conn.close()
        raise HTTPException(status_code=409, detail="Conflict")

    msg = aio_pika.Message(body=json.dumps("Account edited successfully").encode())
    await ex.publish(msg, routing_key="account.edit")
    await conn.close()
    return account
