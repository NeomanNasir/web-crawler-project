#Here we will find all Latest and Trending news for aljazeera.com
import logging
import requests
import re
import csv
import sys
from html import unescape

def get_page_content(url):
    """get_page_content takes a url and returns the content of the page"""
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        logging.error(e)

    if response.ok:
        return response.text

    logging.error("Can not get content from: " + url)

def crawl_website():
    """Here we will accomplish all required stuff"""
    url = "https://www.aljazeera.com/"

    content = get_page_content(url)
    content = content.replace("\n", " ")

    latest_news = latest_news_pat.findall(content)
    for item in latest_news:
        link, title = item
        link = url + link
        title = unescape(title)
        link_dict = {"news_link": link, "news_title": title}
        csv_writer.writerow(link_dict)

    trending = trending_pat.findall(content)
    for item in trending:
        link, title = item
        link = url + link
        title = unescape(title)
        link_dict = {"news_link": link, "news_title": title}
        csv_writer.writerow(link_dict)

    msc = msc_pat.findall(content)
    msc = set(msc)
    for link in msc:
        link = url + link
        link_dict = {"news_link": link, "news_title": "take from link"}
        csv_writer.writerow(link_dict)

if __name__ == "__main__":
    latest_news_pat = re.compile(r'<div class="latest-news-topic">.*?href="/(.*?)"><h4 class="latest-news-topic-link">(.*?)<')
    trending_pat = re.compile(r'<div class="col-sm-7 news-trending-txt">.*?href="/(.*?)"><p>(.*?)<')
    msc_pat = re.compile(r'<a href="/(news/2018.*?)">')

    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m%d%Y %I:%M:%S %p',
    filename="aljazeera.log", level=logging.DEBUG)

    with open("aljazeera_links.csv", "w", encoding="ISO-8859-1") as csvf:
        csv_writer = csv.DictWriter(csvf, fieldnames=["news_link", "news_title"])
        csv_writer.writeheader()

        crawl_website()
        print("Crawling Done!")
