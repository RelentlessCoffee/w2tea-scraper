from typing import Optional
from bloop import BaseModel, Column, String, Integer, Engine
from bloop.ext.pendulum import DateTime
import pendulum


class Product(BaseModel):
    class Meta:
        write_units = 5
    name = Column(String, hash_key=True, name="n")
    date = Column(DateTime, range_key=True, name="d")
    quantity = Column(Integer, name="q")
    url = Column(String, name="u")
    og_name = Column(String, name="og")


class VendorImports(BaseModel):
    vendor = Column(String, hash_key=True, name="v")
    last_run_at = Column(DateTime, name="lr")


engine = Engine()
engine.bind(Product)
engine.bind(VendorImports)


def make_product_name(vendor: str, name: str, weight: str):
    name = name.lower().replace(" ", "-").replace(".", "_")
    product_name = vendor + "." + name + "." + weight
    return product_name


def get_last_import_date(vendor: str):
    run = VendorImports(vendor=vendor)
    engine.load(run)
    return run.last_run_at


def set_last_import_date(vendor: str, date: pendulum.Pendulum):
    run = VendorImports(vendor=vendor, last_run_at=date)
    engine.save(run)


def insert_row(vendor: str, name: str, weight: str, quantity: Optional[int], date: pendulum.Pendulum, url: str):
    product = Product()
    product.name = make_product_name(vendor, name, weight)
    product.date = date
    product.quantity = quantity
    product.url = url
    product.og_name = name
    engine.save(product)


# insert_row("w2t", "repave", "25g", 2041, pendulum.now(), "my-url")
