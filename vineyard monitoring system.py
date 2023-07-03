import time
import bluetooth                       #-------> import bluetooth module
import RPi.GPIO as GPIO                # ------> Import GPIO module so that we can controll pins
import urllib.request
import Adafruit_DHT
import spidev
import os

#moisture setup
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
    
GPIO.setwarnings(False)                #-------> To disable warnings
GPIO.setmode(GPIO.BOARD)               #-------> GPIO pins scheme (here its set to physical board)

GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)              # ------↓
GPIO.setup(10, GPIO.OUT, initial=GPIO.LOW)             # ---->Declaring motor1 pins(8,10) as output and low at first

GPIO.setup(3, GPIO.OUT, initial=GPIO.LOW)              # -------↓
GPIO.setup(5, GPIO.OUT, initial=GPIO.LOW)              # ----->Declaring motor1 pins(8,5) as output and low at first


GPIO.setup(13, GPIO.OUT, initial=GPIO.LOW)             #------>Declaring buzzer pin 13 as output and low at start
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)             #--------> declaring pin 15(led pin) as output and low at first

# Set pin modes for servo and button
GPIO.setup(36, GPIO.OUT)                              #servo


# Create servo object
servo = GPIO.PWM(36, 50)  # 50 Hz (20 ms period)

# Define servo angles
angle_0 = 2.5  # 0 degrees
angle_90 = 7.5  # 90 degrees

# Move servo to 0 degrees
servo.start(angle_0)


a = 0                                  #----> varible for storing value 1 or 0 for our led to turn on or off

server_socket=bluetooth.BluetoothSocket(bluetooth.RFCOMM)              #-----> declaring our bluetooth server socket
port = 1                                                               #-----> a variable to store value of port
server_socket.bind(("",port))                                          #----> bindind port to our sever socket
server_socket.listen(1)                                                #------>make our bluetooth sever to listen for 1 connection at a time
client_socket,address = server_socket.accept()                         #----> accept connection from client and get the address
print ("Accepted connection from ",address)                            #------> print the bluetooth address of the connected client or the device 
def readChannel(channel):
    val = spi.xfer2([1,(8+channel)<<4,0])
    data = ((val[1]&3) << 8) + val[2]
    data = 1024 - data
    #print("data = ",data)
    data = (data)/750*100
    return data
def moisture():
    
    val = readChannel(0)
    if (val != 0):
        print("Moisture =",val,"%")
        #	time.sleep(2)
        
       #f=urllib.request.urlopen("https://api.thingspeak.com/update?api_key=AFNIVFIVC9KKPQZ1&field3=%s" % (val))
        #print(f.read())
        #f.close()
    
def DHT11() :
    humidity, temperature= Adafruit_DHT.read_retry(Adafruit_DHT.DHT11,27)
    print("humidity : ", humidity, "temp :", temperature)
    time.sleep(2)
    f=urllib.request.urlopen("https://api.thingspeak.com/update?api_key=AFNIVFIVC9KKPQZ1&field1=%s&field2=%s" % (humidity,temperature))
    print(f.read())
    f.close()

def left():                        
    print (" LEFT")    
    GPIO.output(8, GPIO.LOW)                   #-----> turning left
    GPIO.output(10, GPIO.HIGH)
    GPIO.output(3, GPIO.HIGH)
    GPIO.output(5, GPIO.LOW)

def right():
    print ("right")
    GPIO.output(8, GPIO.HIGH) 
    GPIO.output(10, GPIO.LOW)                  #-----> turning right  
    GPIO.output(3, GPIO.LOW)
    GPIO.output(5, GPIO.HIGH)

def forward():
    print ("FORWARD")
    GPIO.output(8, GPIO.HIGH)
    GPIO.output(10, GPIO.LOW)                   #-----> move forward
    GPIO.output(3, GPIO.HIGH)
    GPIO.output(5, GPIO.LOW)

def back():
    print ("BACKWARDS")
    GPIO.output(10, GPIO.HIGH)
    GPIO.output(8, GPIO.LOW)
    GPIO.output(5, GPIO.HIGH)                   #-----> move backwards
    GPIO.output(3, GPIO.LOW)

def stop():
    print ("STOP")
    GPIO.output(8, GPIO.LOW)
    GPIO.output(10, GPIO.LOW)                   #-----> stop
    GPIO.output(3, GPIO.LOW)
    GPIO.output(5, GPIO.LOW)
data=""
while True:                                  #------> run the below functions in loop 
    
    data= client_socket.recv(1024)           #-----> declaring variable "data" as the data received from the client 
    data = data.decode('UTF-8')              #-----> the data recieved will be in the form of byes 
    print ("Received: ", data)               #       so we will convert it into strings
    
    if (data == "F"):                        #----> if the data is f
        forward()                            #      then function forward
        
    elif (data == "L"):                      #----> if the data is L
        left()                               #      then function left
        
    elif (data == "R"):                      #----> if the data is R
        right()                              #      then function right
        
    elif (data == "B"):                      #----> if the data is B
        back()                               #      then function back
        
    elif (data == "s"):                      #----> if the data is s
        stop()                               #      then function stop
    elif (data == "read"):
        servo.ChangeDutyCycle(angle_90)        # Move servo to 90 degrees
        #code for Adc and read soil moisture
        DHT11()
        time.sleep(1)
        moisture()
        time.sleep(1)
        servo.ChangeDutyCycle(angle_0)# Move servo back to 0 degrees
        
    elif(data == "X"):                       #----> if the data is X
        GPIO.output(13, GPIO.HIGH)           #      then set buzzer pin 13 value high 
    elif(data == "x"):                       #----> if the data is x
        GPIO.output(13, GPIO.LOW)            #      then set buzzer pin 13 value low 
        
    elif (data == "l"):                      #----> if the data is L
         a+=1                                #      then increase value of variable a by 1
    if(a == 2):                              #----> if variable a value is 2 then set it back to zero
        a = 0                                #      then set  variable a to 0
    if(a == 1):                              #----->if 'a' value is 1 
        GPIO.output(15, GPIO.HIGH)           #      then set led pin 15 value to High to turn on the light
    if(a == 0):                              #----->if 'a' value is 0
        GPIO.output(15, GPIO.LOW)            #      then set led pin 15 value to LOW to turn off the light


#----------------------------------------------------End of The code =)-------]