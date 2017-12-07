from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

from rigeye import db

# 初始化scheduler
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


# 检查实例是否丢失信号
def check_instances_signal():

    for instance in db.instances.find():

        latest_data = db.data.find({'instance_id': str(instance['_id'])})
        latest_data = latest_data.sort([('time', -1)]).limit(1)
        latest_data = latest_data.next()

        now = time.time()

        if now - latest_data['time'] >= 5 and instance['status'] != 'NOSIGNAL':

            db.instances.update_one({'_id': instance['_id']}, {
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

        elif (now - latest_data['time'] < 5 and instance['status'] != 'MONITORING'):

            db.instances.update_one({'_id': instance['_id']}, {
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


def load_jobs():
    scheduler.add_job(
        func=check_instances_signal,
        trigger=IntervalTrigger(seconds=1),
        id='checking_job',
        name='Check signal from instances',
        replace_existing=True
    )
