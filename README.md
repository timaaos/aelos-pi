# aelos-pi
A Raspberry Pi modification for Aelos Bot
## Components:
- [Waveshare Servo Driver HAT](https://www.waveshare.com/wiki/Servo_Driver_HAT)
- [Raspberry Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero/)
- [Python 3.7](https://www.python.org/downloads/release/python-373/)
## Why we made this?
Be honest, Aelos software is bad. So we made custom software for Aelos Bot.
## How to use:
Run `main.py` to start websocket server.  
Connect via any websocket client and run commands.
### Commands:
- Set Motors Angle: `100 80 30 100 100 93 55 124 100 120 170 100 100 107 145 76` every number is angle for motor, be aware, first angle for 16th motor, second angle for 1st motor, third angle for 2nd motor and etc.
- Run Motion: `run MOTION_NAME` runs motion from `base_act.py`
