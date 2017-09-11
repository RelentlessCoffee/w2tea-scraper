import boto3
import base64
import pendulum
import bs4
import json
from data import insert_row, get_last_import_date, set_last_import_date

prefixes = {
    "w2t": "white2tea/raw_data/"
}


def list_objects(vendor: str, uploaded_on: pendulum.Pendulum):
    bucket = boto3.resource("s3").Bucket("tea-scraper")
    objects = []
    prefix = prefixes[vendor] + uploaded_on.to_date_string()
    for item in bucket.objects.filter(Prefix=prefix):
        # removes prefix from object key
        pieces = item.key[len(prefix):].split("/")
        date_string, encoded_url = pieces
        date = pendulum.parse(date_string)
        encoded_url = encoded_url.encode("utf-8")
        decoded_url = base64.b64decode(encoded_url)
        decoded_url = decoded_url.decode("utf-8")
        obj = {
            "vendor": vendor,
            "date": date,
            "url": decoded_url,
            "item": item
        }
        objects.append(obj)
    return objects


def get_html(obj):
    item = obj["item"].get()
    content = item["Body"].read()
    soup = bs4.BeautifulSoup(content, 'html.parser')
    return soup


def list_days_between(start: pendulum.Pendulum, end: pendulum.Pendulum):
    start = start.start_of("day")
    end = end.start_of("day")
    days = []
    while start < end:
        days.append(start)
        start = start.add(days=1)
    return days


def parse_and_upload(obj):
    soup = get_html(obj)
    name = find_name(soup)
    options = find_options(soup)
    date = obj["date"]
    vendor = obj["vendor"]
    url = obj["url"]
    for option in options:
        weight = option["weight"]
        quantity = option["quantity"]
        insert_row(vendor, name, weight, quantity, date, url)


def parse_and_upload_vendor(vendor: str):
    start = get_last_import_date(vendor)
    end = pendulum.utcnow()
    days = list_days_between(start, end)
    for date in days:
        objs = list_objects(vendor, date)
        for obj in objs:
            parse_and_upload(obj)
        set_last_import_date(vendor, date)


class NoMaxQuantity(Exception):
    pass


def _find_options_from_form(soup):
    form = soup.find("form", class_="variations_form cart")
    if form is None:
        raise NoMaxQuantity("no max quantity")
    product_data = form['data-product_variations']
    product_data = json.loads(product_data)
    quantities = [option["max_qty"] for option in product_data]
    options = soup.find_all("option")[1:]
    options = [option["value"] for option in options]
    # return list(zip(options, quantities))
    option_dicts = []
    for option, quantity in zip(options, quantities):
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = None
        option_dicts.append({
            "weight": option,
            "quantity": quantity
            })
    return option_dicts


def _find_options_from_input(soup):
    product_data = soup.find("input", class_="input-text qty text")
    if product_data is None:
        return [{"weight": "", "quantity": None}]
    try:
        quantity = product_data['max']
    except KeyError:
        quantity = ""
    if quantity == "":
        return [{"weight": "", "quantity": None}]
    return [{"weight": "", "quantity": int(quantity)}]


def find_options(soup):
    try:
        return _find_options_from_form(soup)
    except NoMaxQuantity:
        return _find_options_from_input(soup)


def find_name(soup):
    title = soup.find("h1")
    return title.string.strip()


if __name__ == '__main__':
    vendor = "w2t"
    parse_and_upload_vendor(vendor)