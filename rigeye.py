import time
import operator
import atexit

import json
from bson import ObjectId

from flask import Flask, request, session, redirect, url_for, abort, render_template, flash, jsonify
app = Flask(__name__)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='admin888'
))
app.config.from_envvar('RIGEYE_SETTINGS', silent=True)

from pymongo import MongoClient
DATABASE_URL  = 'localhost'
DATABASE_PORT = 27017
client = MongoClient(host=DATABASE_URL, port=DATABASE_PORT)
db = client['rigeye']

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
scheduler = BackgroundScheduler()
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

def jsonifym(b):
	b['_id'] = str(b['_id'])
	return b

def check_instances_signal():
	instances = db.instances.find()
	for instance in instances:
		latest_data = db.data.find({ 'instance_id': str(instance['_id']) }).sort([('time', -1)]).limit(1)
		latest_data = latest_data.next()
		now = time.time()
		if now - latest_data['time'] >= 5 and instance['status'] != 'NOSIGNAL':
			db.instances.update_one({ '_id': instance['_id'] }, {
				'$set': {
					'status': 'NOSIGNAL'
				}
			}, True)
			db.events.insert({
				'level': 'danger',
				'title': 'Lose Instance Signal',
				'content': str(instance['_id']) + '.LOSE_SIGNAL',
				'createdAt': time.time()
			})
		elif now - latest_data['time'] < 5 and instance['status'] != 'MONITORING':
			db.instances.update_one({ '_id': instance['_id'] }, {
				'$set': {
					'status': 'MONITORING'
				}
			}, True)
			db.events.insert({
				'level': 'success',
				'title': 'Recatch Instance Signal',
				'content': str(instance['_id']) + '.RECACHE_SIGNAL',
				'createdAt': time.time()
			})

scheduler.add_job(
	func=check_instances_signal,
	trigger=IntervalTrigger(seconds=1),
	id='checking_job',
	name='Check signal from instances',
	replace_existing=True)

@app.route('/')
def index():
	pool = []
	for instance in db.instances.find():
		pool.append({'name': str(instance['_id']), 'data': sum([data['net_speed_r'] for data in db.data.find({ 'instance_id': str(instance['_id']) })])})
	pool.sort(key=operator.itemgetter('data'), reverse=True)
	for i in range(len(pool)):
		pool[i]['data'] = [pool[i]['data']]
	events_statistics = {
		'danger': db.events.find({ 'level': 'danger' }).count(),
		'success': db.events.find({ 'level': 'success' }).count()
	}
	print events_statistics
	return render_template('index.html', data_topn=pool[:5], events_statistics=events_statistics)

@app.route('/instances')
def list_instances():
	instances = [jsonifym(instance) for instance in db.instances.find()]
	return render_template('instances.html', instances=instances)

@app.route('/dashboard')
def dashboard():
	panels = [jsonifym(panel) for panel in db.panels.find()]
	return render_template('dashboard.html', panels=panels)

@app.route('/dashboard/add')
def add_panel():
	instances = [instance for instance in db.instances.find()]
	return render_template('add_panel.html', instances=instances)

@app.route('/dashboard/insert', methods=['POST'])
def insert_panel():
	db.panels.insert({
		'instance_id': request.form['instance_id'],
		'title': request.form['title'],
		'module': request.form['module']
	})
	return redirect(url_for('dashboard'))

@app.route('/dashboard/remove/<panel_id>')
def remove_panel(panel_id):
	db.panels.remove(ObjectId(panel_id))
	return redirect(url_for('dashboard'))

@app.route('/events')
def list_events():
	events = [event for event in db.events.find().sort([('createdAt', -1)])]
	return render_template('events.html', events=events)

# RESTful API

@app.route('/rest/add_data', methods=['POST'])
def add_data():
	data = request.json
	db.data.insert(data, w=1)
	return 'ok'

@app.route('/rest/add_info', methods=['POST'])
def add_info():
	info = request.json
	if info.has_key('token'):
		instance = db.instances.find_one(ObjectId(info['token']))
		if instance:
			return str(instance['_id'])
		else:
			info.pop('token')

	instance = db.instances.insert(info, w=1)
	db.events.insert({
		'level': 'success',
		'title': 'Catch New Instance Signal',
		'content': str(instance) + '.CACHE_SIGNAL'
	})
	return str(instance)

@app.route('/rest/get_latest_data/<instance_id>', methods=['GET'])
def get_latest_data(instance_id):
	data = db.data.find({ 'instance_id': instance_id }).sort([('time', -1)]).limit(1)
	if data.count():
		data = data.next()
		data = jsonifym(data)
		return jsonify(data)
	return 'err'

@app.route('/rest/get_60_data/<instance_id>/<module>', methods=['GET'])
def get_1min_data(instance_id, module):
	data = db.data.find({ 'instance_id': instance_id }).sort([('time', -1)]).limit(60)
	res = [[item['time']*1000, item[module]] for item in data]
	return jsonify(res[::-1])

@app.route('/rest/get_info/<instance_id>', methods=['GET'])
def get_info(instance_id):
	instance = db.instances.find_one({ '_id': ObjectId(instance_id) })
	instance['_id'] = str(instance['_id'])
	return jsonify(instance)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
