import requests
import bs4
import boto3
import datetime
import base64

HOMEPAGE_URL = "http://white2tea.com/tea-shop/"


def load_single_page(url):
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    return soup


def parse_nav_tree(root, path=None):
    path = path or []
    results = []
    for child in root.contents:
        if not child.name:
            continue
        name = child.a.text
        next_root = child.ul
        child_path = path + [name]
        if not next_root:
            url = child.a["href"]
            results.append((child_path, url))
        else:
            results.extend(parse_nav_tree(next_root, path=child_path))
    return results


def get_categories():
    soup = load_single_page(HOMEPAGE_URL)
    root = soup.find('ul', class_="product-categories")
    return parse_nav_tree(root)


def get_product_urls(soup):
    product_urls = []
    while soup:  # while soup is not none process next page.
        links = soup.find_all('div', class_="product-title")
        for link in links:
            link = link.a["href"]
            product_urls.append(link)
        soup = get_next_page(soup)
    return product_urls


def get_next_page(soup):
    page = soup.find('a', class_="next page-numbers")
    if page is None:
        return None
    else:
        link = page["href"]
        return load_single_page(link)


# product_name = link.a.text


def encode_url(url):
    encoded_url = base64.b64encode(url.encode("utf-8"))
    return encoded_url.decode("utf-8")


def timestamp():
    now = datetime.datetime.utcnow()
    time_stamp = now.isoformat()
    return time_stamp


def upload_to_s3(url, page_data, time_stamp):
    bucket_name = 'tea-scraper'
    path = [
        "white2tea",
        "raw_data",
        time_stamp,
        encode_url(url)
    ]
    key = "/".join(path)
    data = page_data
    s3 = boto3.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=key, Body=data)


if __name__ == '__main__':
    time_stamp = timestamp()
    categories = get_categories()
    all_products = set()
    for _, url in categories:
        urls = get_product_urls(load_single_page(url))
        all_products.update(urls)
    for url in sorted(all_products):
        response = requests.get(url)
        page_data = response.text
        upload_to_s3(url, page_data, time_stamp)
