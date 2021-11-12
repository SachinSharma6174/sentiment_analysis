#
# Worker server
#
import pickle
import jsonpickle
import platform
import io
import os
import sys
import pika
import redis
import hashlib
import json
import requests


from flair.data import Sentence

from flair.models import TextClassifier
classifier = TextClassifier.load('sentiment')

hostname = platform.node()

##
## Configure test vs. production
##
#redisHost = os.getenv("REDIS_HOST") or "localhost"
#rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
redisHost='10.1.0.15'
rabbitMQHost='10.1.0.19'

print(f"Connecting to rabbitmq({rabbitMQHost}) and redis({redisHost})")

##
## Set up redis connections
##
db = redis.Redis(host=redisHost)                                                                           

##
## Set up rabbitmq connection
##
rabbitMQ = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

# rabbitMQChannel.queue_declare(queue='toWorker')
# rabbitMQChannel.exchange_declare(exchange='logs', exchange_type='topic')
infoKey = f"{platform.node()}.worker.info"
debugKey = f"{platform.node()}.worker.debug"


def callback(ch, method, properties, body):
    print("Received %r" % body.decode())
    req = eval(body.decode())
    print(req)
    model = req['model']
    sentences = req['sentences']
    # sentence_dict = {}

    for sentence in sentences:

        if not db.exists(sentence):
            sentence_to_predict = Sentence(sentence)
            classifier.predict(sentence_to_predict)
            print(sentence_to_predict.to_dict('sentiment'))
            db.set(sentence,str(sentence_to_predict.to_dict('sentiment')))   
            # sentence_dict[sentence] = sentence_to_predict.to_dict('sentiment')

    ch.basic_ack(delivery_tag = method.delivery_tag)


# rabbitMQChannel.basic_consume(queue='toWorker',auto_ack=false,on_message_callback=callback)
rabbitMQChannel.basic_consume(queue='toWorker',auto_ack=False ,on_message_callback=callback)
rabbitMQChannel.start_consuming()




def log_debug(message, key=debugKey):
    print("DEBUG:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)

def log_info(message, key=infoKey):
    print("INFO:", message, file=sys.stdout)
    rabbitMQChannel.basic_publish(
        exchange='logs', routing_key=key, body=message)


##
## Your code goes here...
##