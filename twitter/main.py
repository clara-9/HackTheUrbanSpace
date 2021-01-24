import tweepy

consumer_key= 'zkE1Zp1iUixmXpXyzSBsMaU6f'
consumer_secret='PiiQ6a0cVMliuIz4XTWgV7g0GX52ielbDq1yB3jCyYxtvt40Ez'
access_token='1353209823911956481-JZoHTfPWue3dnSNN2FuFOOqau1TN0u'
access_token_secret='wKZjqN1aR13Hd07qa3LfM7ctHeC0FV8sCIzjKtd3Jatea'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

#api.update_status("Hack the urban space!")


api.update_with_media("static/img/1.jpg", status="Test")

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)
