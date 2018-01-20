from lxml import html
import requests
from selenium import webdriver
import os
import sys
import pandas as pd

class ProductPage(object):
    name = None
    picture = None
    product_name = None
    description = None
    joined_category = None

    def out(self):
        return [
            self.name,
            self.picture,
            1,
            self.product_name,
            1,
            self.joined_category,
            self.description
        ]

def scrape(driver, name):
    product = ProductPage()
    product.name = name

    driver.get("https://www.hubba.com/products/"+ name)

    if driver.current_url == "https://www.hubba.com/":
        return None
    product.product_name = driver.find_element_by_class_name("product-page__desktop-header").text.split("\n")[0]
    product.description = driver.find_element_by_class_name("hui-accordion-pane__content--description").text

    driver.find_element_by_class_name("image-overlay").click()
    product.picture = driver.find_element_by_class_name("hubba-ui-full-content-slider--active").find_element_by_tag_name("img").get_attribute("ng-src")
    return product

def scrape_missing_products(headless = False):
    import data
    chrome_options = webdriver.ChromeOptions()
    
    if headless:
        chrome_options.add_argument('headless')
        chrome_options.add_argument('no-sandbox')

    filedir = os.path.dirname(os.path.abspath(__file__))
    driver = webdriver.Chrome(filedir + "/chromedriver", chrome_options = chrome_options)

    result = []
    missing_products = data.get_missing_products()
    N = len(missing_products)
    for i, missing_prod in enumerate(missing_products):
        print("\r{}/{}\t".format(i+1, N), end="")
        prod = scrape(driver, missing_prod)
        if prod:
            result.append(prod.out())

    df = pd.DataFrame(result)
    df.columns = ["name", "picture", "no_of_rows", "product_name", "count", "joined_category", "description"]

    return df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input file", type=str)
    parser.add_argument("--headless", help="whether to use headles", action="store_true")
    args = parser.parse_args()
    headless = args.headless
    output_filename = args.input

    df = scrape_missing_products(headless=headless)
    df.to_csv(output_filename)
