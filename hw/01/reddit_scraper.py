import requests, bs4, os
import argparse
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
            'User-Agent': 'Reddit Rocks',
            'From': 'redditor@seznam.cz'
        }
        self.politeness_timeout = politeness_timeout


    def scrape(self):
        target_queue = ["/"] 
        scraped_posts = 0
        htmlparser = etree.HTMLParser()

        posts = []
        
        while target_queue and scraped_posts < self.target_post_count:
            target = target_queue.pop()

            print("FETCHING A NEW THING LIST...")

            # fetch the posts page target
            (page_data, cached) = self.fetch_target(target)
            print("")

            # parse the xml tree
            tree = etree.HTML(page_data)

            # find all things (posts)
            things = tree.xpath('//div[contains(@class, "thing")]')

            # exclude video and promoted things
            non_video_things = [thing for thing in things if thing.attrib.get("data-kind", "") != "video" and thing.attrib.get("data-promoted", "false") != "true"]

            # iterate over things and scrape title, text, timestamp, author, score, and comment
            for thing in non_video_things:
                # scrape the link to the thing detail
                thing_target = thing.attrib["data-permalink"].replace(f"/r/{self.subreddit}", "")

                # fetch the thing detail
                (thing_page_data, thing_cached) = self.fetch_target(thing_target)

                # parse the xml tree of the thing
                thing_tree = etree.HTML(thing_page_data)

                # parse title
                title = thing_tree.xpath('string(//p[contains(@class, "title")]/a[contains(@class, "title")])')

                # parse title
                text = thing_tree.xpath('string((//div[contains(@class, "sitetable")])[1]//div[contains(@class, "usertext-body")])')

                # parse timestamp
                timestamp = thing_tree.xpath('(//div[contains(@class, "sitetable")])[1]//div[contains(@class, "thing")]/@data-timestamp')[0]

                # parse author
                author = thing_tree.xpath('(//div[contains(@class, "sitetable")])[1]//div[contains(@class, "thing")]/@data-author')[0]

                # parse score
                score = thing_tree.xpath('(//div[contains(@class, "sitetable")])[1]//div[contains(@class, "thing")]/@data-score')[0]

                # parse the count of comments
                comments_count = thing_tree.xpath('(//div[contains(@class, "sitetable")])[1]//div[contains(@class, "thing")]/@data-comments-count')[0]


                if len(text) > 0:
                    # check whether the text is non-zero length (the thing is not of an image type)
                    post = {"title": title, "text": text, "timestamp": timestamp, "score": score, "comments_count": comments_count, "author": author} 
                    posts.append(post)
                    scraped_posts = scraped_posts + 1
                    print(f"SCRAPED - {scraped_posts}/{self.target_post_count}\n")
                else:
                    print(f"FOUND NON-TEXT THING\n")

                if not thing_cached:
                    # be polite!!!
                    time.sleep(self.politeness_timeout)

                if scraped_posts >= self.target_post_count:
                    break

            # find the link to the next page of things
            next_page_link = tree.xpath('//div[contains(@class, "nav-buttons")]//span[contains(@class, "next-button")]/a/@href')

            # a link to the next page exists
            if len(next_page_link) > 0:
                next_target = next_page_link[0].replace(self.get_base_url(), "")
                target_queue.append(next_target)
                posts_loaded = len(text)
            else:
                print("OUT OF POSTS :(")

            if not cached:
                # be polite!!!
                time.sleep(self.politeness_timeout)
                
        return posts

    def fetch_target(self, target):
        # check whether the target is already cachced
        page_data = self.cache.get_resource(target)
        cached = False
        if page_data is None:  
            # if not then fetch it
            link = self.get_url(target) 
            print(f"FETCHING - {link}")
            response = requests.get(f"{link}", headers=self.headers)
            page_data = response.text
            # add the page to the cache
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
        # initialize cache
        self.base_folder = base_folder
        if not os.path.exists(cache_folder):
            os.mkdir(cache_folder)

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
        # check whether the resource is already cached
        resource_name = self.sanitize_name(resource_name)
        resource_path = f"{self.base_folder}/{resource_name}"
        if os.path.exists(resource_path):
            with open(resource_path, "r") as resource_file: 
                return resource_file.read() 
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='subreddit', type=str, help="The subbredit to scrape")

    # Retur the input via different parameter name
    parser.add_argument('-c', '--count', dest='posts_count', type=int, default=50)
    parser.add_argument('-cf', '--cache-folder', dest='cache_folder', default="cache")
    parser.add_argument('-pt', '--politeness-timeout', dest='politiness_timeout', type=float, default=0.33)
    parser.add_argument('-o', '--output', dest='output_file')
    # TODO use refresh argument
    parser.add_argument('-r', '--refresh', dest='refresh', default=False)

    # TODO use ignore stickied posts
    parser.add_argument('-is', '--ignore-stickied', dest='ignore_stickied', default=True)

    args = parser.parse_args()

    subreddit = args.subreddit

    if args.output_file is None:
        args.output_file = f"{args.output_file}.json"

    cache = ResourceCache(args.cache_folder, subreddit)
    scraper = RedditScraper(subreddit, args.posts_count, cache, args.politiness_timeout)
    posts = scraper.scrape()
    json = json.dumps(posts)
    output_file_name = args.output_file
    with open(output_file_name, "w") as output_file: 
        output_file.write(json)
        print(f"\nOUTPUT SAVED TO {output_file_name}")



