#!/usr/bin/python
# -*- coding: utf-8 -*-

## Basic libraries
import sys, time, math, struct


##############################
## PWM signal
from RPIO import PWM 
PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
pwm = PWM.Servo(pulse_incr_us=1)
## Brushless motors
pinPropLft = 27
pinPropRgt = 22
## Relay signal input
pinRlyLft1 = 12
pinRlyLft2 = 13
pinRlyRgt1 = 5
pinRlyRgt2 = 6
## Initialize
pwm.set_servo(pinPropLft, 1000)
time.sleep(1)
pwm.set_servo(pinPropRgt, 1000)
time.sleep(1)

  

##############################
## Step motor
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
## pins
pinStp = 21
pinDir = 20
pinSlp = 26
#3 setup pin as out & initialize as low level 
GPIO.setup(pinStp, GPIO.OUT, initial=0)
GPIO.setup(pinDir, GPIO.OUT, initial=0)
GPIO.setup(pinSlp, GPIO.OUT, initial=0)
## Function for step motor
def stepMotor(step):
    GPIO.output(pinSlp, 1) ## wakeup
    time.sleep(0.1)
    # Direction
    if step < 0:
        GPIO.output(pinDir, 0)
    else:
        GPIO.output(pinDir, 1)
    # step
    for i in range(1, int(abs(step) * 1.8 *100)):
        GPIO.output(pinStp, 1)
        GPIO.output(pinStp, 0)
        time.sleep(0.0001)
    GPIO.output(pinSlp, 0) ## sleep
    return


#############################
## LED light
pinLED = 19
GPIO.setup(pinLED, GPIO.OUT, initial=1) ## Low level will trigger the relay   
GPIO.output(pinLED, 0)
time.sleep(1)
GPIO.output(pinLED, 1)
    
    

##############################
## For reading sensor data
import time, threading, smbus, ctypes
from shutil import copyfile
from MS5803  import MS5803
from BMP280  import BMP280
from MPU9250 import MPU9250

## BMP280
def readBMP280():
    thread = threading.currentThread() 
    bmp280 = BMP280()
    while getattr(thread, "do_run", True):
        thread.data =  bmp280.readAll()
        thread.mbar = thread.data['mbar']
        thread.temp = thread.data['temp']
        with open("/dev/shm/mjpeg/sensor_rov_pres.html", "w") as f:
            f.write("ROV pressure: " + str(int(thread.mbar)))
            f.close()
        copyfile("/dev/shm/mjpeg/sensor_rov_pres.html", "/var/www/js/sensor_rov_pres.html")
        with open("/dev/shm/mjpeg/sensor_rov_temp.html", "w") as f:
            f.write("ROV temperature: " + str(int(thread.temp)))
            f.close()
        copyfile("/dev/shm/mjpeg/sensor_rov_temp.html", "/var/www/js/sensor_rov_temp.html")
        time.sleep(0.5)

tReadBMP280 = threading.Thread(target=readBMP280)
tReadBMP280.start()
# tReadBMP280.do_run = False

# MPU9250
def readMPU9250():
    thread = threading.currentThread() 
    mpu9250 = MPU9250()
    while getattr(thread, "do_run", True):
        thread.data =  mpu9250.readMagnet()
        with open("/dev/shm/mjpeg/sensor_rov_heading.html", "w") as f:
            f.write("ROV heading: " + str(int(thread.data)))
            f.close()
        copyfile("/dev/shm/mjpeg/sensor_rov_heading.html", "/var/www/js/sensor_rov_heading.html")
        time.sleep(0.5)

tReadMPU9250 = threading.Thread(target=readMPU9250)
tReadMPU9250.start()
# tReadMPU9250.do_run = False

# MS5803
def readMS5803():
    thread = threading.currentThread()   
    ms5803 = MS5803() 
    while getattr(thread, "do_run", True):
        thread.data = ms5803.read()
        thread.mbar = thread.data['mbar']
        thread.temp = thread.data['temp']
        with open("/dev/shm/mjpeg/sensor_water_pres.html", "w") as f:
            f.write("Water pressure: " + str(int(thread.mbar)))
            f.close()
        copyfile("/dev/shm/mjpeg/sensor_water_pres.html", "/var/www/js/sensor_water_pres.html")
        with open("/dev/shm/mjpeg/sensor_water_temp.html", "w") as f:
            f.write("Water temperature: " + str(int(thread.temp)))
            f.close()
        copyfile("/dev/shm/mjpeg/sensor_water_temp.html", "/var/www/js/sensor_water_temp.html")
        time.sleep(0.5)

tReadMS5803 = threading.Thread(target=readMS5803)
tReadMS5803.start()
# tReadMS5803.do_run = False



#####################################
## preview.html
import time, re, subprocess
## template
template = """
<html>
    <head>
        <title>ecoROV preview</title>
        <style>
            {style}
        </style>
    </head>
    <body>
        <a class="menu-item" style="float: right;" href="/index.html"><h2>HOME</h2></a>
        <br>{disk}<br><br>
        {img_grid}
    </body>
</html>
"""
css = """
    .floated_img{float: left; margin: 10px;}
    .thumb{width: 256px;}  
    """
img_blk = """
        <div class="floated_img">
            <a target="_blank" href="{doc_org}"><img src="{img_th}" class="thumb"></a>
            <p>{doc_name}</p>
        </div> 
        """
def update_preview():
    df_Disk  = re.sub(r"/dev/root *| /\n","", subprocess.check_output("df -h | grep root", shell=True))
    df_disk  = re.split(" +", df_Disk)
    df_used  = "Total size: <b>%s</b>; Used: <b>%s</b>; Available: <b>%s</b>; Percentage: <b>%s</b>;"  % tuple(df_disk)
    img_ths  = subprocess.check_output("cd /var/www/ && find media -type f -name *.th.jpg", shell=True).split('\n')[:-1]
    img_ths.sort(reverse = True)
    doc_orgs = [re.sub(r'\..{5}\.th\.jpg$', "", img) for img in img_ths]
    img_blks = [img_blk.format(img_th = img_ths[i], doc_org = doc_orgs[i], doc_name = re.sub(r'^media/', "", doc_orgs[i])) for i in range(len(img_ths))]
    pag_html = template.format(style = css, disk = df_used, img_grid = ''.join(img_blks))
    with open("/var/www/preview.html", "w") as f:
        f.write(pag_html)
        f.close()      
## Initialize
update_preview()        
# update_preview
def updatePreview():
    thread = threading.currentThread()   
    state_init = subprocess.check_output("cd /var/www/ && find media -type f -name *.th.jpg", shell=True).split('\n')[:-1]
    while getattr(thread, "do_run", True):
        state_now = subprocess.check_output("cd /var/www/ && find media -type f -name *.th.jpg", shell=True).split('\n')[:-1]
        if state_now != state_init:
            state_init = state_now
            update_preview()
        time.sleep(2)
## Start
tUpdatePreview = threading.Thread(target=updatePreview)
tUpdatePreview.start()
# tUpdatePreview.do_run = False




#####################################
## Define camera control functions
def camera(cmd):
    with open("/var/www/FIFO", "w") as f:
        f.write(cmd)
        f.close()

        
########################################
## fastcgi-python server
from flup.server.fcgi import WSGIServer 
import urlparse
## app
def app(environ, start_response):
  start_response("200 OK", [("Content-Type", "text/html")])
  Q = urlparse.parse_qs(environ["QUERY_STRING"])
  yield ('&nbsp;') # flup expects a string to be returned from this function
  if "cam" in Q:
    camera(Q["cam"][0])

WSGIServer(app).run()