from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
from app.services.whatsapp_service import send_whatsapp_message
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db)):
    items_str = ",".join(map(str, order.items))
    db_order = models.Order(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        items=items_str,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Send WhatsApp confirmation
    send_whatsapp_message(order.customer_phone, f"✅ Order {db_order.id} received. Status: {db_order.status}")

    return db_order

@router.get("/orders/", response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(database.get_db)):
    return db.query(models.Order).all()

@router.patch("/{order_id}")
def update_order_status(order_id: int, status: str, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()
    db.refresh(order)

    send_whatsapp_message(order.customer_phone, f"🔄 Order {order.id} status updated: {status}")
    return {"message": "Order status updated"}

@router.delete("/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = "canceled"
    db.commit()
    db.refresh(order)

    send_whatsapp_message(order.customer_phone, f"❌ Order {order.id} has been canceled")
    return {"message": "Order canceled"}
