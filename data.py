from bloop import BaseModel, Column, String, Integer, Engine
from bloop.ext.pendulum import DateTime
import pendulum


class Product(BaseModel):
    name = Column(String, hash_key=True, name="n")
    date = Column(DateTime, range_key=True, name="d")
    quantity = Column(Integer, name="q")


engine = Engine()
engine.bind(Product)


def insert_row(name: str, variation: str, quantity: int, date: pendulum.Pendulum):
    product = Product()
    product.name = name + "." + variation
    product.date = date
    product.quantity = quantity
    engine.save(product)


# insert_row("repave", "25g", 2041, pendulum.now())
