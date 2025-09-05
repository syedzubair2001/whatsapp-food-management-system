


# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app import models, schemas, database
# from app.services.whatsapp_service import send_whatsapp_message
# from typing import List
# from app.utils import role_required

# router = APIRouter(prefix="/orders", tags=["Orders"])

# # Only customer can place orders
# @router.post("/", response_model=schemas.OrderResponse, dependencies=[Depends(role_required("customer"))])
# def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db)):
#     items_str = ",".join(map(str, order.items))
#     db_order = models.Order(
#         customer_name=order.customer_name,
#         customer_phone=order.customer_phone,
#         items=items_str,
#         status="pending"
#     )
#     db.add(db_order)
#     db.commit()
#     db.refresh(db_order)

#     # WhatsApp confirmation
#     send_whatsapp_message(order.customer_phone, f"✅ Order {db_order.id} received. Status: {db_order.status}")
#     return db_order


# # Restaurant can view all orders
# @router.get("/", response_model=List[schemas.OrderResponse], dependencies=[Depends(role_required("restaurant"))])
# def get_orders(db: Session = Depends(database.get_db)):
#     return db.query(models.Order).all()


# # Restaurant or Delivery can update status
# @router.patch("/{order_id}", dependencies=[Depends(role_required("restaurant"))])
# def update_order_status(order_id: int, status: str, db: Session = Depends(database.get_db)):
#     order = db.query(models.Order).filter(models.Order.id == order_id).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")

#     order.status = status
#     db.commit()
#     db.refresh(order)

#     send_whatsapp_message(order.customer_phone, f"🔄 Order {order.id} status updated: {status}")
#     return {"message": "Order status updated"}


# # Only restaurant can cancel order
# @router.delete("/{order_id}", dependencies=[Depends(role_required("restaurant"))])
# def cancel_order(order_id: int, db: Session = Depends(database.get_db)):
#     order = db.query(models.Order).filter(models.Order.id == order_id).first()
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")

#     order.status = "canceled"
#     db.commit()
#     db.refresh(order)

#     send_whatsapp_message(order.customer_phone, f"❌ Order {order.id} has been canceled")
#     return {"message": "Order canceled"}




from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.utils import get_current_user  # adjust path if needed


from app import models, schemas, database
from app.services.whatsapp_service import send_whatsapp_message
from app.utils import role_required

router = APIRouter(prefix="/orders", tags=["Orders"])


# # ------------------- Customer: Place Order ------------------- #
# @router.post("/", response_model=schemas.OrderResponse, dependencies=[Depends(role_required("customer"))])
# def create_order(order: schemas.OrderCreate, db: Session = Depends(database.get_db)):
#     items_str = ",".join(map(str, order.items))
#     db_order = models.Order(
#         customer_name=order.customer_name,
#         customer_phone=order.customer_phone,
#         items=items_str,
#         status="pending"
#     )
#     db.add(db_order)
#     db.commit()
#     db.refresh(db_order)

#     # WhatsApp confirmation (safe)
#     result = send_whatsapp_message(
#         order.customer_phone,
#         f"✅ Order {db_order.id} received. Status: {db_order.status}"
#     )
#     if result.get("status") == "failed":
#         print(f"⚠️ WhatsApp failed: {result['error']}")

#     return db_order

@router.post("/", response_model=schemas.OrderResponse, dependencies=[Depends(role_required("customer"))])
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    items_str = ",".join(map(str, order.items))
    
    db_order = models.Order(
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        items=items_str,
        status="pending",
        user_id=current_user.id  # now safe
    )

    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    # WhatsApp message (safe)
    try:
        result = send_whatsapp_message(
            order.customer_phone,
            f"✅ Hello {order.customer_name}, your order {db_order.id} has been received. Status: {db_order.status}"
        )
        if result.get("status") == "failed":
            print(f"⚠️ WhatsApp failed: {result['error']}")
    except Exception as e:
        print(f"⚠️ WhatsApp exception: {e}")

    return db_order



# ------------------- Restaurant + Delivery: View Orders ------------------- #
@router.get("/", response_model=List[schemas.OrderResponse], dependencies=[Depends(role_required(["restaurant", "delivery"]))])
def get_orders(db: Session = Depends(database.get_db)):
    return db.query(models.Order).all()


# ------------------- Restaurant + Delivery: Update Status ------------------- #
@router.patch("/{order_id}", dependencies=[Depends(role_required(["restaurant", "delivery"]))])
def update_order_status(order_id: int, status: str, db: Session = Depends(database.get_db), current_user=Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Optional: restrict what each role can update
    if current_user.role == "delivery" and status not in ["picked_up", "delivered"]:
        raise HTTPException(status_code=403, detail="Delivery can only update to 'picked_up' or 'delivered'")

    order.status = status
    db.commit()
    db.refresh(order)

    result = send_whatsapp_message(
        order.customer_phone,
        f"🔄 Order {order.id} status updated: {status} by {current_user.role}"
    )
    if result.get("status") == "failed":
        print(f"⚠️ WhatsApp failed: {result['error']}")

    return {"message": f"Order status updated by {current_user.role}"}

# ------------------- Restaurant: Cancel Order ------------------- #
@router.delete("/{order_id}", dependencies=[Depends(role_required("customer"))])
def cancel_order(order_id: int, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = "canceled"
    db.commit()
    db.refresh(order)

    result = send_whatsapp_message(
        order.customer_phone,
        f"❌ Order {order.id} has been canceled"
    )
    if result.get("status") == "failed":
        print(f"⚠️ WhatsApp failed: {result['error']}")

    return {"message": "Order canceled"}
