from flask import Flask, request, send_file
import requests
from PIL import Image
from io import BytesIO

import os

print(os.getenv('GOOGLE_API_KEY'))


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

# sample request: http://127.0.0.1:5000/street_view?lat=46.414382&lon=10.013988
@app.route("/street_view")
def species_human_response():
    latitude=request.args.get("lat")
    longitude=request.args.get("lon")
    payload = {'size': '600x300', 'location': f'{latitude},{longitude}', 'key':os.getenv('GOOGLE_API_KEY')}
    r = requests.get('https://maps.googleapis.com/maps/api/streetview', params=payload)
    i = BytesIO(r.content)
    return send_file(i, mimetype='image/jpeg')