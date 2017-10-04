from typing import Optional, Union
from bloop import BaseModel, Column, String, Integer, Engine
from bloop.ext.pendulum import DateTime
import pendulum


PRICE_SCALE = 10000


class ScrapedData(BaseModel):
    class Meta:
        write_units = 10
        table_name = "teascraper.ScrapedData"
    id = Column(String, hash_key=True, name="id")
    date = Column(DateTime, range_key=True, name="sd")
    quantity = Column(Integer, name="q")
    url = Column(String, name="u")
    price = Column(Integer, name="p")


class Product(BaseModel):
    class Meta:
        write_units = 5
        table_name = "teascraper.Product"
    vendor_id = Column(String, hash_key=True, name="vid")
    product_id = Column(String, range_key=True, name="pid")
    sku = Column(String, name="sku")
    variation = Column(String, name="v")
    weight = Column(String, name="w")
    name = Column(String, name="n")


class VendorImports(BaseModel):
    class Meta:
        table_name = "teascraper.VendorImports"
    vendor_id = Column(String, hash_key=True, name="id")
    last_run_at = Column(DateTime, name="lr")


engine = Engine()
engine.bind(Product)
engine.bind(VendorImports)
engine.bind(ScrapedData)


def make_product_id(vendor: str, name: str, weight: str):
    name = name.lower().replace(" ", "-").replace(".", "_")
    product_name = vendor + "." + name + "." + weight
    return product_name


def unique_product_name(name: str, weight: str):
    name = name.lower().replace(" ", "-").replace(".", "_")
    product_name = name + "." + weight
    return product_name


def get_last_import_date(vendor_id: str):
    run = VendorImports(vendor_id=vendor_id)
    engine.load(run)
    return run.last_run_at


def set_last_import_date(vendor_id: str, date: pendulum.Pendulum):
    run = VendorImports(vendor_id=vendor_id, last_run_at=date)
    engine.save(run)


def insert_row(
        vendor_id: str,
        name: str,
        sku: str,
        variation: str,
        weight: str,
        quantity: Optional[int],
        date: pendulum.Pendulum,
        url: str,
        price: Optional[Union[int, float]]):
    product_id = unique_product_name(name, weight)
    if price is not None:
        price = int(price * PRICE_SCALE)
    product = Product(
        vendor_id=vendor_id,
        product_id=product_id,
        sku=sku or None,
        variation=variation or None,
        weight=weight or None,
        name=name
    )
    data = ScrapedData(
        id=vendor_id + "." + product_id,
        date=date,
        quantity=quantity,
        url=url,
        price=price
    )
    engine.save(product, data)


# insert_row("w2t", "repave", "25g", 2041, pendulum.now(), "my-url")
