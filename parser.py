import boto3
import base64
import bs4
import pendulum
import json
from s3 import cache_for_host
from data import insert_row, get_last_import_date, set_last_import_date
cache = cache_for_host()
prefixes = {
    "w2t": "white2tea/raw_data/"
}


def list_objects(vendor: str, uploaded_on: pendulum.Pendulum):
    bucket = boto3.resource("s3").Bucket("tea-scraper")
    objects = []
    prefix = prefixes[vendor]
    for item in bucket.objects.filter(Prefix=prefix + uploaded_on.to_date_string()):
        # removes prefix from object key
        pieces = item.key[len(prefix):].split("/")
        date_string, encoded_url = pieces
        date = pendulum.parse(date_string)
        encoded_url = encoded_url.encode("utf-8")
        decoded_url = base64.b64decode(encoded_url)
        decoded_url = decoded_url.decode("utf-8")
        obj = {
            "vendor_id": vendor,
            "date": date,
            "url": decoded_url,
            "item": item
        }
        objects.append(obj)
    return objects


def get_html(obj):
    content = cache.get(obj["item"])
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
    parsed_data = form_try(soup, obj["vendor_id"], obj["url"], obj["date"])
    for entry in parsed_data:
        insert_row(**entry)


def parse_and_upload_vendor(vendor_id: str):
    start = get_last_import_date(vendor_id)
    end = pendulum.utcnow()
    days = list_days_between(start, end)
    for date in days:
        objs = list_objects(vendor_id, date)
        for obj in objs:
            parse_and_upload(obj)
        set_last_import_date(vendor_id, date)


def form_try(soup, vendor_id, url, date):
    data = parse_from_form(soup)
    if data is None:
        data = [parse_from_page(soup)]
    for entry in data:
        entry["name"] = find_name(soup)
        entry["vendor_id"] = vendor_id
        entry["url"] = url
        entry["date"] = date
    return data


def parse_from_form(soup):
    form = soup.find("form", class_="variations_form cart")
    if form is None:
        return None
    product_data = form['data-product_variations']
    form = json.loads(product_data)
    parsed_data = []
    for entry in form:
        quantity = entry["max_qty"]
        if quantity is not None:
            quantity = int(quantity)
        parsed_data.append({
            "sku": entry['sku'],
            "variation": str(entry['variation_id']),
            "weight": entry['attributes']['attribute_pa_amount'],
            "quantity": quantity,
            "price": float(entry['display_price'])
        })
    return parsed_data


def find_price(soup):
    el = soup.find("p", class_="price")
    if el is None:
        return None
    prices = el.find_all("span", class_="woocommerce-Price-amount amount")
    assert len(prices) == 1, prices
    price = prices[0].contents[-1]
    return float(price)


def find_quantity_page(soup):
    product_data = soup.find("input", class_="input-text qty text")
    if product_data is None:
        return None
    try:
        quantity = product_data['max']
    except KeyError:
        quantity = ""
    if quantity == "":
        return None
    return int(quantity)


def find_variation_page(soup):
    variation = soup.find("input", attrs={"name": "add-to-cart"})
    if variation is None:
        return ""
    try:
        return str(variation["value"])
    except KeyError:
        return ""


def find_sku_page(soup):
    el = soup.find("span", class_="sku")
    if el is None:
        return ""
    try:
        sku = el.text
    except KeyError:
        return ""
    return sku


def parse_from_page(soup):
    parsed_data = {
        "sku": find_sku_page(soup),
        "variation": find_variation_page(soup),
        "quantity": find_quantity_page(soup),
        # there is no weight when there is no form
        "weight": "",
        "price": find_price(soup)
    }
    return parsed_data


def find_name(soup):
    title = soup.find("h1")
    return title.string.strip()


if __name__ == '__main__':
    vendor_id = "w2t"
    parse_and_upload_vendor(vendor_id)