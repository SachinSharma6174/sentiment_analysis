##
from flask import Flask, request, Response, jsonify
import platform
import io, os, sys
import pika, redis
import hashlib, requests
import jsonpickle
import json

app = Flask(__name__)

##
## Configure test vs. production
##
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

# print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

# redis = redis.Redis(
#      host= '10.106.190.124',
#      port= '6379')

redis = redis.Redis(
     host= redisHost,
     port= '6379')


# redis.set('mykey', 'Hello from Docker!')
# redis.set('This thing sucks','{"analysis":{"model":"sentiment","result":{"entities":[],"labels":[{"confidence":0.9999688863754272,"value":"NEGATIVE"}],"text":"This thing sucks"}},"sentence":"This thing sucks"}')
redis.set('I don\'t think this one exists','{"analysis":{"model":"sentiment","result":{"entities":[],"labels":[{"confidence":0.9999688863754272,"value":"NEGATIVE"}],"text":"I don\'t think this one exists"}},"sentence":"I don\'t think this one exists"}')
value = redis.get('mykey') 
print(value)


@app.route('/apiv1/analyze', methods=['POST'])
def analyze():
    r = request
    request_pickled = jsonpickle.encode(r.get_json())
    # convert the data to a PIL image type so we can extract dimensions
    try:
    	rabbitMQ = pika.BlockingConnection(
    		pika.ConnectionParameters(host=rabbitMQHost))
    	rabbitMQChannel = rabbitMQ.channel()
    	rabbitMQChannel.queue_declare(queue='toWorker')
    	rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
    	infoKey = f"{platform.node()}.worker.info"
    	debugKey = f"{platform.node()}.worker.debug"
    	# formattedJson = json.dumps(workerJson)
    	rabbitMQChannel.basic_publish(exchange='',routing_key='toWorker', body=request_pickled)
    	response = {
    		"action": "queued" 
        }
    except Exception as e:
        response = { "error": e }
        print(e)
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/cache/', methods=['GET'])
def cache():
    keys = redis.keys()
    value = []
    for key in keys:
    	value.append(redis.get(key).decode())

    # convert the data to a PIL image type so we can extract dimensions
    try:
        response = {
            'value' : value
            }
    except:
        response = { 'value' : 0}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/apiv1/sentiment/sentence', methods=['POST'])
def sentiment():
    r = request
    try:
    	req = r.get_json()
    	model = req['model']
    	data = req['sentences']
    	print(model)
    	print(data)
    	sentences=[]

    	for sentence in data:
    		if redis.exists(sentence):
    			sentences.append(redis.get(sentence).decode())

    	response = {
    		"model": "sentiment",
        	"sentences": sentences
  		 }    
    except Exception as e:
    	
        response = { 
        	"error" : "not analyzed yet :("
        }
        print(e)


    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/')
def hello_world():
	return "200 OK"
    # return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)

##
## Your code goes here..
##