import requests
import json
import boto3
import time
import pandas as pd

def lambda_handler(event, context):
    #Load necassary data for API requests
    s3_client = boto3.client('s3')
    file = s3_client.get_object(Bucket="rawgamedata", Key="scraping_data/api_cookies.json")
    cookies = json.load(file['Body'])

    file = s3_client.get_object(Bucket="rawgamedata", Key="scraping_data/api_headers.json")
    headers = json.load(file['Body'])

    file = s3_client.get_object(Bucket="rawgamedata", Key="scraping_data/api_search_json.json")
    json_data = json.load(file['Body'])

    items = event["Items"]

    data = pd.DataFrame()

    
    for item in items:
        api_url = item["api_url"]
        json_data["searchPage"] = item["page"]
        multiplier = 1
        while multiplier <= 5:
            time.sleep(2 ** multiplier)
            response = requests.post(api_url, headers=headers, json=json_data)
            print(f"Status code: {response.status_code} sleep time: {2 ** multiplier}")
            if response.status_code == 200:
                js = response.json()
                temp_data = pd.DataFrame(js["data"])
                data = pd.concat([data, temp_data], ignore_index=True)
                break
            else:
                multiplier += 1

    s3_client.put_object(Bucket='rawgamedata', Key=f"howlongtobeat_{items[0]["page"]}_{items[-1]["page"]}.csv", Body=(data.to_csv(None, index=False)).encode('UTF-8'))

