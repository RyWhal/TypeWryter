# TypeWryter
TypeWryter is a terminal application designed for distraction free writing. It doesn't allow any fancy editing. You can write and you can backspace, thats it; preventing the urge to go back and edit. Files save on every carriage return.

This code is a heavily modified version of [zerowriter](https://github.com/zerowriter/zerowriter1/tree/main) since they had a very good head start on developing this sort of project. Their project is awesome, but is a little different and will have a somewhat different featureset.  
 
## Getting Started
1. Set up Raspberry Pi with Waveshare 4.1in epaper display - [More info available on Waveshare's Website](https://www.waveshare.com/wiki/4.2inch_e-Paper_Module_(B)_Manual#Overview)
2. Update apt: `sudo apt update`
3. Upgrade available packages: `sudo apt upgrade`
4. Update apt-get packages: `sudo apt-get update`
4.[Enable the SPI interface on your Raspberry Pi](https://www.waveshare.com/wiki/4.2inch_e-Paper_Module_(B)_Manual#Enable_SPI_Interface)
   * `sudo raspi-config`
   * Choose Interfacing Options -> SPI -> Yes Enable SPI interface
   * `sudo reboot now`
   * Check `/boot/config.txt`, and you can see 'dtparam=spi=on' was written in.
5. Install The following (E-Paper Dependencies):
```
sudo apt-get install python3-pip
sudo apt-get install python3-pil
sudo apt-get install python3-numpy
sudo pip3 install RPi.GPIO
sudo pip3 install spidev
sudo apt install python3-gpiozero
```
6. Install QRcode package: `sudo pip3 install qrcode`
7. Install Flask: `pip install Flask`
8. Clone this repo. `git clone https://github.com/RyWhal/TypeWryter.git`
9. Run it from the TypeWrytes directory with: `sudo python main.py`

Optional:
1. Install the Pi-Sugar tools, including battery monitor: `curl http://cdn.pisugar.com/release/pisugar-power-manager.sh | sudo bash`

# OS
I used Raspberry Pi OS (64-bit) Lite.
You can use whatever you want, but you may have to tweak minor things. 


## Known Issues and limitations

1. Unable to connect to wifi-networks from within the TypeWrytes application*
2. Unable to connect to bluetooth devices from within the TypeWrytes application*
4. Scrolling back in text history is not working.
5. You cant rename a writing session.

*note: This application is meant to act almost as the OS for my WriterDeck, FreeWrite, TypeWryter, whatever. The plan is for the Raspberry Pi to boot straight into this software when you turn it on. So the software needs to handle some of the things the OS would usually handle. These things that I cant do yet (wifi, bluetooth) only matter if you're not doing them ahead of time in the OS. 


## Browsing files on the local network
If you navigate to Menu --> Network File Browser --> Start Server
A local Flask webserver will spin up on whatever device is running TypeWryter (note the Flask package must be installed on your machine via `pip install Flask`)
TypeWryter will present you with a url, QR code, and  4 digit password. You can either visit the URL, or Scan the QR code,  and then enter the password to see the files on your TypeWryter.


## Parts list for my device:
1. Raspberry Pi Zero 2W -  https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/
2. 4 inch E-ink display -  https://www.amazon.com/gp/product/B074NR1SW2
3. External battery - https://www.amazon.com/gp/product/B08D678XPR
4. Case - undecided





