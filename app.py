import requests
import json
import pandas as pd
import time
import os
import csv
import datetime
import tweepy  # https://github.com/tweepy/tweepy
import os
from youtube_transcript_api import YouTubeTranscriptApi
import textwrap
import csv
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# To set your environment variables in your terminal run the following line:
load_dotenv()  # take environment variables from .env.
bearer_token = os.getenv("BEARER_TOKEN")
username = "growbiz"

def find_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    response = requests.request("GET", url, auth=bearer_oauth)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    json_response = response.json()
    return json_response['data']['id']

def create_url(username):
    user_id = find_user_id(username)
    print(user_id)
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)

def get_params(next_token=None):
    params = {"tweet.fields": "created_at", "max_results": 100}
    if next_token:
        params['pagination_token'] = next_token
    return params

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def main(username):
    url = create_url(username)
    params = get_params()
    data = []

    response_counter = 0 

    while True:
        json_response = connect_to_endpoint(url, params)
        response_counter += 1

        if not json_response['data']:
            break
        
        for tweet in json_response['data']:
            data.append([tweet['created_at'], tweet['id'], tweet['text']])

        if 'next_token' not in json_response['meta']:
            break

        params = get_params(json_response['meta']['next_token'])

        if response_counter % 10 == 0:
            print("Taking a 15min break to comply with Twitter API Rate Limit...")
            time.sleep(60 * 15)  # sleep for 15 minutes

    df = pd.DataFrame(data, columns=["Created At", "ID", "Text"])

    df.to_csv('tweets_20.csv', index=False)

# The extract youtube transcripts function
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

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes

@app.route('/')
def home():
    return "Welcome to the home page!"

@app.route('/extract_tweets', methods=['POST'])
def extract_tweets():
    if 'username' not in request.json:
        return jsonify({'error': 'username not provided in request'}), 400

    username = request.json['username']

    main(username)

    tweets_data = pd.read_csv('tweets_20.csv').to_dict()
    return jsonify(tweets_data)

@app.route('/extract_tweets/download', methods=['GET'])
def download_tweets():
    return send_file('tweets_20.csv',
                     mimetype='text/csv',
                     attachment_filename='tweets_20.csv',
                     as_attachment=True)


@app.route('/extract_transcripts', methods=['POST'])
def extract_transcripts_endpoint():
    if 'video_urls' not in request.json:
        return jsonify({'error': 'video_urls not provided in request'}), 400

    video_urls = request.json['video_urls']

    extract_transcripts(video_urls)

    transcripts_data = pd.read_csv('youtube_transcripts.csv').to_dict()
    return jsonify(transcripts_data)

@app.route('/extract_transcripts/download', methods=['GET'])
def download_transcripts():
    return send_file('youtube_transcripts.csv',
                     mimetype='text/csv',
                     attachment_filename='youtube_transcripts.csv',
                     as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
