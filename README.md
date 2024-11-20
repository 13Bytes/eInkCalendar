<div id="top"></div>


<h3 align="center">Portal eInk Calendar</h3>

  <p align="center">
    A small battery powered desk-calenda with the theme of a <a href="https://store.steampowered.com/app/620/Portal_2/">portal</a> chamber info.
    <br />
    It displays the current date, the next few events from one or more calendars, the current weather, a rotating quote and whether a person in your contact list has a birthday (inc. their name).
    <br />
    
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

### Battery
The device will power itself on regularly (by default 6/6h but this can be changed on the  file `~/wittypi/schedule.wpi`) to update the screen and then shutdown, preserving battery life.

When battery is near depleting it will display a red empty battery icon on the upper left corner. On that state it will still power-up for a good number of cycles, but could be a good idea to charge the battery to preserve its health.

<p align="right">(<a href="#top">back to top</a>)</p>



### Components
This repo includes the software (100% python) and the STLs of the frame.

I used the following hardware:

* [Waveshare 800×480, 7.5inch E-Ink display (13505)](https://www.waveshare.com/product/displays/7.5inch-e-paper-hat-b.htm)
* [Raspberry Pi 3b](https://www.raspberrypi.com/products/raspberry-pi-3-model-b/)\
(The Raspi is a bit overkill if you only want to update the calendar. But since it's powered on anyways, I use it to host many other things as well. If you only want to use it for the calendar, you should take a look at the Raspberry Pi Zero series)

* [Witty Pi 4 L3V7](https://www.uugear.com/product/witty-pi-4-l3v7/)
* L3V7 Battery (Samsung inr18650-35e) and connectors, if needed, for the Witty Pi.
* [External panel button](https://www.amazon.es/dp/B09MBDMPDT) for for powering up and down.
* [External USB-C panel extension port](https://www.amazon.es/dp/B0D17K3CCY) for battery charging.


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
  wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.75.tar.gz
  tar zxvf bcm2835-1.75.tar.gz 
  cd bcm2835-1.75/
  sudo ./configure
  sudo make
  sudo make check
  sudo make install
  ```
*  sudo apt-get install openssl


* Install Witty Pi software
  
  See instructions on the [product description](https://www.uugear.com/product/witty-pi-4-l3v7/) or in the [manual](https://www.uugear.com/doc/WittyPi4L3V7_UserManual.pdf), also available in the hardware section of this repository.

  ```sh
  wget https://www.uugear.com/repo/WittyPi4/install.sh
  sudo sh install.sh
  ```

  This script will also install wiring pi so you can skip the next step.
  
  To update this software repeat these steps.
  
  **Note:** When assembling the hardware, the Raspberry pi would only boot, when both the Witty Pi and the e-Paper driver HAT are connected, after installing this software.


* Install wiringPi libraries
  They will allow the use of the `gpio` command, used all over the place by witty. The most current version can be found in the [github repo](https://github.com/WiringPi/WiringPi) in the [releases folder](https://github.com/WiringPi/WiringPi/releases).
  Download:
    ```sh
  cd /tmp
  wget [insert link to arm.deb file here eg: https://github.com/WiringPi/WiringPi/releases/download/3.8/wiringpi_3.8_arm64.deb]
  sudo dpkg -i wiringpi-[insert file version here].deb
  ```
  

* Install the locales
```sh
sudo dpkg-reconfigure locales
```
Make sure that later in settings the locale is one of the selected here (and include the .utf8 if is in the name).

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
   sudo apt-get install python3-pip python3-pil python3-numpy RPi.GPIO python3-spidev
   # requirements by this repo
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install -r requirements.txt
   #old: sudo python3 -m pip install -r requirements.txt
   ```
3. Create a config-file
   ```sh
   cp settings.py.sample settings.py
   ```
   Now edit `settings.py` and set all your settings:

- `LOCALE: "en_US"` (or e.g. `en-GB.UTF-8`) Select your desired format and language. 
   It needs to be installed on your device (which 95% of time is already the case - as it's you system-language). 
   You can list all installed local-packages with `locale -a`.
   If the desired one is missing, add it in this menu `sudo dpkg-reconfigure locales` (for Raspberry Pis) or take a look at the general [Debian Wiki](https://wiki.debian.org/Locale)). 
   Used for generate the text for the interface but also for selecting the holidays.

- `WEBDAV_CALENDAR_URLS The calendars to be displayed:
   ```python
    WEBDAV_CALENDAR_URLS = [
 	{
 	"url": "webcal://...",
 	"calendar_name": "a name",
 	"is_apple": True,
 	"pattern_fill": "DIAGONALSTRIPESUPPERRIGHT",
	"pattern_red_stripes": False
 	},
 	{
 	"url": "webcal://...2",
 	"calendar_name": "a name2",
 	"is_apple": True,
 	"pattern_fill": "VERTICALSTRIPES",
	"pattern_red_stripes": False
 	},
     ]
    ```

   Is a list of dicts, at least one must be filled, where the keys are:
	- `URL` is the URL for the calendar (should be public)
	- `calendar_name` is the name for displaying the calendar on the screen and
	- `is_apple` is to indicate that Apple iCal is the provider of the url (solves some issues).
	- `pattern_fill` can be BLACK, RED, VERTICALSTRIPES, HORIZONTALSTRIPES, DIAGONALSTRIPESLOWERRIGHT, DIAGONALSTRIPESUPPERRIGHT and will fill rectangle near the calendar appointments
	- `pattern_red_stripes` when true a red color will be used in the striped patterns instead of white
	
   
   

- `CALDAV_CONTACT_USER = "louis"` Username for logging into your CALDAV contact-list.
   
- `CALDAV_CONTACT_PWD = "secret"` Password for logging into your CALDAV contact-list.
   
- `APERTURE_DECORATIONS = True` Will show the aperture science decorations and logo. If false will hide them (and gain some space).

- `SHOW_QUOTES = True` Will show a random quote from [quotable.io](https://api.quotable.io).

- `ROTATE_IMAGE = True` This will rotate the image 180° before printing it to the calendar. `True` is required if you use my STL, as the dipay is mounted upside-down.

- `FIRST_WEEKDAY_IS_SUNDAY = True` Will start the week in sunday on the calendar if true. Otherwise it will be Monday.

- `TOMORROWIO_API_KEY = "[insert api key here]" For accessing the weather please go to (tomorrow.io)[https://tomorrow.io/] register for a free account and insert the key here. When empty or commented will make not show the weather.

- `WEATHER_LOCATION = "53.551086,9.993682"` Location for weather forecast. Empty or commented so to not showing the weather. A latitude-longitude pair of numbers according to ISO 6709, separated by , in query parameters. See also [tomorrow.io api formats](https://docs.tomorrow.io/reference/api-formats#locations). Note: This example is for Hamburg DE.

- `TEMPERATURE_UNIT = "C" ` Temperature Units (can be C for Celsius or F for Fahrenheit)

- `RECHARGE_VOlTAGE = 3.5 ` Voltage when the device will notify for a recharge in Volts. 3.5V is about 25% of charge for the battery that I'm using (samsung inr18650-35e), but this will change. Please see your battery datasheet.


4. Configure Witty Pi enviroment (settings and scripts). Use the `wittyPi.sh`:
	1. Configure the white blink light to disabled (to strong and repetitive).
	  
	2. Configure the Witty Pi so it won't boot when charging with `Auto-On when USB 5V is connected` to `No`. The default state of this device is off and it don't need to be power on to charge the battery:
	3. Also on these settings choose `Synchronize with network time`and `Write RTC time to system`.
    
	4. The software installs a webserver for configuring the Witty (the script ./wittyPi.sh seems to have the same functionality). The configuration for the server assumes that is installed in /home/pi/uwi, if not please change `~/uwi/uwi.conf`.
	
	Note that if  you don't want a "public" webserver without user access control you can **remove it** by running this command and restarting your device:
	```sh
	sudo update-rc.d -f uwi remove
	```


5. In the startup the witty pi script `afterStartup.sh` should run the `/home/<insert user here>/eInkCalendar/run_calendar_witty.sh` on the background with this line:
	 
```sh
/home/<insert user here>/eInkCalendar/run_calendar_witty.sh &
```
	
This will run the `run_calendar.sh` script and wait to shutdown the computer.
	
Please make sure that the commands on all those scripts have the correct paths. The PATH environment is not defined when they run so the full path must be used. Check the paths on your system with `whereis <command>`.

6. Add the line `/home/pi<or other username>/eInkCalendar/run_calendar_witty.sh &` to `~/wittypi/afterStartup.sh`. Note the use of the amperstand in the end of the line to not block the startup process.

7. The script `~/wittypi/runScript.sh` has a bug described [here](https://www.uugear.com/forums/technial-support-discussion/locked-witty-pi-after-rescheduling-and-shutdown-on-slower-systems/), that can crash the system when shutting down on some slower systems. The fiz is described on the post. Also a fixed script is in the [Witty Pi folder](/hardware/Witty%20Pi%204%20L3V7/).

7. Create or change the `~/wittypi/schedule.wpi` and run `~/wittypi/runScript.sh`. This will create the schedule of startup and shutdown for screen refreshing. Use the file in schedule.wpi in the [Witty Pi folder](/hardware/Witty%20Pi%204%20L3V7/) or copy this:

```sh
BEGIN 2024-09-01 07:00:00
# Will not end (or at least in the following 40 years)
END   2064-09-01 07:15:00
#Will stay on 20 minutes (the displayRun.py has a timeout of 10 minutes for a network connection retry)
ON    M20
#Will startup in about 6 hours (H6) in production.
OFF   H5 M40
# For testing, allowing less time between boots, you can use the following line (after commenting the previous)
#OFF	M15
```

<p align="right">(<a href="#top">back to top</a>)</p>



## Frame

The STLs of the frame can be found in [hardware](https://github.com/13Bytes/eInkCalendar/tree/main/hardware).
It's designed for 3D-printing.
The two parts can be screwed together in three of the four corners.

The raspi is held in place by threaded heat set inserts (M2.5).


<img src="https://user-images.githubusercontent.com/12069002/150642718-5a24c717-1a19-4883-b932-1f1588f124fa.png" height=400>
<img src="https://user-images.githubusercontent.com/12069002/150642799-6145283c-6e35-43b8-842b-40c608fecd77.png" height=400>

<p align="right">(<a href="#top">back to top</a>)</p>


## Questions

### The battery was dead and now the screen doesn't refresh, what can I do?
The clock is out of sync. Run the `wittyPi.sh`script, Synchronize with network time`, and `Write RTC time to system`.

### It doens't boot?
Witty Pi sometimes can crash on shutdown, especially after a RTC reset. You must try to disconnect it from its power sources: the USB cable and the battery. Then try to restart the pi.


Stuck somewhere? \
You can <a href="#contact">contact</a> me, or create a [issue](https://github.com/13Bytes/eInkCalendar/issues).

<p align="right">(<a href="#top">back to top</a>)</p>




<!-- CONTACT -->
## Contact
Original Idea and Design:
Louis - [@Louis_D_](https://twitter.com/Louis_D_) - coding@13bytes.de

Original Idea and Design:
João - @joao - coding@colaco.me

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* I got the idea from following [reddit-post](https://www.reddit.com/r/RASPBERRY_PI_PROJECTS/comments/qujt3i/wip_portal_desktop_calendar/).
* This readme-page uses this [template](https://github.com/othneildrew/Best-README-Template).

<p align="right">(<a href="#top">back to top</a>)</p>
