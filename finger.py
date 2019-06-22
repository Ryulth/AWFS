from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import base64
import time
from pyfingerprint.pyfingerprint import PyFingerprint
#--------------------------------------
import smbus
import time
import hashlib
from ast import literal_eval
# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
res_flag=1
def customcallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    temp=message.payload.decode()
    temp=literal_eval(temp).replace("'",'"')
    temp=json.loads(temp)
    print(temp['state'])
    if temp['state'] == 0:
        lcd_init()
        lcd_string("DENIED",LCD_LINE_1)
        lcd_string("ONE MORE TIME",LCD_LINE_2)
    else:
        lcd_init()
        lcd_string(str(temp['state']),LCD_LINE_1)
        lcd_string("ACCESS",LCD_LINE_2)
    global res_flag
    res_flag=0
TOPIC='finger'

func=1
std_id='2013104068'
room="241-3"
MQTTClient=AWSIoTMQTTClient("finger_send")
MQTTClient.configureEndpoint("az6ybpcj57i7z-ats.iot.ap-northeast-2.amazonaws.com",8883)
MQTTClient.configureCredentials("Amazon_Root_CA1.pem","a7fdac8939-private.pem.key","a7fdac8939-certificate.pem.crt")
MQTTClient.connect()
user_hash=''
flag=1
lcd_init()
lcd_string("Waiting",LCD_LINE_1)
lcd_string("for finger...",LCD_LINE_2)
while(1):
    
    func=int(input("enter func:"))
    if func==1:
        std_id=input("enter id:")
        for i in range(0,5):
            print (str(i+1)+"times")
            lcd_init()
            lcd_string(str(i+1)+"times",LCD_LINE_1)
            lcd_string("For 5 times",LCD_LINE_2)
            time.sleep(2)
            try:
                f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

                if ( f.verifyPassword() == False ):
                    raise ValueError('The given fingerprint sensor password is wrong!')

            except Exception as e:
                print('The fingerprint sensor could not be initialized!')
                print('Exception message: ' + str(e))

            ## Gets some sensor information
            print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

            ## Tries to enroll new finger
            try:
                print('Waiting for finger...')
                lcd_init()
                lcd_string("Waiting",LCD_LINE_1)
                lcd_string("for finger...",LCD_LINE_2)
                while ( f.readImage() == False ):
                    pass
                ## Converts read image to characteristics and stores it in charbuffer 1
                f.convertImage(0x01)
                ## Checks if finger is already enrolled
                result = f.searchTemplate()
                positionNumber = result[0]
                lcd_init()
                lcd_string("Remove finger...",LCD_LINE_1)
                time.sleep(2)
                lcd_init()
                lcd_string("Wating",LCD_LINE_1)
                lcd_string("for same finger again...",LCD_LINE_2)
                print('Waiting for same finger again...')
                if ( positionNumber >= 0 ):
                    print('Template already exists at position #' + str(positionNumber))
                    continue
                ## Wait that finger is read again
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
                ## Saves template at new position number
                positionNumber = f.storeTemplate()
                print('Finger enrolled successfully!')
                print('New template position #' + str(positionNumber))
                characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')

                ## Hashes characteristics of template
                print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())
                user_hash=hashlib.sha256(characterics).hexdigest()
            except Exception as e:
                print('Operation failed!')
                print('Exception message: ' + str(e))
                continue
            jsonobj=json.dumps({"func":func,"id":std_id, "hash":user_hash,"row":positionNumber})
            try:
                MQTTClient.publish(TOPIC,jsonobj,1)
                MQTTClient.unsubscribe(TOPIC)
            except:
                pass
        lcd_init()
        lcd_string(std_id,LCD_LINE_1)
        lcd_string("Finger enrolled",LCD_LINE_2)
        time.sleep(2)
    if func==0: #attendace
        #while(flag):
        try:
            f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
                
            if ( f.verifyPassword() == False ):
                print('The given fingerprint sensor password is wrong!')
        except Exception as e:
            print('The fingerprint sensor could not be initialized!')
            print('Exception message: ' + str(e))
            continue
            ## Gets some sensor information
        print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))
        ## Tries to search the finger and calculate hash
        try:
            print('Waiting for finger...')
            lcd_init()
            lcd_string("Waiting",LCD_LINE_1)
            lcd_string("for finger...",LCD_LINE_2)
            ## Wait that finger is read
            while ( f.readImage() == False ):
                pass
            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)
            print(type(f))
            ## Searchs template
            result = f.searchTemplate()
            positionNumber = result[0]
            accuracyScore = result[1]
            if ( positionNumber == -1 ):
                print('No match found!')
                lcd_init()
                lcd_string("DENIED",LCD_LINE_1)
                lcd_string("ONE MORE TIME",LCD_LINE_2)
                continue
            else:
                print('Found template at position #' + str(positionNumber))
                print('The accuracy score is: ' + str(accuracyScore))
                ## Loads the found template to charbuffer 1
            f.loadTemplate(positionNumber, 0x01)
            ## Downloads the characteristics of template loaded in charbuffer 1
            characterics = str(f.downloadCharacteristics(0x01)).encode('utf-8')
            ## Hashes characteristics of template
            print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())
            user_hash=hashlib.sha256(characterics).hexdigest()
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
        jsonobj=json.dumps({"func":func,"room":room, "hash":user_hash,"row":positionNumber})
        try:
            MQTTClient.publish(TOPIC,jsonobj,1)
            MQTTClient.unsubscribe(TOPIC)
        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
        
        MQTTClient2=AWSIoTMQTTClient('finger_res')
        MQTTClient2.configureEndpoint('az6ybpcj57i7z-ats.iot.ap-northeast-2.amazonaws.com',8883)
        MQTTClient2.configureCredentials('Amazon_Root_CA1.pem','a7fdac8939-private.pem.key','a7fdac8939-certificate.pem.crt')
        MQTTClient2.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
        MQTTClient2.configureDrainingFrequency(2) # Draining: 2 Hz
        try:
            MQTTClient2.connect()
        except:
            MQTTClient2.unsubscribe(TOPIC+"/response")    
            MQTTClient2.connect()
        res_flag=1
        while(res_flag):
            try:
                MQTTClient2.subscribe(TOPIC+"/response",1,customcallback)
            except:
                
                res_flag=0
                break
        
                
        
