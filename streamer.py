from twython import Twython
from twython import TwythonStreamer
import json
import pprint
import re

def main():

    APP_KEY = "oH3BNSQlQEAk76sy5TZm884UK"
    APP_SECRET = "VVHkdw8L1iGtvWoAT1m1BFu2vm63N4CxfOgbjbHBb649vmnkn9"

    OAUTH_TOKEN = "859082520352223233-TYRf4TlpkXxdxVob37EeiCXDWtpxDEq"
    OAUTH_TOKEN_SECRET = "xMAve86tBx3iJPEHjhgPp5kdOutM2bITJrsWjIUgBM1rP"

    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    # List of JSON objects we will be using
    tweet_summaries = []

    # Top 50 trending in USA(WOEID: id=23424977)
    trending = twitter.get_place_trends(id=23424977)

    # Current highest trending
    # Using the first trend from trending. If you want to use second trending
    # ex: top trending = trending[0]['trends'][1]['name']
    top_trending = trending[0]['trends'][0]['name']

    def print_summary(summary):
        pprint.pprint(summary)

    # Streamer to track popular trends
    class MyStreamer(TwythonStreamer):
        def on_success(self, data):
            if 'text' in data:

                line = data['text']
                at = '@'
                colon = ':'
                # Extracts username from each response from streamer
                username = line[line.find(at)+1 : line.find(colon)]

                # limit to 1000-2000
                # sometimes connection breaks because we fall behind in getting the tweets (network related issue?)
                # Number of tweets surveyed is limited to 15 for now but you can change
                # len(username) < 15 is Twitter's max for username length
                if(username and at in line and colon in line and len(username) < 15 and len(tweet_summaries) < 15):
                    summary = {}
                    user_lookup = twitter.lookup_user(screen_name=username)
                    followers_count = user_lookup[0]['followers_count']
                    following_count = user_lookup[0]['friends_count']
                    ratio = followers_count / following_count
                    tweet = line[line.find(colon) + 2 : len(line)

                    summary['username'] = username
                    summary['followers_count'] = followers_count
                    summary['following_count'] = following_count
                    summary['ratio'] = ratio
                    if(re.search(r'http\S+', tweet)):
                        summary['hasLink'] = True
                        tweet = re.sub(r'http\S+', '', tweet)

                    else:
                        summary['hasLink'] = False
                    summary['tweet_content'] = tweet
                    summary['trend'] = top_trending
                    summary_json = json.dumps(summary)
                    tweet_summaries.append(summary_json)
                    # DEBUGGING STATEMENTS to see continuous tweets coming from streamer
                    #print(username)
                    #print(tweet)
                    #print(data['text'].encode('utf-8'))
                    #print(line[line.find(colon) + 2 : len(line)])
                    #print(followers_count)
                    #print(following_count)
                    #print(ratio)
                    #print(len(tweet_summaries))
                if(len(tweet_summaries) == 15):
                    # Instead of printing, I guess you start using tweet_summaries here in a different function
                    print_summary(tweet_summaries)
                    streamer.disconnect()


        def on_error(self, status_code, data):
            print(status_code)
            self.disconnect()


    streamer = MyStreamer(APP_KEY, APP_SECRET,
                        OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    # Get top trending hashtag and start streamer
    streamer.statuses.filter(track=top_trending)

main()
