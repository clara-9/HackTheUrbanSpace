from flask import Flask, request, send_file
import requests
from io import BytesIO
from google.cloud import storage
import uuid 
from datetime import datetime

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory

cloud_config= {
        'secure_connect_bundle': 'secure-connect-hackcambridge.zip'
}

auth_provider = PlainTextAuthProvider('clara', 'helloclara')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect('dataspace')


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
    lat=request.args.get("lat")
    lon=request.args.get("lon")
    print(file)
    path=os.path.join("/tmp/", file.name)
    file.save(path)
    img_id=id_generator()
    image_url=upload_to_bucket(img_id, path)
    now = datetime.now()
    print(now)
    session.execute("""INSERT INTO dataspace.hostile_arch (image_id, latitude, longitude, timestamp, user_id) 
                    VALUES (%s, %s, %s,%s, 'admin')""", (img_id, float(lat), float(lon), now))
    return img_id

@app.route("/img_id_creator")
def id_generator():
    img_id=str(uuid.uuid4())
    return img_id

@app.route("/hostile_data")
def go_cassandra():
    session.row_factory = dict_factory
    rows = session.execute("select * from hostile_arch").all()
    #take into account url for image downlad is https://storage.googleapis.com/hostile-images and the id
    print(rows)
    if rows:
        print(rows)
    else:
        print("An error occurred.")
    return {"rows":rows}

        

if __name__ == "__main__":
    app.run(host = '127.0.0.1', port = 8080, debug=True)