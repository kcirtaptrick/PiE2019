import time
import os 
import sys
import json
from multiprocessing import Process

sys.path.insert(0, '/home/pi/.local/lib/python2.7/site-packages/')

import pigpio

gpio = pigpio.pi()

auto = {
    "recording": False,
    "path": [],
    "foot": 0.73469387748,
    "rotation": 2.45
}



motor = {
    "config": {
        "drive": 0.5,
        "lift": 1
    },
    "right": {
        "name": "right",
        "pins": [12, 16],
        "value": 0
    },
    "left": {
        "name": "left",
        "pins": [21, 20],
        "value": 0
    },
    "lift": {
        "name": "lift",
        "pins": [19, 26],
        "value": 0
    }
}

startTime = 0
switchID = "18851477588195929070"
switch0 = False
switch1 = False
switch2 = False
stop_down=1
stop_up=1
start_pos_up = 1
def setM(m, speed):
    global startTime
    global motor
    global auto
    if speed != motor[m["name"]]["value"]:
        motor[m["name"]]["value"] = speed
        if auto["recording"]:
            auto["path"].append({
                "time": time.time() - startTime,
                "motor": {
                    "name": motor[m["name"]]["name"],
                    "pins": motor[m["name"]]["pins"],
                    "value": speed
                }
            })
            print(auto["path"])
        if(speed >= 0):
            gpio.write(m["pins"][1], 0)
            gpio.set_PWM_dutycycle(m["pins"][0], 255 * speed)
        else:
            gpio.write(m["pins"][0], 0)
            gpio.set_PWM_dutycycle(m["pins"][1], 255 * -speed)
    # setM(motor, speed)
def resetMotors():
    for m in motor:
        if "pins" in m:
            gpio.write(m["pins"][0], 0)
            gpio.write(m["pins"][1], 0)

resetMotors()
def autonomous_setup():
    print("Autonomous mode has started!")
    Robot.run(autonomous_play)

def autonomous_main():
    pass
    
    
async def autonomous_actions():
    #Tells robot to move forward:
    Robot.run(autonomous_move())
async def autonomous_play():
    data = json.load(open('/home/pi/Autonomous/autonomous_data.json', 'r'))
    lastTime = 0
    startTime = time.time()
    path = data[len(data) - 1]
    while time.time() - startTime < path["time"]:
        for i in range(0, len(path["path"]) - 1):
            if(time.time() - startTime > path["path"][i]["time"] and time.time() - startTime < path["path"][i + 1]["time"]):
                setM(path["path"][i]["motor"], path["path"][i]["motor"]["value"])
                print("i: " + str(i) + ", " + path["path"][i]["motor"]["name"] + ": " + str(path["path"][i]["motor"]["value"]))
        # if(time.time() - startTime > path["path"][len(path["path"]) - 1]["time"]):
        #     setM(path["path"][len(path["path"])]["motor"], path["path"][len(path["path"])]["motor"]["value"])
            
async def auto_action(motor, time):
    setM(motor, motor["value"])
    await Actions.sleep(time)
    
async def autonomous_move():
    pass
    

def teleop_setup():
    print("Tele-operated mode has started!")

