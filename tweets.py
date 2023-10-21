import csv
import datetime
import tweepy  # https://github.com/tweepy/tweepy
import os
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap
import csv


# Sign up for the Twitter API and generate a Bearer Token here:
# https://developer.twitter.com/en/docs/twitter-api

TWITTER_BEARER_TOKEN = '''AAAAAAAAAAAAAAAAAAAAACHGqQEAAAAAcnQHe%2B%2FjfA7UPliYyClaDdjDSBk%3DBWnC93AcojSdnA03lTuYtqAZIYdzxE5MtnW7nBUuFxxi2SRMHy'''
username = "growbiz"


def get_tweets(username: str):
    """
    Pulls 3,200 (maximum allowed) most recent tweets for specified username and saves to tweets_<username>.csv
    """

    client = tweepy.Client(TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)
    user_id = client.get_user(username=username).data.id
    responses = tweepy.Paginator(client.get_users_tweets, user_id, max_results=100, limit=100)
    tweets_list = [["link", "username" "tweet"]]
    currentime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    counter = 0
    for response in responses:
        counter += 1
        print(f"==> processing {counter * 100} to {(counter + 1) * 100} of {username}'s tweets")
        try:
            for tweet in response.data:  # see any individual tweet by id at: twitter.com/anyuser/status/TWEET_ID_HERE
                tweets_list.append([f"https://twitter.com/anyuser/status/{tweet.id}", username, tweet.text])
        except Exception as e:
            print(e)

    with open(f"tweets_{username}_{currentime}.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(tweets_list)

    print("Done!")


def get_tweets(username: str):
    client = tweepy.Client(TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)
    user_id = client.get_user(username=username).data.id
    responses = tweepy.Paginator(client.get_users_tweets, user_id, max_results=100, limit=100)
    tweets_list = [["link", "username" "tweet"]]
    currentime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    counter = 0
    for response in responses:
        counter += 1
        print(f"==> processing {counter * 100} to {(counter + 1) * 100} of {username}'s tweets")
        try:
            for tweet in response.data.data if response.data is not None else []: 
                if not tweet.possibly_sensitive:  
                    tweets_list.append([f"https://twitter.com/anyuser/status/{tweet.id}", username, tweet.text])
        except Exception as e:
            print(f"Error in processing tweets {counter * 100} to {(counter + 1) * 100}: {e}")
            pass

    with open(f"tweets_{username}_{currentime}.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(tweets_list)

    print("Done!")


def extract_transcripts(video_urls): 
    def extract_video_id(video_id_or_url):
        # a youtube video id is 11 characters long
        # if the video id is longer than that, then it's a url
        if len(video_id_or_url) > 11:
            # it's a url
            # the video id is the last 11 characters
            return video_id_or_url[-11:]
        else:
            # it's a video id
            return video_id_or_url
    def get_transcript(video_url_or_id):
        try:
            video_id = extract_video_id(video_url_or_id)
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            print(f"Error: {e}")
            return None
    def format_transcript(transcript, max_line_width=80):
        formatted_transcript = ""
        wrapper = textwrap.TextWrapper(width=max_line_width)
        for entry in transcript:
            wrapped_text = wrapper.fill(text=entry['text'])
            formatted_transcript += wrapped_text + "\n\n"
        return formatted_transcript

    data = []
    for video_url in video_urls:
        transcript = get_transcript(video_url)
        if transcript:
            formatted_transcript = format_transcript(transcript)
            data.append([video_url, formatted_transcript])

    with open("youtube_transcripts.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Youtube Links", "Transcript"])
        writer.writerows(data)



            
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    get_tweets(username)
    # video_urls = ['https://www.youtube.com/watch?v=Rk_CGf1HcC8', 'https://www.youtube.com/watch?v=Na4kgcj5Jy4', 'https://www.youtube.com/watch?v=Yef5cMxW834']
    # extract_transcripts(video_urls)
