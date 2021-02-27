# Simple Reddit scraper
- written in Python
- stores downloaded webpages to a cache to reduce the number of network calls when run multiple times to scrape the same subreddit
## Usage
```
$ python3 reddit_scraper.py cardano --count 5
FETCHING A NEW THING LIST...
FETCHING - https://old.reddit.com/r/cardano/

FETCHING - https://old.reddit.com/r/cardano/comments/ltqdkv/were_bringing_down_the_fake_daedalus_play_store/
SCRAPED - 1/5

FETCHING - https://old.reddit.com/r/cardano/comments/ltlu4c/fake_deadalus_wallet_play_store/
SCRAPED - 2/5

FETCHING - https://old.reddit.com/r/cardano/comments/ltkbwe/86_decentralized_with_all_the_good_news_we/
FOUND NON-TEXT THING

FETCHING - https://old.reddit.com/r/cardano/comments/ltkqwq/im_more_interested_in_seeing_this_number_going_up/
FOUND NON-TEXT THING

FETCHING - https://old.reddit.com/r/cardano/comments/ltkvkh/just_converted_my_eth_bnb_and_vet_to_ada/
SCRAPED - 3/5

FETCHING - https://old.reddit.com/r/cardano/comments/lti028/team_cardano_is_sending_shockwaves_worldwide/
SCRAPED - 4/5

FETCHING - https://old.reddit.com/r/cardano/comments/ltqtkq/dear_charles/
SCRAPED - 5/5


OUTPUT SAVED TO cardano.json

$ python3 reddit_scraper.py -h
usage: reddit_scraper.py [-h] [-c POSTS_COUNT] [-cf CACHE_FOLDER] [-pt POLITENESS_TIMEOUT] [-o OUTPUT_FILE] [-r] [-ks]
                         subreddit

positional arguments:
  subreddit             The subbredit to scrape

optional arguments:
  -h, --help            show this help message and exit
  -c POSTS_COUNT, --count POSTS_COUNT
  -cf CACHE_FOLDER, --cache-folder CACHE_FOLDER
  -pt POLITENESS_TIMEOUT, --politeness-timeout POLITENESS_TIMEOUT
  -o OUTPUT_FILE, --output OUTPUT_FILE
  -r, --refresh         Refreshes the main page of the subreddit
  -ks, --keep-stickied  Keep stickied posts
```
