"""Module for the login service"""

from fastapi import FastAPI, HTTPException, status, Depends, Response
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

def get_db():
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

#List all account (For Debuging)
@app.get("/api/login/view", response_model=list[AccountRead])
def get_all_bank_accounts(db: Session = Depends(get_db)):
    stmt = select(AccountDB).order_by(AccountDB.id)
    result = db.execute(stmt)
    account_list = result.scalars().all()
    return account_list

@app.post("/api/login/sign-up", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def add_user(payload: AccountCreate, db: Session = Depends(get_db)):
    """Sign In method to create an account"""
    account = AccountDB(**payload.model_dump())
    db.add(account)
    try:
        db.commit()
        db.refresh(account)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Account already exists")
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
        return "login Successful"
    raise HTTPException(status_code=400, detail="Incorrect Password")

@app.delete("/api/login/delete/{account_id}")
def get_user_login(account_id: int, db: Session = Depends(get_db)) -> Response:
    """Deletes a user from the database"""
    account = db.get(AccountDB, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/api/login/patch/{account_id}", response_model=AccountRead)
def partial_edit_login_details(account_id: int, payload: AccountPartialUpdate, db: Session = Depends(get_db)):
    """Edit email, username, or password"""
    account = db.query(AccountDB).filter(AccountDB.id == account_id).first()
    if not account:
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
    return account
