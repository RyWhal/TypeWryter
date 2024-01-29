# TypeWryter
TypeWryter is a terminal application designed for distraction free writing. It doesn't allow any fancy editing. You can write and you can backspace, thats it, preventing the urge to go back and edit. Files save once and minute and on escape. 
 
## Getting Started
1. Clone the repo. `git clone https://github.com/RyWhal/TypeWryter.git`
2. Run it with `python main.py`
3. ????
4. Write

## Known Issues
For more info on the current issues, see https://github.com/RyWhal/TypeWryter/issues

1. Unable to connect to wifi-networks*
2. Unable to connect to bluetooth devices*
3. When you try to escape (CTRL+E) from the networked file browser QR code, the whole app crashes. The networked file browser functions until you CTRL+E
4. This application is _NOT_ adapted to work with any E-Ink display yet. This will only run on a traditional terminal environment on a normal display right now (LCD, LED, IPS, etc.)

*note: This application is meant to act almost as the OS for my WriterDeck, FreeWrite, TypeWryter, whatever. The plan is for the Raspberry Pi to boot straight into this software when you turn it on. So the software needs to handle some of the things the OS would usually handle. These things that I cant do yet (wifi, bluetooth) only matter if you're not doing them ahead of time in the OS. 


## Browsing files on the local network
If you navigate to Settings --> File Manager --> Download Files: 
A local Flask webserver will spin up on whatever device is running TypeWryter (note the Flask package must be installed on your machine via `pip install Flask`)
TypeWryter will present you with a url and QR code. You can either visit the URL or Scan the QR code to see the files on your TypeWryter.


## Parts list for my device:
1. Raspberry Pi Zero 2W -  https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/
2. 4 inch E-ink display -  https://www.amazon.com/gp/product/B074NR1SW2
3. External battery - https://www.amazon.com/gp/product/B08D678XPR
4. Case - undecided

## Dependencies
I'm still building this section out, because honestly I dont remember everything I used. `Flask` is necessary for running the networked file browser, and `qrendcode` generates the QR codes where needed. 

Python Dependencies:
```
pip install Flask 
```

For the QR Code Generator
```
brew install qrencode
```

E-Paper Dependencies:
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
sudo apt install python3-gpiozero
```
