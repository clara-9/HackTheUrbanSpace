from flask import Flask, request, send_file
import requests
from io import BytesIO
from google.cloud import storage
import uuid 

import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

# sample request: http://127.0.0.1:5000/street_view?lat=46.414382&lon=10.013988
@app.route("/street_view")
def street_view():
    latitude=request.args.get("lat")
    longitude=request.args.get("lon")
    payload = {'size': '600x300', 'location': f'{latitude},{longitude}', 'key':os.getenv('GOOGLE_API_KEY')}
    r = requests.get('https://maps.googleapis.com/maps/api/streetview', params=payload)
    i = BytesIO(r.content)
    return send_file(i, mimetype='image/jpeg')

@app.route("/bucket_upload", methods=['POST'])
def upload_to_bucket(img_name, path_to_file):
    """ Upload data to a bucket"""

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        'keys.json')

    bucket = storage_client.get_bucket('hostile-images')
    blob = bucket.blob(img_name)
    blob.upload_from_filename(path_to_file)

    #returns a public url
    print(blob.public_url)
    return blob.public_url


@app.route("/send_image", methods=['POST'])
def bird_capture():
    file=request.files['file']
    print(file)
    path=os.path.join("/tmp/", file.name)
    file.save(path)
    img_id=id_generator()+".jpg"
    image_url=upload_to_bucket(img_id, path)
    return img_id

@app.route("/img_id_creator")
def id_generator():
    img_id=str(uuid.uuid1())
    return img_id
