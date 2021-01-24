import os
import tempfile
import tweepy

from google.cloud import storage

consumer_key= 'zkE1Zp1iUixmXpXyzSBsMaU6f'
consumer_secret='PiiQ6a0cVMliuIz4XTWgV7g0GX52ielbDq1yB3jCyYxtvt40Ez'
access_token='1353209823911956481-JZoHTfPWue3dnSNN2FuFOOqau1TN0u'
access_token_secret='wKZjqN1aR13Hd07qa3LfM7ctHeC0FV8sCIzjKtd3Jatea'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

storage_client = storage.Client()

def blur_offensive_images(data, context):
    file_data = data

    file_name = file_data["name"]
    bucket_name = file_data["bucket"]

    blob = storage_client.bucket(bucket_name).get_blob(file_name)

    file_name = current_blob.name
    _, temp_local_filename = tempfile.mkstemp()

    api = tweepy.API(auth)

    api.update_with_media("temp_local_filename", status="Test")

    return
