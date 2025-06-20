import os
import time
import json
import logging
import requests
import math
import boto3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tempfile import mkdtemp

def lambda_handler(event, context):

    s3_client = boto3.resource('s3')
    for bucket in s3_client.buckets.all():
        print(bucket.name)


    chrome_options = ChromeOptions()
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')
    #chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1280,1696")
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    #chrome_options.add_argument("--single-process")
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome-usr-data")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")
    chrome_options.binary_location = os.getenv('CHROME_BIN', '/usr/bin/google-chrome')

    service = Service(
            executable_path=os.getenv('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver-linux64/chromedriver'),
            service_log_path="/tmp/chromedriver.log"
        )

    driver = webdriver.Chrome(options=chrome_options, service=service)

    driver.get('https://www.howlongtobeat.com')
    
    #Store source code in case of error for future debuging
    s3_client.Bucket("rawgamedata").put_object(Body=driver.page_source, Key="scraping_logs/page_source.html")

    #Find search box and select it to trigger first API call
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'site-search')))

    search_box.click()

    time.sleep(1)

    network_log = driver.get_log("performance")
    
    #Save networg log for debugging
    s3_client.Bucket("rawgamedata").put_object(Body=(bytes(json.dumps(network_log).encode('UTF-8'))), Key="scraping_logs/network_log.json")
    
    #NOTE: Below data is what I found to be the best way to find the network record of the API call
    #message.params.request.method: "POST" validate log is POST request
    #message.params.request.postData.searchType: "games" confirm that it's the request calling the api we want to scrape
    #message.params.request.url: url to access search api for first level scraping
   

    #This loop searches the network log for the api request and gathers data for a complete scrape
    for message in network_log:
        try:
            message_json = json.loads(message["message"])
            #print(message_json["message"]["params"]["request"]["method"])
            if(message_json["message"]["params"]["request"]["method"] == "POST"):
                postData_json = json.loads(message_json["message"]["params"]["request"]["postData"])
                if(postData_json["searchType"] == "games"):
                    api_url = message_json["message"]["params"]["request"]["url"]
        except (KeyError, TypeError, IndexError, ValueError):
            logging.info("not it")

    #Load necassary data for API requests
    s3_client = boto3.client('s3')
    file = s3_client.get_object(Bucket="rawgamedata", Key="scraping_data/api_cookies.json")
    cookies = json.load(file['Body'])
    
    file = s3_client.get_object(Bucket="rawgamedata", Key="scraping_data/api_headers.json")
    headers = json.load(file['Body'])

    file = s3_client.get_object(Bucket="rawgamedata", Key="scraping_data/api_search_json.json")
    json_data = json.load(file['Body'])

   

    #NOTE: Call API to test it and get results to gather the last few bits of info for scraping
    response = requests.post(api_url, headers=headers, json=json_data)
    
    js = response.json()

    
    page_count = js["pageTotal"]

    lambda_data = [{"page" : i, "api_url" : api_url} for i in range(1, page_count + 1)]
#    concurent_lambdas = 50
#    api_count_per_lambda = math.ceil(page_count / concurent_lambdas)
#    
#    lambda_data = {}
#    
#    #NOTE: Build JSON to create concurent cluster of lambdas to scrape site 
#    for i in range(0, concurent_lambdas):
#        start = 1 + (i * api_count_per_lambda)
#        end = (i + 1) * api_count_per_lambda if ((i + 1) * api_count_per_lambda) < page_count else page_count
#    
#        temp_search = {"cookies" : cookies, "headers" : headers, "json_data" : json_data, "api_url": api_url, "start": start, "end": end}
#        lambda_data[f"lambda_{i}"] = temp_search
    #NOTE:Store final data to launch lambda scraping cluster 
    s3_client.put_object(Bucket="rawgamedata", Key="scraping_data/lambda_data.json", Body=(bytes(json.dumps(lambda_data).encode('UTF-8'))))

