import requests
import logging
import sys
import re
import csv
from html import unescape
from urllib.request import urlopen

def write_webpage_as_html(filepath, data):
    try:
        with open(filepath, 'wb') as fobj:
            if data:
                fobj.write(data)
    except Exception as e:
        logging.error(e)

def get_page_content(url):
    """take url link and return the content of the page"""
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        logging.error(e)

    if response.ok:
        response = response.text
        response = response.replace("\n", " ")
        return response

    logging.error("Can not get content from: " + url)
    return ""

def get_next_page(content):
    """takes page content and returns next_page url if have"""
    next = next_page_pat.findall(content)
    if len(next) == 0:
        return None

    return next[0]

def scrape_post_links(content, category_name):
    """takes category content and put required info in a csv file"""
    posts = post_link_pat.findall(content)

    for item in posts:
        link, title = item
        title = unescape(title)
        print("Scraping: " + title)
        logging.info("Scraping: " + link)

        post_info = {"Title": title, "Post Link": link, "Category": category_name}
        csv_writer.writerow(post_info)
        global news_links
        news_links += "<li><a href = '{}'target='_blank'>{} <><><><><> Catagory: {}</li>\n".format(link, title, category_name)


def crawl_category(category_url, category_name):
    """which takes category_url and category_name and
    do scraping tasks in a category"""
    while True:
        content = get_page_content(category_url)
        scrape_post_links(content, category_name)

        next_page = get_next_page(content)
        if next_page is None:
            break

        category_url = next_page


def crawl_website():
    """This is the main function that coordinates the whole crawling tasks"""
    url = "http://subeen.com/"
    content = get_page_content(url)
    if content == "":
        logging.critical("Got nothing form: " + url)
        sys.exit(1)

    categories = category_pat.findall(content)
    for item in categories:
        category, category_name = item

        crawl_category(category, category_name)

if __name__ == "__main__":
    category_pat = re.compile(r'<li class="cat-item.*?"><a href="(.*?)" >(.*?)<')
    post_link_pat = re.compile(r'<h2 class="entry-title"><a href="(.*?)" rel="bookmark">(.*?)<')
    next_page_pat = re.compile(r'<a class="next page-numbers" href="(.*?)">')
    htmltext = '''
<html>
    <head><title>Simple News Link Scrapper</title></head>
    <body>
        {NEWS_LINKS}
    </body>
</html>
'''
    news_links = '<ol>'
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt = '%m%d%Y %I:%M:%S %p',
    filename="subeen_site_crawler.log", level = logging.DEBUG)

    with open("subeen_site_posts.csv", "w", encoding = "UTF-8") as csvf:
        csv_writer = csv.DictWriter(csvf, fieldnames=["Title", "Post Link", "Category"])
        csv_writer.writeheader()

        crawl_website()
        news_links += '</ol>'
        htmltext = htmltext.format(NEWS_LINKS = news_links)
        write_webpage_as_html('subeen_site_all_posts.html', htmltext.encode())
        print("Crawling Done!")
