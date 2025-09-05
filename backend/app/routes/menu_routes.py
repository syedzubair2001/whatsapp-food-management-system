# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app import models, schemas, database

# router = APIRouter(prefix="/menu", tags=["Menu"])

# @router.post("/", response_model=schemas.MenuItemResponse)
# def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(database.get_db)):
#     menu_item = models.MenuItem(**item.dict())
#     db.add(menu_item)
#     db.commit()
#     db.refresh(menu_item)
#     return menu_item

# @router.get("/", response_model=list[schemas.MenuItemResponse])
# def get_menu(db: Session = Depends(database.get_db)):
#     return db.query(models.MenuItem).all()



from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.utils import role_required

router = APIRouter(prefix="/menu", tags=["Menu"])

# Only restaurant can create menu items
@router.post("/", response_model=schemas.MenuItemResponse, dependencies=[Depends(role_required("restaurant"))])
def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(database.get_db)):
    menu_item = models.MenuItem(**item.dict())
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item

# Anyone (customer/restaurant/delivery) can see menu
@router.get("/", response_model=list[schemas.MenuItemResponse])
def get_menu(db: Session = Depends(database.get_db)):
    return db.query(models.MenuItem).all()
