#!/usr/bin/python
from multiprocessing import Process, Pipe
import time
import math
import smbus


debug = False

class PCA9685:

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("Reseting PCA9685")
    self.write(self.__MODE1, 0x00)
    
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
      print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
      
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
      print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
    
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print("Setting PWM frequency to %d Hz" % freq)
      print("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def reset(self):
    self.write(self.__MODE1, 0x80)
    if (self.debug):
      print("reset")

  def setPWM(self, channel,  on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
      print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))

class aelBot:

    def __init__(self):
        self.SENTINEL = 'SENTINEL'	
        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(200) 
        self.conn = []
        self.proc = []
        for num in range(0,16):    
            parent_conn, child_conn = Pipe()
            self.conn.append([parent_conn, child_conn])
            pr = Process(target=self.setMultiServoGradus, args=(child_conn,))
            self.proc.append(pr)
            pr.start()
			
    def write(self,cnct, data):
        cnct.send(data)
        cnct.send(self.SENTINEL)
    def get_pulse(self,grad):
        return int(grad)*(1600/200)+500
		
    def setMultiServoGradus(self,child_conn):
        while True:
            for msg in iter(child_conn.recv, self.SENTINEL):
#msg like [num,grad,old_grad,speed]
                num = int(msg[0])
                grad = int(msg[1])
                old_grad = int(msg[2])
                step_speed = float(msg[3])
                i = old_grad		
                if(old_grad>grad):
                    while i > int(grad):
                        pulse = self.get_pulse(i)
                        self.pwm.setPWM(int(num), 0, int(pulse))
                        time.sleep(0.01)
                        i -= step_speed				
                    if(i-int(grad) <= step_speed):
                        pulse = self.get_pulse(grad)                     
                        self.pwm.setPWM(int(num), 0, int(pulse))
                    print(num,pulse) 
                if(old_grad<grad):
                    while i < int(grad):
                        pulse = self.get_pulse(i)
                        self.pwm.setPWM(int(num), 0, int(pulse))
                        time.sleep(0.01)
                        i += step_speed				
                    if(int(grad)-i <= step_speed):
                        pulse = self.get_pulse(grad)                     
                        self.pwm.setPWM(int(num), 0, int(pulse))
                    print(num,pulse)
					
            self.write(child_conn, num)		
