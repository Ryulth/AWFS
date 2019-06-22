from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import base64

TOPIC='test'
 
def get_b64str_from_file(fpath):
    with open(fpath, 'rb') as imfile:
        s=str(base64.urlsafe_b64encode(imfile.read()))
    return s[2:-1]
def get_file_from_b64str(data):
    if len(data)%4:
        data += '='*(4-len(data)%4)
    img_based64_bytes=base64.urlsafe_b64decode(bytes(data,'utf-8'))
    f = open('savetest.jpg','wb') 
    f.write(img_based64_bytes)
    f.close()

MQTTClient=AWSIoTMQTTClient('finger_test')
MQTTClient.configureEndpoint('az6ybpcj57i7z-ats.iot.ap-northeast-2.amazonaws.com',8883)
MQTTClient.configureCredentials('AmazonRootCA1.pem','a7fdac8939-private.pem.key','a7fdac8939-certificate.pem.crt')
MQTTClient.connect()

for i in range(1):
    img_str=get_b64str_from_file('testfinger.jpg')
    print(len(img_str))
    #클라이언트 json 생성후 전송
    jsonobj=json.dumps({"room":"241-3", "hash":img_str})
    try:
        MQTTClient.publish(TOPIC,jsonobj,1)
        print(MQTTClient.onMessage('stse'))
        MQTTClient.unsubscribe(TOPIC)
    except:
        pass
    #json 받은 상태라고 생각 --서버단
    jsonget=json.loads(jsonobj)
    room=jsonget['room']
    data=jsonget['img']
    get_file_from_b64str(data)
MQTTClient.disconnect()