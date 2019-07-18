import requests
import csv

from bs4 import BeautifulSoup

URL_BASE = "https://www.apple.com"
STORE_LIST_URL = "/retail/storelist/"


def get_phone_from_store_page(path):
    html = requests.get("{}{}".format(URL_BASE, path)).content
    soup = BeautifulSoup(html, features="lxml")
    return soup.find('span', attrs={'class': 'store-phone'}).text


def get_phone_from_store_listing(ul):
    return ul.find_all('li')[-1].text


def get_details_from_store_li(store, region, country):
    store_url = store.find('a').attrs['href']
    store_name = store.text
    print(store_name)
    try:
        store_phone = get_phone_from_store_page(store_url)
    except AttributeError:
        store_phone = ''
    return {
        'name': store_name,
        'url': "{}{}".format(URL_BASE, store_url),
        'region': region,
        'country': country,
        'phone': store_phone
    }


def get_details_from_store_ul(store, region, country):
    store_link = store.find('a')
    store_url = store_link.attrs['href']
    store_name = store_link.text
    print(store_name)
    try:
        store_phone = get_phone_from_store_listing(store)
    except AttributeError:
        store_phone = ''
    return {
        'name': store_name,
        'url': "{}{}".format(URL_BASE, store_url),
        'region': region,
        'country': country,
        'phone': store_phone
    }


def country_has_sections(country):
    sections = country.find_all('div', attrs={'class': 'toggle-section'})
    n_sections = len(sections)
    return n_sections > 0


def fetch_store_details(soup):
    store_details = []

    countries = soup.find_all('div', attrs={'class': 'listing'})
    for country in countries:
        country_name = country.attrs['id']

        if country_has_sections(country):
            regions = country.find_all(attrs={'class': 'toggle-section'})
            for region in regions:
                region_name = region.find('h3').text

                if country_name == "usstores":
                    for store in region.find_all('li'):
                        details = get_details_from_store_li(
                            store, region_name, country_name)
                        store_details.append(details)

                else:
                    for store in region.find_all('ul'):
                        details = get_details_from_store_ul(
                            store, region_name, country_name)
                        store_details.append(details)

        else:
            for store in country.find_all('ul'):
                details = get_details_from_store_ul(store, '', country_name)
                store_details.append(details)

    return store_details


def write_csv(store_details, fname, header):
    with open(fname, 'w') as f:
        writer = csv.DictWriter(f, header)
        writer.writeheader()
        writer.writerows(store_details)


if __name__ == '__main__':
    html = requests.get("{}{}".format(URL_BASE, STORE_LIST_URL)).content
    soup = BeautifulSoup(html, features="lxml")

    store_details = fetch_store_details(soup)
    write_csv(store_details, "./apple_stores.csv",
              ('country', 'region', 'name', 'url', 'phone'))
