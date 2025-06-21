import sys
import boto3
import pandas as pd
from io import StringIO

s3 = boto3.client('s3')
bucket = 'rawgamedata'

listOfObjects = s3.list_objects_v2(Bucket=bucket)

dflist = []

for obj in listOfObjects.get('Contents', []):
    key = obj['Key']
    if key.endswith('.csv'):
        csv = s3.get_object(Bucket=bucket, Key=key)
        body = csv['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(body))
        dflist.append(df)
        
combined_df = pd.concat(dflist, ignore_index=True)
print(combined_df.head())