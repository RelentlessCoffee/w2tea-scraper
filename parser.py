import boto3
import base64
import pendulum
import bs4

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
