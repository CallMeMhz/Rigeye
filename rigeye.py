import json
from bson import ObjectId
from time import time
import pymongo
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='admin888'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

DATABASE_URL  = 'localhost'
DATABASE_PORT = 27017
client = pymongo.MongoClient(host=DATABASE_URL, port=DATABASE_PORT)
db = client['rigeye']

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/instances')
def list_instances():
	instances = [instance for instance in db.instances.find()]
	for i in range(len(instances)):
		instances[i]['_id'] = str(instances[i]['_id'])
	return render_template('instances.html', instances=instances)

@app.route('/dashboard')
def dashboard():
	panels = [panel for panel in db.panels.find()]
	for i in range(len(panels)):
		panels[i]['_id'] = str(panels[i]['_id'])
	return render_template('dashboard.html', panels=panels)

@app.route('/data/add_data', methods=['POST'])
def add_data():
	data = request.json
	db.data.insert(data, w=1)
	return 'ok'

@app.route('/data/add_info', methods=['POST'])
def add_info():
	info = request.json
	if info['token']:
		print info['token']
		instance = db.instances.find_one(ObjectId(info['token']))
		if instance:
			return str(instance['_id'])
		else:
			info.pop('token')

	instance = db.instances.insert(info, w=1)
	return str(instance)

@app.route('/data/get_data/<instance_id>', methods=['GET'])
def get_data(instance_id):
	data = db.data.find({ 'instance_id': instance_id }).sort([('time', -1)]).limit(1)
	data = data.next()
	data['_id'] = str(data['_id'])
	return json.dumps(data)

@app.route('/data/get_all_data/<instance_id>/<module>', methods=['GET'])
def get_all_data(instance_id, module):
	data = db.data.find({ 'instance_id': instance_id }).sort([('time', -1)]).limit(60)
	res = [[item['time']*1000, item[module]] for item in data]
	return json.dumps(res[::-1])

@app.route('/data/get_info/<instance_id>', methods=['GET'])
def get_info(instance_id):
	instance = db.instances.find_one({ '_id': ObjectId(instance_id) })
	instance['_id'] = str(instance['_id'])
	return json.dumps(instance)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)