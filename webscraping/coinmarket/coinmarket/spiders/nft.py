import scrapy
from scrapy.selector import Selector
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from shutil import which
import time
import datetime

class NftSpider(scrapy.Spider):
    name = 'nft'
    # allowed_domains = ['coinmarketcap.com']
    # start_urls = ['http://coinmarketcap.com/']
    def start_requests(self):
        yield SeleniumRequest (
            url = 'https://coinmarketcap.com',
            wait_time = 3,
            screenshot = True,
            callback=self.parse_result,
        )

    def parse_result(self, response):
        
        driver = response.meta['driver']
        nft_tab = driver.find_elements_by_xpath("//a[@class='table-control-link-button cmc-link']")
        # nft_tab[3].click()

        scroll_pause_time = 1
        screen_height = driver.execute_script("return window.screen.height;")
        i = 1

        while True:
            # scroll one screen height each time
            driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
            i += 1
            time.sleep(scroll_pause_time)
            # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
            scroll_height = driver.execute_script("return document.body.scrollHeight;")  
            # Break the loop when the height we need to scroll to is larger than the total scroll height
            if (screen_height) * i > scroll_height:
                break

        time.sleep(3)

        html = driver.page_source
        resp_obj = Selector(text=html)
        
        for coin in resp_obj.xpath("//tbody/tr"):
            yield {
                'datetime': datetime.datetime.now(),
                'name': coin.xpath(".//td[3]/div/a/div/div/p/text()").get(),
                'abbrv': coin.xpath(".//td[3]/div/a/div/div/div/p/text()").get(),
                'price': coin.xpath(".//td[4]/div/a/text()[1]").get(),
                '24h_percentage': coin.xpath(".//td[5]/span/text()[1]").get(),
                '24h_situation': coin.xpath(".//td[5]/span/span/@class").get().replace("icon-Caret-",""),
                '7d_percentage': coin.xpath(".//td[6]/span/text()[1]").get(),
                '7d_situation': coin.xpath("//td[6]/span/span/@class").get().replace("icon-Caret-",""),
                'marketcap': coin.xpath(".//td[7]/p/span[2]/text()").get(),
                'volume(24h)': coin.xpath(".//td[8]/div/a/p/text()").get(),
                'circulating_supply': coin.xpath(".//td[9]/div//p/text()").get().split(" ")[0]
                

            }

        next_page = response.xpath("//div[@class='sc-4r7b5t-3 bvcQcm']//li[@class='next']/a/@href").get()
        if next_page:
            absolute_url = f"https://coinmarketcap.com{next_page}"
            yield SeleniumRequest (
                url = absolute_url,
                wait_time = 3,
                callback=self.parse_result
            )
        
