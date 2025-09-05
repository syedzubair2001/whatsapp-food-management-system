# from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database import Base

# class MenuItem(Base):
#     __tablename__ = "menu_items"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     description = Column(String, nullable=True)
#     price = Column(Float, nullable=False)
#     available = Column(Boolean, default=True)

# class Order(Base):
#     __tablename__ = "orders"

#     id = Column(Integer, primary_key=True, index=True)
#     customer_name = Column(String, nullable=False)
#     customer_phone = Column(String, nullable=False)
#     items = Column(String, nullable=False)  # store as comma-separated
#     status = Column(String, default="pending")



from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# ------------------ User Model ------------------ #
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # hashed password
    role = Column(String, nullable=False)  # customer / restaurant / delivery

    # One-to-many relationship: one user can place many orders
    orders = relationship("Order", back_populates="user")


# ------------------ Menu Item Model ------------------ #
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    available = Column(Boolean, default=True)


# ------------------ Order Model ------------------ #
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    items = Column(String, nullable=False)  # store as comma-separated
    status = Column(String, default="pending")

    # Link order to a user
    user_id = Column(Integer, ForeignKey("users.id"), nullable = True)
    user = relationship("User", back_populates="orders")
