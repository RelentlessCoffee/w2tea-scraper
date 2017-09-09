from bloop import BaseModel, Column, String, Integer, Engine
from bloop.ext.pendulum import DateTime
import pendulum


class Product(BaseModel):
    name = Column(String, hash_key=True, name="n")
    date = Column(DateTime, range_key=True, name="d")
    quantity = Column(Integer, name="q")
    url = Column(String, name="u")


engine = Engine()
engine.bind(Product)


def insert_row(vendor: str, name: str, variation: str, quantity: int, date: pendulum.Pendulum, url: str):
    product = Product()
    product.name = vendor + "." + name + "." + variation
    product.date = date
    product.quantity = quantity
    product.url = url
    engine.save(product)


# insert_row("w2t", "repave", "25g", 2041, pendulum.now(), "my-url")
