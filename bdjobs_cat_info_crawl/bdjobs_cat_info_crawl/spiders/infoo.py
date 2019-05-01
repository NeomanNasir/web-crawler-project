# -*- coding: utf-8 -*-
# A project with scrapy + selenium
from scrapy import Spider
from selenium import webdriver
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.common.exceptions import NoSuchElementException
from time import sleep


class InfooSpider(Spider):
    name = 'infoo'
    allowed_domains = ['jobs.bdjobs.com/jobsearch.asp?fcatId=8&icatId=']
    # start_urls = ['http://jobs.bdjobs.com/jobsearch.asp?fcatId=8&icatId=']

    def start_requests(self):
        self.driver = webdriver.Chrome('/home/nnasir/Programming/ScrapingUdemyCourse/chromedriver')
        self.driver.get('http://jobs.bdjobs.com/jobsearch.asp?fcatId=8&icatId=')

        sel = Selector(text=self.driver.page_source)
        jobs = sel.xpath('//*[@class="job-title-text"]/a/@href').extract()
        for job in jobs:
            url = 'http://jobs.bdjobs.com/' + job
            yield Request(url, callback=self.parse_job)

        while True:
            try:
                xnext = sel.xpath('//a[text()="Next »"]/@href').extract_first()
                if xnext == 'javascript:void(0)':
                    self.logger.info('No more page to load!')
                    self.driver.quit()
                    break
                next_page = self.driver.find_element_by_xpath('//a[text()="Next »"]')
                sleep(3)
                self.logger.info('Sleeping for 3 seconds!')
                next_page.click()

                sel = Selector(text=self.driver.page_source)
                jobs = sel.xpath('//*[@class="job-title-text"]/a/@href').extract()
                for job in jobs:
                    url = 'http://jobs.bdjobs.com/' + job
                    yield Request(url, callback=self.parse_job)

            except NoSuchElementException:
                self.logger.info('No more page to load!')
                self.driver.quit()
                break


    def parse_job(self, response):
        job_title = response.xpath('.//*[@class="job-title "]/text()').extract_first()
        comp_name = response.xpath('.//*[@class="company-name "]/text()').extract_first()
        job_loc = response.xpath('.//*[@class="job_loc "]/p/text()').extract_first()
        salary = response.xpath('.//*[@class="salary_range"]/ul/text()').extract_first()
        Emp_st = response.xpath('.//*[@class="job_nat"]/p/text()').extract_first()
        edu_req = response.xpath('//*[@class="edu_req"][1]/ul/li/text()').extract()
        yield {'job title': job_title,
               'company name': comp_name,
               'job location': job_loc,
               'salary': salary,
               'Employment Status': Emp_st,
               'Educational requirments': edu_req}