def teleop_main():
    global stop_up
    global stop_down
    global start_pos_up
    global auto
    global startTime
    global motor
    dup = Gamepad.get_value("dpad_up")
    ddown = Gamepad.get_value("dpad_down")
    dleft = Gamepad.get_value("dpad_left")
    dright = Gamepad.get_value("dpad_right")
    if Gamepad.get_value("button_start"):
        if not auto["recording"]:
            print("Recording")
            auto["recording"] = True
            startTime = time.time()
        else:
            print("Already recording")
    if Gamepad.get_value("button_back"):
        if auto["recording"]:
            print("Logging Record")
            auto["recording"] = False
            data = json.load(open('/home/pi/Autonomous/autonomous_data.json', 'r'))
            data.append({
                "Title": "Untitled",
                "time": time.time() - startTime,
                "path": auto["path"]
            })
            
            # print(json.dumps(data, indent=2))
            json.dump(data, open('/home/pi/Autonomous/autonomous_data.json', 'w'), indent=2)
        else:
            print("Not recording")
    if Gamepad.get_value("button_b"):
        data = []
        for i in range(0, 10):
            data.append({
                "test" + str(i): i
            })
        print(data)
    if Gamepad.get_value("r_bumper"):
        motor["config"]["drive"] = 1
    if Gamepad.get_value("l_bumper"):
        motor["config"]["drive"] = 0.5
    if dup:
        if dleft:
            setM(motor["left"], 0)
            setM(motor["right"], motor["config"]["drive"])
        elif dright:
            setM(motor["left"], motor["config"]["drive"])
            setM(motor["right"], 0)
        else:
            setM(motor["left"], motor["config"]["drive"])
            setM(motor["right"], motor["config"]["drive"])
    elif ddown:
        if dleft:
            setM(motor["left"], 0)
            setM(motor["right"], -motor["config"]["drive"])
        elif dright:
            setM(motor["left"], -motor["config"]["drive"])
            setM(motor["right"], 0)
        else:
            setM(motor["left"], -motor["config"]["drive"])
            setM(motor["right"], -motor["config"]["drive"])
    elif dright:
        setM(motor["right"], -motor["config"]["drive"])
        setM(motor["left"], motor["config"]["drive"])
    elif dleft:
        setM(motor["right"], motor["config"]["drive"])
        setM(motor["left"], -motor["config"]["drive"])
    else:
        setM(motor["right"], 0)
        setM(motor["left"], 0)
        
        
    # setM(motor["left"], (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") + Gamepad.get_value("dpad_right") - Gamepad.get_value("dpad_left")) * motor["config"]["drive"])
    # setM(motor["right"], (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") - Gamepad.get_value("dpad_right") + Gamepad.get_value("dpad_left")) * motor["config"]["drive"])
   
    if Gamepad.get_value("r_bumper"):
        motor["config"]["drive"] = 1
    if Gamepad.get_value("l_bumper"):
        motor["config"]["drive"] = 0.5
    if Gamepad.get_value("r_trigger") == 1:
        stop_down = 1  # clear stop value
        start_pos_up = 1
        if Robot.get_value(switchID,"switch0") and stop_up:
            setM(motor["lift"], motor["config"]["lift"])# keep going UP
        else: # hit top limit switch, stop and reverse motor
            setM(motor["lift"], 0.0)  # stop motor for now
    elif Gamepad.get_value("l_trigger") == 1 :
        start_pos_up = 1
        stop_up = 1  # clear stop value
        if Robot.get_value(switchID,"switch2") and stop_down:
            setM(motor["lift"], -motor["config"]["lift"])# keeping going DOWN
        else: # hit bottom limit switch, stop and reverse motor
            setM(motor["lift"], 0.0)  # stop motor for now
    elif Gamepad.get_value("button_a") == 1:
        if Robot.get_value(switchID,"switch1") and start_pos_up :
            setM(motor["lift"], motor["config"]["lift"]) # go up 
        elif Robot.get_value(switchID,"switch1") == 0  :
            setM(motor["lift"], 0.0)# stop
            start_pos_up = 0
    else:
        start_pos_up = 1
        setM(motor["lift"], 0.0)




# Problem 1
def tennis_balls2(num):
  if num%3 == 0:
      return num/3
  elif num%2 != 0:
      return num*4+2
  else:
      return num+1
def tennis_ball(num):
  for i in range(0,5):
    num = tennis_balls2(num)
  return num

# Problem 2
def remove_duplicates(num):
  num2 = str(num)
  array = ""
  i = 0
  while i < len(num2):
    #print("I"+str(i))
    if i < len(num2):
      #print("I"+str(i))
      if num2[i] in array :
        
        #print("in"+num2[i])
        #print(num2)
        if i < len(num2):
          num2 = num2[:i]+num2[i+1:]
        else:
          num2 = num2[:i-1]
        #num2 = num2.split(num2[i])
        #print(num2)
        i -= 1
      else:
        #print("Array"+array)
        array += num2[i]
    i+= 1
  return(int(num2))

# Problem 3
def rotate(num):
  num = str(num)

  big = 0;
  for i in num:
    if int(i) > big:
      big = int(i)


  for i in range(big):
    lastnum = num[-1:]
    num = num[:-1]
    num = lastnum + num

  return(int(num))

#Problem 4
def next_fib(num):
  i = 0;
  j = 1;
  if num == 0:
    return 0
  elif num == 1:
    return 1
  while (j<num):
    temp = j
    j = i + j
    i = temp
    
  return j

# Problem 5
def most_common (inputnum):
  outs = []
  zeroArr = []
  for i in range(10):
    outs.append(0)
    zeroArr.append(0)

  for i in str(inputnum):
    outs[int(i)]+=1

# Problem 6
def get_coins(num):
  q = (int) (num / 25)
  num = num % 25
  n = (int) (num / 5)
  num = num % 5

  return int(str(q)+str(n)+str(num))
