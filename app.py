from flask import Flask, request, send_file, render_template, redirect, url_for
import requests
from io import BytesIO
import simplejson as json
from google.cloud import storage
import uuid 
from datetime import datetime

from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory

from src.predict import Model
import os


cloud_config = {
        'secure_connect_bundle': 'secure-connect-hackcambridge.zip'
}

auth_provider = PlainTextAuthProvider('clara', 'helloclara')
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect('dataspace')

app = Flask(__name__)

model_path = './models/resnet50.pkl'
model = Model(model_path)

# you can set key as config

# Initialize the extension
GoogleMaps(app,key='AIzaSyAj9mcBERAIP8uLtCIO4lBmeEnfkBMjEhA')

@app.route('/')
def hello_world():
    return render_template('index.html',)

@app.route('/file')
def hello_file():
        # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('file.html', mymap=mymap, sndmap=sndmap)

# sample request: http://127.0.0.1:5000/street_view?lat=46.414382&lon=10.013988
@app.route("/street_view")
def street_view():
    latitude = request.args.get("lat")
    longitude = request.args.get("lon")
    payload = {'size': '600x300', 'location': f'{latitude},{longitude}', 'key': os.getenv('GOOGLE_API_KEY')}
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

    # returns a public url
    print(blob.public_url)
    return blob.public_url

#TODO send image to AI model
@app.route("/send_image", methods=['POST'])
def bird_capture():
    print(request)
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
    # if image.is_hostile_arch():
        # cassandra execute
    session.execute("""INSERT INTO dataspace.hostile_arch (image_id, latitude, longitude, timestamp, user_id) 
                    VALUES (%s, %s, %s,%s, 'admin')""", (img_id, float(lat), float(lon), now))
    return redirect(url_for('index'))

@app.route("/img_id_creator")
def id_generator():
    img_id=str(uuid.uuid4())
    return img_id

@app.route("/hostile_data")
def go_cassandra():
    session.row_factory = dict_factory
    rows = session.execute("select image_id, user_id, latitude, longitude from hostile_arch").all()
    #take into account url for image downlad is https://storage.googleapis.com/hostile-images and the id
    print(rows)
    if rows:
        print(rows)
    else:
        print("An error occurred.")
    return json.dumps({"rows":rows})


@app.route("/predict", methods=['POST'])
def predict():
    """
    returns 'hostile' or 'friendly' as a string
    """
    prediction = model.predict_single_image(request.files['image'].read())
    print(prediction[0])
    return prediction[0]

if __name__ == "__main__":
    app.run(host = '127.0.0.1', port = 8080, debug=True)