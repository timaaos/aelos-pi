#!/usr/bin/python
from aelbot import aelBot
from base_act import base_act
from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer, SimpleSSLWebSocketServer
import socket
import signal
import sys
import time

defmotors = [100, 80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76]
motors = [100, 80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76]
old_motors = [101, 81, 31, 101, 101, 92, 54, 125, 101, 121, 171, 101, 101, 106, 144, 75]
speed = 1

class Server(WebSocket):

   def handleMessage(self):
      global old_motors
      global speed
      global proc
      stm=time.time()      
      dt = self.data[0:100]
      print(dt)
      dataarr = dt.split(" ")
      if len(dataarr) == 16:
          intdata = []
          for i in dataarr:
             intdata.append(int(i))
          old_motors = SetPosition(pi_val(intdata),old_motors,speed)
      elif len(dataarr) == 2: 
          if dataarr[0] == "speed":
            print("set speed",float(dataarr[1])/30)
            speed = float(dataarr[1])/15		  
          if dataarr[0] == "run":
            print("run",dataarr[1])
            play_cat(dataarr[1])		  
      elif len(dataarr) == 1: 
          if dataarr[0] == "exit":
              print("running exit()")
              signal.signal(signal.SIGINT, close_sig_handler)
              websock.serveforever()			  
		  
		  
      self.sendMessage('step time:'+str(time.time()-stm))

   def handleConnected(self):
      pass

   def handleClose(self):
      pass

def play_cat(act):
    lines = base_act[act].split("\n")
    global speed
    global old_motors	
    for line in lines:
#        print(line)
        if line.split(" ")[0]=="MOVE":
            motors = []
            motors.append(int(line.split(" ")[16],16))
            for i in range(1,16):
                motors.append(int(line.split(" ")[i],16))
            print("set motors:", motors)
            old_motors = SetPosition(pi_val(motors),old_motors,speed)
        if line.split(" ")[0]=="SPEED":		
            speed = float(int(line.split(" ")[1],16))/30	
            print("set speed:",speed)		
        if line.split(" ")[0]=="DELAY":		
            time.sleep(int(line.split(" ")[1]+line.split(" ")[2],16)/1000)	
            print("sleeped:",int(line.split(" ")[1]+line.split(" ")[2],16)/1000)
    DefPosition()
			
def pi_val(motors):

    new_motors = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in range(0,16):

# corrections to PI values	

        if i == 0:
            new_motors[i] = motors[i]+5
        elif i == 8:
            new_motors[i] = motors[i]-5
        elif i == 14:
            new_motors[i] = motors[i]+10
        elif i == 6:
            new_motors[i] = motors[i]-10
        else:			
            new_motors[i] = motors[i]

# base restrictions
			
        if new_motors[i] < 1:
            new_motors[i] = 1            		
        if new_motors[i] > 199:
            new_motors[i] = 199

        if i == 0:
            if new_motors[i]>150:
                new_motors[i]=150	
            if new_motors[i]<60:
                new_motors[i]=60	
        if i == 8:
            if new_motors[i]>140:
                new_motors[i]=140	
            if new_motors[i]<40:
                new_motors[i]=40	

        if i==4 and new_motors[i]>120:
            	new_motors[i]=120	
        if i==12 and new_motors[i]<70:
            	new_motors[i]=70	

        if i==5 and new_motors[i]>170:
            	new_motors[i]=170	
        if i==13 and new_motors[i]<20:
            	new_motors[i]=20	
			
        if i==6 and new_motors[i]>175:
            	new_motors[i]=175	
        if i==14 and new_motors[i]<25:
            	new_motors[i]=25	

        if i==7 and new_motors[i]<20:
            	new_motors[i]=20	
        if i==15 and new_motors[i]>180:
            	new_motors[i]=180	

    for i in range(0,16):
# advanced restrictions 
        if i == 1 and (new_motors[1]+new_motors[2])<60:
            new_motors[1] = 60 - new_motors[2]		
        if i == 9 and (new_motors[9]+new_motors[10])>340:
            new_motors[9] = 340 - new_motors[10]		
            print(new_motors[9],new_motors[10])

		
			
			
    print("m",motors)
    print("newm",new_motors)
    return new_motors
			
def parseFile(filename):
    global old_motors
    global speed
    lines = []
    file = open('motions/'+filename) 
    filestr = file.read()
    file.close()
    for linestr in filestr.split("\n"):
        if linestr.startswith("#"):
            continue
        elif linestr.startswith("use"):
            line = linestr.split(" ")
            includedline = parseFile(line[1])
            for i in includedline:
                lines.append(i)

        else:
            line = linestr.split(" ")
            intline = []
            i=0
            for n in line:
                if n == "xx":
                    lineind = filestr.split("\n").index(linestr)
                    n = lines[lineind-1][i]
                    intline.append(int(n))
                else:
                    intline.append(int(n))
                i=i+1
            lines.append(intline)
    return lines
  

def runMotion(name):
    global old_motors
    global debug
    ln=parseFile(name + '.motion')
    for line in ln:
        SetPosition(line,old_motors)
        old_motors=line

def DefPosition():
    global old_motors
    global speed
#    motors = parseFile('stand.motion')[0]
    SetPosition(pi_val(defmotors),old_motors,1)
    return motors
    
def seat():
    global old_motors
    global speed
    motors = [95,90,10,80,90,90,130,30,85,90,170,100,90,90,40,140]
    SetPosition(motors,old_motors,speed)
    return motors

def SetPosition(motors,old_motors,speed):
    i=0
    print(motors,old_motors,speed)
    chk = []
    for num in range(0,16):
        if(motors[num]==0):
	        motors[num]=old_motors[num]
        if(motors[num]!=old_motors[num] and motors[num]!=0):
            print(motors[num])
            robot.write(robot.conn[num][0],[num,motors[num],old_motors[num],speed])
            chk.append(num)			
            i=i+1
    y=0
    while True:
        for nm in chk:
            if robot.conn[nm][0].recv != None:
                for msg in iter(robot.conn[nm][0].recv, robot.SENTINEL):
                    y=y+1					
        if(i==y):
            break
    return motors
	
def close_sig_handler(signal, frame):
      global proc
      for num in range(0,16):	
          robot.proc[num].terminate()
      websock.close()
      sys.exit()
      exit()	  

if __name__=='__main__':
 
    robot = aelBot()
    print("start")
#    seat()
    DefPosition()
    websock = SimpleWebSocketServer('', 8000, Server)
    signal.signal(signal.SIGINT, close_sig_handler)
    websock.serveforever()
	
