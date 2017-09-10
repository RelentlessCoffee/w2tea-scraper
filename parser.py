import boto3
import base64
import pendulum
import bs4
import json
from data import insert_row

prefixes = {
    "w2t": "white2tea/raw_data/"
}


def list_objects(vendor: str, uploaded_after: pendulum.Pendulum):
    bucket = boto3.resource("s3").Bucket("tea-scraper")
    objects = []
    prefix = prefixes[vendor]
    for item in bucket.objects.filter(Prefix=prefix):
        # removes prefix from object key
        pieces = item.key[len(prefix):].split("/")
        date_string, encoded_url = pieces
        date = pendulum.parse(date_string)
        encoded_url = encoded_url.encode("utf-8")
        decoded_url = base64.b64decode(encoded_url)
        decoded_url = decoded_url.decode("utf-8")
        if date > uploaded_after:
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


def parse_and_upload(obj):
    soup = get_html(obj)
    name = find_name(soup)
    print(name)
    options = find_options(soup)
    date = obj["date"]
    vendor = obj["vendor"]
    url = obj["url"]
    for option in options:
        weight = option["weight"]
        quantity = option["quantity"]
        insert_row(vendor, name, weight, quantity, date, url)


def parse_and_upload_vendor(vendor: str, uploaded_after: pendulum.Pendulum):
    objs = list_objects(vendor, uploaded_after)
    for obj in objs:
        parse_and_upload(obj)


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
        if quantity == "":
            quantity = None
        else:
            quantity = int(quantity)
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
    date = pendulum.now().subtract(days=7)
    parse_and_upload_vendor(vendor, date)