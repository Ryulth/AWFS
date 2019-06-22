from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import base64
from ast import literal_eval

def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    temp=message.payload.decode()
    temp=literal_eval(temp).replace("'",'"')
    temp=json.loads(temp)
    print(temp['state'])
    global res_flag
    res_flag=0
TOPIC='finger/response'

MQTTClient2=AWSIoTMQTTClient('finger_res')
MQTTClient2.configureEndpoint('az6ybpcj57i7z-ats.iot.ap-northeast-2.amazonaws.com',8883)
MQTTClient2.configureCredentials('AmazonRootCA1.pem','a7fdac8939-private.pem.key','a7fdac8939-certificate.pem.crt')
MQTTClient2.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
MQTTClient2.configureDrainingFrequency(2) # Draining: 2 Hz
MQTTClient2.configureConnectDisconnectTimeout(10) # 10 sec
MQTTClient2.configureMQTTOperationTimeout(20) # 5 sec
MQTTClient2.connect()
res_flag=1
while(res_flag):
    MQTTClient2.subscribe(TOPIC,1,customCallback)
 
