<div id="top"></div>


<h3 align="center">Portal eInk Calendar</h3>

  <p align="center">
    A small desk-calendar with the theme of a <a href="https://store.steampowered.com/app/620/Portal_2/">portal</a> chamber info.
    <br />
    It displays the current date, the next few events in your calendar and whether a person in your contact list has a birthday (inc. their name).
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#components">Components</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#frame">Frame</a></li>
    <li><a href="#questions">Questions</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
The finished project on my desk:

<img src="https://user-images.githubusercontent.com/12069002/150647924-80f5f8fa-098a-4592-b257-7ac27326abfb.jpg" height=500>
<img src="https://user-images.githubusercontent.com/12069002/150647951-48b0ee2c-e09c-45f7-ba01-4635f47f1a91.jpg" height=500>

The pie is displayed when a person in your contacts has a birthday (along with the name below it).
The other three icons are currently displayed randomly.



<p align="right">(<a href="#top">back to top</a>)</p>



### Components
This repo includes the software (100% python) and the STLs of the frame.

I used the following hardware:

* [Waveshare 800×480, 7.5inch E-Ink display (13505)](https://www.waveshare.com/product/displays/7.5inch-e-paper-hat-b.htm)
* [Raspberry Pi 3b](https://www.raspberrypi.com/products/raspberry-pi-3-model-b/)\
(The Raspi is a bit overkill if you only want to update the calendar. But since it's powered on anyways, I use it to host many other things as well. If you only want to use it for the calendar, you should take a look at the Raspberry Pi Zero series)
<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
The prerequisites are based on [this](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B)) waveshare instruction to get your rapi ready for the display:

* Enable the SPI interface on your raspi
  ```sh
  sudo raspi-config
  # Choose Interfacing Options -> SPI -> Yes  to enable SPI interface
  ```
* Install BCM2835 libraries
  ```sh
  wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
  tar zxvf bcm2835-1.60.tar.gz 
  cd bcm2835-1.60/
  sudo ./configure
  sudo make
  sudo make check
  sudo make install
  ```
* Install wiringPi libraries
  ```sh
  sudo apt-get install wiringpi
  
  #For Pi 4, you need to update it：
  cd /tmp
  wget https://project-downloads.drogon.net/wiringpi-latest.deb
  sudo dpkg -i wiringpi-latest.deb
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/13Bytes/eInkCalendar
   cd eInkCalendar
   ```
2. Install requirements
   ```sh
   sudo apt-get update
   # requirements by waveshare
   sudo apt-get install python3-pip python3-pil python3-numpy RPi.GPIO python-spidev
   # requirements by this repo
   sudo python3 -m pip install -r requirements.txt
   ```
3. Create config-file
   ```sh
   cp settings.py.sample settings.py
   ```
   Now edit `settings.py` and set all your settings:

   `LOCALE: "en_US"` (or e.g. `en-GB.UTF-8`) Select your desired format and language. It needs to be installed on your device (which 95% of time is already the case - as it's you system-language. If not, take a look at the [Debian Wiki](https://wiki.debian.org/Locale))
   
   `WEBDAV_CALENDAR_URL = "webcal://p32-caldav.icloud.com/published/2/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"` The address of your shared wabdav calendar. (It needs to be publicly accessible by this URL)
   
   `WEBDAV_IS_APPLE = True` Is the calendar hosted on icloud?
   
   `CALDAV_CONTACT_USER = "louis"` Username for logging into your CALDAV contact-list.
   
   `CALDAV_CONTACT_PWD = "secret"` Password for logging into your CALDAV contact-list.
   
   `ROTATE_IMAGE = True` This will rotate the image 180° before printing it to the calendar. `True` is required if you use my STL, as the dipay is mounted upside-down.



4. Add the start-script to your boot-process:\
   (You might need to adapt the path `/home/pi/eInkCalendar/run_calendar.sh` acordingly)

   Make `run_calendar.sh` executable
   ```sh
   chmod +x /home/pi/eInkCalendar/run_calendar.sh
   ``` 
   and add it to crontab, as follows:
   ```sh
   crontab -e
   ```
   and add following line:\
   ```@reboot sleep 60 && /home/pi/eInkCalendar/run_calendar.sh```\

<p align="right">(<a href="#top">back to top</a>)</p>



## Frame

The STLs of the frame can be found in [hardware](https://github.com/13Bytes/eInkCalendar/tree/main/hardware).
It's designed for 3D-printing.
The two parts can be screwed together in three of the four corners.

The raspi is held in place by threaded heat set inserts.


<img src="https://user-images.githubusercontent.com/12069002/150642718-5a24c717-1a19-4883-b932-1f1588f124fa.png" height=400>
<img src="https://user-images.githubusercontent.com/12069002/150642799-6145283c-6e35-43b8-842b-40c608fecd77.png" height=400>

<p align="right">(<a href="#top">back to top</a>)</p>


## Questions

Stuck somewhere? \
You can <a href="#contact">contact</a> me, or create a [issue](https://github.com/13Bytes/eInkCalendar/issues).

<p align="right">(<a href="#top">back to top</a>)</p>




<!-- CONTACT -->
## Contact

Louis - [@Louis_D_](https://twitter.com/Louis_D_) - coding@13bytes.de

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* I got the idea from following [reddit-post](https://www.reddit.com/r/RASPBERRY_PI_PROJECTS/comments/qujt3i/wip_portal_desktop_calendar/).
* This readme-page uses this [template](https://github.com/othneildrew/Best-README-Template).

<p align="right">(<a href="#top">back to top</a>)</p>
