# Web Scraping with Python 03- Start Here
# By John Watson Rooney
# 02/09/2024
# Add functions
# Get info from product link page
# 03/06/2024
# Integrating a pagination while loop
# Getting rid of error: "httpx.ConnectError: [Errno 11001] getaddrinfo failed"
# Add timer and add CSV function



from urllib.parse import urljoin  # This library helps joins partial urls
from dataclasses import (
    dataclass,
    asdict,
)  # Creating a dataclass for the data instead of using a list
import httpx
from httpx import ReadTimeout
from selectolax.parser import HTMLParser
import time
# An app that shows the current time.
#import helper
# fields give us access to the field headers, useful for csv file.
from dataclasses import (
    dataclass,
    asdict,
    fields,
)  # Creating a dataclass for the data instead of using a list
import json
import csv

@dataclass
class Item:
    name: str
    Item_num: str
    POS_num: str
    Location: str
    Condition: str
    Price: float


def get_html(url, retries=3, **kwargs):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

    for _ in range(retries):
        try:
            resp = httpx.get(url, headers=headers, follow_redirects=True)
            resp.raise_for_status()
            html = HTMLParser(resp.text)
            return html

        except httpx.HTTPStatusError as exc:
            print(
                f"Error response {exc.response.status_code} while requesting {exc.request.url!r}. Page Limit Exceeded"
            )
            return False
        # except (httpx.RequestError, httpx.TimeoutError) as exc:
        # ChatGPT put httpx.TimeoutError which does not exist.
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            print(f"Error occurred: {exc}")
            print(f"Retrying request to {url}")
            time.sleep(2)  # Wait for 2 seconds before retrying
            continue
    print(f"Failed to fetch data from {url} after {retries} retries.")
    return False


def parse_search_page(html):
    products = html.css("section.plp-product-grid")  # Prints a bunch of <Node section>
    for product in products:
        yield urljoin(
            "https://www.guitarcenter.com/", product.css_first("a").attributes["href"]
        )


# def parse_item_page(html: HTMLParser):
def parse_item_page(html):
    new_item = Item(
        name=extract_text(html, "div.pdp-title"),
        Item_num=extract_text(html, "span.mr-1"),
        POS_num=extract_text(html, "span.pos"),
        # Got Location to work!
        Location=extract_text(html, "a.text-primaryColor"),
        Condition=extract_text(html, "*.jsx-2743111440"),
        Price=extract_text(html, "span.price-format"),
    )
    #return new_item
    # Have to change for json purposes but still good to use and understand data classes
    return asdict(new_item)

def extract_text(html, sel):
    try:
        # return html.css_first(sel).text()
        text = html.css_first(sel).text()
        # Cleanrdata is put into here
        return clean_data(text)
    except AttributeError:
        return None

def export_to_json(products):
    # Need encoding="utf-8" to get rid of trailing "," commas
    with open("products.json", "w", encoding="utf-8") as f:
        # Need ensure_ascii=False, indent=4 makes formatting much nicer
        json.dump(products, f, ensure_ascii=False, indent=4)
    print("saved to json")

def export_to_csv(products):
    # Taking field names from data classes. This shows data classes usefulness.
    field_names = [field.name for field in fields(Item)]
    # newline='' will get rid of blank lines between each record
    with open("products.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()
        writer.writerows(products)
    print("saved to csv")

# This gets put into extract_text()
def clean_data(value):
    chars_to_remove = ["Item #:", "POS #:", "Condition:", "$"]
    for char in chars_to_remove:
        if char in value:
            value = value.replace(char, "")
    # strip() removes any white space
    return value.strip()


def main():
    products = []
    x = 0
#    print("Time start: ", helper.get_time())

    while True:
        baseurl = f"https://www.guitarcenter.com/Used/Electric-Guitars.gc?N=1076+18145&Ns=cD&Nao={x}&pageName=used-page&recsPerPage=24&profileCountryCode=US&profileCurrencyCode=USD&SPA=true"
        print(f"Gathering page: {x}")
        html = get_html(baseurl)

        if html is False:
            break
        product_urls = parse_search_page(html)
        for url in product_urls:
            #print(url)
            html = get_html(url)  # Modified for chapter 3
            products.append(parse_item_page(html))
            time.sleep(1)

        x += 24

        # for product in products:
        #     print(asdict(product))

        export_to_json(products)
        export_to_csv(products)

if __name__ == "__main__":
    main()
