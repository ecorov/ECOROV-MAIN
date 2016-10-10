# python-setuptools contains easy_install which will be used for installing RPIO
# lighttpd is light weight web server
# python-flup is a python library contains FastCGI
# python-dev contain "Python.h"
# python-smbus for GPIO
sudo apt-get install -y git python-setuptools python-dev python-flup python-smbus lighttpd

# Install RPIO. RPi 3 has problem to instalL RPIO, the solution is using the following repository.
cd; git clone https://github.com/withr/RPIO-RPi3.git; cd RPIO-RPi3
sudo python setup.py install; cd; sudo rm -R RPIO-RPi3;

## Install ecorov 
cd; 
sudo rm -R *;  
sudo git clone https://github.com/withr/ecorov.git; cd ecorov; 

## INSTALL raspimjpeg
## raspimjpeg binary program;
sudo cp -r bin/raspimjpeg /opt/vc/bin/
sudo chmod 755 /opt/vc/bin/raspimjpeg
if [ ! -e /usr/bin/raspimjpeg ]; then
  sudo ln -s /opt/vc/bin/raspimjpeg /usr/bin/raspimjpeg
fi

## pipe for raspimjpeg to read command;
if [ ! -e /var/www/FIFO ]; then
  sudo mknod /var/www/FIFO p
fi
sudo chmod 666 /var/www/FIFO

## raspimjpeg config file;
sudo cp -r etc/raspimjpeg /etc/
sudo chmod 644 /etc/raspimjpeg

sudo cp -R www /var/www












if [ ! -e /usr/bin/pythonRoot ]; then
  sudo cp /usr/bin/python2.7 /usr/bin/pythonRoot
  sudo chmod u+s /usr/bin/pythonRoot
fi

if [ ! -e /etc/lighttpd/lighttpd.conf.bak ]; then
  sudo cp /etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf.bak
fi
sudo cp etc/lighttpd/* /var/www/ecorov
sudo chmod 755 /var/www/ecorov/*
sudo cat etc/lighttpd.conf /etc/lighttpd/lighttpd.conf






sudo killall raspimjpeg
sudo rm /var/www/*






## Automatically start when start RPi;
sudo cp -r etc/rc.local /etc/
sudo chmod 755 /etc/rc.local


## Install mjpeg-streamer
cd; sudo git clone https://github.com/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer-experimental/
sudo make
sudo make install


# cmake for install mjpeg-streamer
# libjpeg8-dev for install mjpeg-streamer
sudo apt-get install -y cmake libjpeg8-dev
export LD_LIBRARY_PATH=/home/pi/mjpg-streamer/mjpg-streamer-experimental/
sudo ln -s /home/pi/mjpg-streamer/mjpg-streamer-experimental/mjpg_streamer /usr/bin/mjpeg-streamer
mjpg_streamer -o "output_http.so -w ./www -p 8080" -i "input_raspicam.so -d 0.05"



## Start raspimjpeg;
sudo mkdir -p /dev/shm/mjpeg
sudo chmod 777 /dev/shm/mjpeg
sudo su -c 'raspimjpeg > /dev/null &' 
