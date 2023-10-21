import requests
import json
import pandas as pd
import time
import os

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='AAAAAAAAAAAAAAAAAAAAACHGqQEAAAAAH3l%2BlJ8AqwBjCKw83leN84FQJxw%3D2FdcSyni6gm9DmHteNclyIAqrozDnIDS3LWA5wn2KRLEMORp1i'
bearer_token = os.environ.get("BEARER_TOKEN")
bearer_token = "AAAAAAAAAAAAAAAAAAAAACHGqQEAAAAAH3l%2BlJ8AqwBjCKw83leN84FQJxw%3D2FdcSyni6gm9DmHteNclyIAqrozDnIDS3LWA5wn2KRLEMORp1i"


# def create_url():
#     user_id = 14622632
#     return "https://api.twitter.com/2/users/{}/tweets".format(user_id)
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

if __name__ == "__main__":
    main(username)