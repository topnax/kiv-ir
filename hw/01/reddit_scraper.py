import requests, bs4, os
import time
import json
from datetime import date
from xml.etree import ElementTree
from lxml import etree

SUBREDDIT_POSTS_PAGE = "https://old.reddit.com/r/"

class RedditScraper:

    def __init__(self, subreddit, target_post_count, cache, politeness_timeout=1):
        self.subreddit = subreddit
        self.target_post_count = target_post_count
        self.cache = cache
        self.headers = {
            'User-Agent': 'ADA Agent',
            'From': 'charles.hoskinson@cardano.org'
        }
        self.politeness_timeout = politeness_timeout


    def scrape(self):
        target_queue = ["/"] 
        scraped_posts = 0
        htmlparser = etree.HTMLParser()

        posts = []
        
        while target_queue and scraped_posts < self.target_post_count:
            target = target_queue.pop()
            
            (page_data, cached) = self.fetch_target(target)

            tree = etree.HTML(page_data)

            text = tree.xpath('//div[contains(@class, "thing")]/div[contains(@class, "entry")]//p[contains(@class, "title")]/a/text()')
            things = tree.xpath('//div[contains(@class, "thing")]')
            non_video_things = [thing for thing in things if not "data-kind" in thing.attrib or thing.attrib["data-kind"] != "video"]

            for thing in non_video_things:
                next_target = thing.attrib["data-permalink"].replace(f"/r/{self.subreddit}", "")
                (thing_page_data, thing_cached) = self.fetch_target(next_target)
                thing_tree = etree.HTML(thing_page_data)
                title = thing_tree.xpath('string(//p[contains(@class, "title")]/a[contains(@class, "title")])')
                text = thing_tree.xpath('string((//div[contains(@class, "sitetable")])[1]//div[contains(@class, "usertext-body")])')

                timestamp = thing_tree.xpath('(//div[contains(@class, "sitetable")])[1]//div[contains(@class, "thing")]/@data-timestamp')[0]

                author = thing_tree.xpath('(//div[contains(@class, "sitetable")])[1]//div[contains(@class, "thing")]/@data-author')[0]
                score = thing_tree.xpath('(//div[contains(@class, "sitetable")])[1]//div[contains(@class, "thing")]/@data-score')[0]
                comments_count = thing_tree.xpath('(//div[contains(@class, "sitetable")])[1]//div[contains(@class, "thing")]/@data-comments-count')[0]
                


                if len(text) > 0:
                    post = {"title": title, "text": text, "timestamp": timestamp, "score": score, "comments_count": comments_count} 
                    posts.append(post)
                    scraped_posts = scraped_posts + 1
                    print(f"SCRAPED {scraped_posts}/{self.target_post_count}")
            
                if not thing_cached:
                    time.sleep(self.politeness_timeout)

                if scraped_posts >= self.target_post_count:
                    break


            next_page_link = tree.xpath('//div[contains(@class, "nav-buttons")]//span[contains(@class, "next-button")]/a/@href')
            next_target = next_page_link[0].replace(self.get_base_url(), "")
            target_queue.append(next_target)
            posts_loaded = len(text)

            if not cached:
                time.sleep(self.politeness_timeout)
                
        return posts

    def fetch_target(self, target):
        page_data = self.cache.get_resource(target)
        cached = False
        if page_data is None:  
            link = self.get_url(target) 
            print(f"fetching: {link}")
            response = requests.get(f"{link}", headers=self.headers)

            page_data = response.text
            
            self.cache.add_resource(target, page_data) 
        else:
            cached = True
            print(f"CACHED - {target}")
        return (page_data, cached)

    def get_base_url(self):
        return f"{SUBREDDIT_POSTS_PAGE}{self.subreddit}" 

    def get_url(self, target):
        return f"{self.get_base_url()}{target}" 


class ResourceCache:

    def __init__(self, cache_folder, subdirectory):
        base_folder = f"{cache_folder}/{subdirectory}"
        self.base_folder = base_folder
        if not os.path.exists(base_folder):
            os.mkdir(base_folder)

    def sanitize_name(self, resource_name):
        return resource_name.replace("/", "#")

    def add_resource(self, resource_name, resource):
        resource_name = self.sanitize_name(resource_name)
        resource_path = f"{self.base_folder}/{resource_name}"
        if os.path.exists(resource_path):
            os.remove(resource_path)
        with open(resource_path, "w") as resource_file: 
            resource_file.write(resource) 

    def get_resource(self, resource_name):
        resource_name = self.sanitize_name(resource_name)
        resource_path = f"{self.base_folder}/{resource_name}"
        if os.path.exists(resource_path):
            with open(resource_path, "r") as resource_file: 
                print(f"{resource_name} cached")
                return resource_file.read() 
        return None


if __name__ == "__main__":
    subreddit = "cardano"
    cache = ResourceCache("cache", subreddit)
    scraper = RedditScraper(subreddit, 550, cache)
    posts = scraper.scrape()
    json = json.dumps(posts)
    with open(f"{subreddit}.json", "w") as output_file: 
        output_file.write(json)

