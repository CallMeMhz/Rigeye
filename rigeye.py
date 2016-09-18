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
db = pymongo.MongoClient(host=DATABASE_URL, port=DATABASE_PORT)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/instances')
def list_instances():
	instances = [{
		'node': 'GHOST',
		'os': 'Linux',
		'status': 'MONITORING',
		'cpu_percent': 30,
		'iowait': 12,
		'load15': 0.91,
	},
	{
		'node': 'GHOST2',
		'os': 'Linux',
		'status': 'NOSIGNAL',
		'cpu_percent': 0,
		'iowait': 0,
		'load15': 0,
	}, ]
	return render_template('instances.html', instances=instances)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)