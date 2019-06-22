from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import base64
import time
from pyfingerprint.pyfingerprint import PyFingerprint
#--------------------------------------
import smbus
import time
import hashlib

TOPIC='test'
func=0
std_id='2013104068'
room="241-3"
MQTTClient=AWSIoTMQTTClient("finger_test")
MQTTClient.configureEndpoint("az6ybpcj57i7z-ats.iot.ap-northeast-2.amazonaws.com",8883)
MQTTClient.configureCredentials("Amazon_Root_CA1.pem","a7fdac8939-private.pem.key","a7fdac8939-certificate.pem.crt")
MQTTClient.connect()

user_hash='12312jsajf'
############

###########
#"room":"241-3",
if func==1: #new
    ## Enrolls new finger
##

## Tries to initialize the sensor
    for i in range(0,5):
        print (str(i+1)+"times")
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

            if ( f.verifyPassword() == False ):
                print('The given fingerprint sensor password is wrong!')

        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            
        ## Gets some sensor information
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

        ## Tries to enroll new finger
        try:
            print('Waiting for finger...')
            
            ## Wait that finger is read
          
            while ( f.readImage() == False ):
                pass
        
            f.convertImage(0x01)
            print('Remove finger...')
            time.sleep(2)
            print('Waiting for same finger again...')
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 2
            f.convertImage(0x02)
            ## Compares the charbuffers
            if ( f.compareCharacteristics() == 0 ):
                print('Fingers do not match')
                continue
            ## Creates a template
            f.createTemplate()
            print('Finger enrolled successfully!')
            characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
            ## Hashes characteristics of template
            print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())
            user_hash=hashlib.sha256(characterics).hexdigest()
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
        jsonobj=json.dumps({"func":func,"id":std_id, "hash":user_hash})
        try:
            MQTTClient.publish(TOPIC,jsonobj,1)
            MQTTClient.unsubscribe(TOPIC)
        except:
            pass
if func==0: #attendace
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            print('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
            


        ## Tries to enroll new finger
    try:
        print('Waiting for finger...')
        while ( f.readImage() == False ):
            pass
        f.convertImage(0x01)
        characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
        ## Hashes characteristics of template
        print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())
        user_hash=hashlib.sha256(characterics).hexdigest()
    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
    jsonobj=json.dumps({"func":func,"id":std_id, "hash":user_hash})
    try:
        MQTTClient.publish(TOPIC,jsonobj,1)
        MQTTClient.unsubscribe(TOPIC)
    except:
        pass
        
