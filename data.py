from typing import Optional, Union
from bloop import BaseModel, Column, String, Integer, Engine, BloopException
from bloop.ext.pendulum import DateTime
import pendulum


PRICE_SCALE = 10000


class ScrapedData(BaseModel):
    class Meta:
        write_units = 5
        table_name = "teascraper.ScrapedData"
    id = Column(String, hash_key=True, dynamo_name="id")
    date = Column(DateTime, range_key=True, dynamo_name="sd")
    quantity = Column(Integer, dynamo_name="q")
    url = Column(String, dynamo_name="u")
    price = Column(Integer, dynamo_name="p")


class Product(BaseModel):
    class Meta:
        write_units = 5
        table_name = "teascraper.Product"
    vendor_id = Column(String, hash_key=True, dynamo_name="vid")
    product_id = Column(String, range_key=True, dynamo_name="pid")
    sku = Column(String, dynamo_name="sku")
    variation = Column(String, dynamo_name="v")
    weight = Column(String, dynamo_name="w")
    name = Column(String, dynamo_name="n")


class VendorImports(BaseModel):
    class Meta:
        table_name = "teascraper.VendorImports"
    vendor_id = Column(String, hash_key=True, dynamo_name="id")
    last_run_at = Column(DateTime, dynamo_name="lr")


engine = Engine()
models = [Product, VendorImports, ScrapedData]
# super hack to handle table setup
# in read-only prod environment
for model in models:
    try:
        engine.bind(model)
    except BloopException:
        print("Skipping table setup for " + model.__name__)
        engine.bind(model, skip_table_setup=True)


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
        dynamo_name=name
    )
    data = ScrapedData(
        id=vendor_id + "." + product_id,
        date=date,
        quantity=quantity,
        url=url,
        price=price
    )
    engine.save(product, data)


def list_vendors():
    imports = engine.scan(VendorImports)
    vendors = []
    for item in imports:
        vendors.append(item.vendor_id)
    return vendors


def list_products(vendor_id):
    products = engine.query(Product, key=Product.vendor_id == vendor_id)
    return list(products)


def get_product(vendor_id, product_id):
    product = Product(vendor_id=vendor_id, product_id=product_id)
    engine.load(product)
    return product


def list_samples(vendor_id, product_id):
    id = vendor_id + "." + product_id
    samples = engine.query(ScrapedData, key=ScrapedData.id == id)
    samples = list(samples)
    for sample in samples:
        if sample.price is not None:
            sample.price /= float(PRICE_SCALE)
    return samples
