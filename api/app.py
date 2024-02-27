from flask import Flask, request, jsonify, abort, make_response
from flask_apscheduler import APScheduler
from functools import wraps
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge
import redis
import logging
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, x-api-key'
    header['Access-Control-Allow-Methods'] = '*'
    return response

r = redis.Redis(host='redis', port=6379, db=0)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.3')

queue_size = Gauge('queue_size', 'Number of messages in the queue')
redis_health = Gauge('redis_health', 'Health status of Redis')

class Config(object):
    JOBS = [
        {
            'id': 'update_metrics',
            'func': 'app:update_metrics',
            'trigger': 'interval',
            'seconds': 5
        }
    ]

app.config.from_object(Config())

def update_metrics():
    try:
        r.ping()
        redis_health.set(1)  # Redis is online
    except redis.exceptions.ConnectionError:
        redis_health.set(0)  # Redis is offline
    queue_size.set(r.llen('queue'))  # Update queue size metric

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# API_KEYS = {
#     "admin": "your-api-key"
# }

API_KEYS = {
    "admin": config.get('API', 'Key')
}

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') in API_KEYS.values():
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function

@app.route('/api/queue/pop', methods=['POST'])
@require_api_key
@metrics.counter('pop_invocations', 'Number of pop method invocations')
def pop():    
    n = int(request.json.get('n', 1))  # Convert n to an integer

    messages = []
    for _ in range(n):  # Batch pop
        message = r.lpop('queue')
        if message is None:
            break
        messages.append(message.decode('utf-8'))  # Decode bytes to string
    queue_size.set(r.llen('queue'))  # Update queue size metric
    if not messages:
        return jsonify({'status': 'error', 'message': 'No messages in queue'}), 400
    return jsonify({'status': 'ok', 'messages': messages})
    

@app.route('/api/queue/push', methods=['POST'])
@require_api_key
@metrics.counter('push_invocations', 'Number of push method invocations')
def push():    
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Missing JSON in request'}), 400
    messages = request.json.get('messages')
    if not messages:
        return jsonify({'status': 'error', 'message': 'Missing messages in request'}), 400
    for message in messages:  # Batch push
        r.rpush('queue', message)
    queue_size.set(r.llen('queue'))  # Update queue size metric
    return jsonify({'status': 'ok'})
    

@app.route('/api/health', methods=['GET'])
@metrics.counter('health_check_invocations', 'Number of health check method invocations')
def health_check():
    try:
        r.ping()
        redis_health.set(1)  # Redis is online
        return jsonify({'status': 'ok', 'redis': 'online'}), 200
    except redis.exceptions.ConnectionError:
        redis_health.set(0)  # Redis is offline
        return jsonify({'status': 'error', 'redis': 'offline'}), 500

@app.route('/api/queue/count', methods=['GET'])
@metrics.counter('count_invocations', 'Number of count method invocations')
@require_api_key
def count():
    queue_size.set(r.llen('queue'))  # Update queue size metric
    count = r.llen('queue')
    return jsonify({'status': 'ok', 'count': count})
    

if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.INFO)
    app.run(host="0.0.0.0", debug=True)
    
