# TODO: Shift autonomous path step times to previous step. 
import time
import datetime
import json
import sys
sys.path.insert(0, '/home/pi/.local/lib/python2.7/site-packages/')

import pigpio
gpio = pigpio.pi()

motor = {
    'current': {
        'direction': '',
        'speed': 0, # Motor Value
        'lift': 0, # Motor Value
    },
    "config": {
        'speeds': [0.5, 1], # Use this to configure "speed modes", will only accept 2 values
        'speed': 0, # This is an index of the list above, not a motor value
        "lift": 1, # Motor Value
    },
    "right": {
        "name": "right",
        "pins": [12, 16], # Ignore
        "ids": ["56703981851323474668674", "56694927379020470104453"],
    },
    "left": {
        "name": "left",
        "pins": [21, 20], # Ignore
        "ids": ["56695389584535285373953", "56689954256640780132715"],
    },
    "lift": {
        "name": "lift",
        "pins": [19, 26],
    }
}

# ANY CHANGES TO AUTONOMOUS CONFIGURATION WILL ONLY GO INTO EFFECT AFTER SAVE AND UPLOAD
autonomous = {
    'list': 'all', # List autonomous and/or archive titles to console using 'none', 'autonomous', 'archive' or 'all'
    'config': {
        'title': 'Untitled', # [RECOMMENDED] Set title of autonomous recording
        'pathIndex': 'last', # Set index of autonomous path that should be used, set to 'last' to use most recent recording
        'step-logging': 'none', # TODO: Set autonomous step logging detail, options: 'none', 'vague', 'explicit'
        'trim-recording': True, # Setting this to true will trim the non-movement in the beginning and end of the recording
        'smart-trim': True, # This will replace all non-movement in the recording longer than autonomous['config']['stop-length']
        'stop-length': 0.3,
        "foot": 0.73469387748,
        "rotation": 2.45,
        "file": "/home/pi/Autonomous/autonomous_path.json",
    },
    'archive': {
        'title': 'Untitled', # [RECOMMENDED] Set title of archive when archiving
        'doArchive': False, # [NOTICE] This will keep archiving everything until set to false, remember to reverse afterward, save, and upload
                            # This will erase autonomous['config']['file'] when the robot is started in tele-op mode 
                            # and append its contents to autonomous['archive']['archiveFile'].
        'file': "/home/pi/Autonomous/archive.json"
    },
    "recording": False,
    'startTime': 0,
    'previousTime': 0,
    'path': [],
}

peripherals = {
    'switch': "18851477588195929070"
}

# Lift values
stop_down=1
stop_up=1
start_pos_up = 1

# setM(String side, float speed, float offset)
def setM(side, speed, offset=1):
    for ID in motor[side]['ids']:
        Robot.set_value(ID, 'duty_cycle', -speed * offset)

# move(String direction, float lift)
def move(direction, lift, speed = None):
    global autonomous
    global motor
    if speed == None:
        speed = motor['config']['speeds'][motor['config']['speed']]
    current = motor['current']
    if(direction != current['direction'] or speed != current['speed'] or lift != current['lift']):
        
        print(speed)
        motor['current'] = {
            'direction': direction,
            'speed': speed,
            'lift': lift,
        }
        if(autonomous['recording']):
            currentTime = time.time()
            autonomous['path'][-1]['time'] = currentTime - autonomous['previousTime']
            autonomous['path'].append({
                'direction': direction,
                'speed': speed,
                'lift': lift
            })
            autonomous['previousTime'] = currentTime

        # Set drive motor values
        if(direction == ''):
            setM("right", 0)
            setM("left", 0)
        elif(direction == 'u'):
            setM("left", speed)
            setM("right", speed)
        elif(direction == 'd'):
            setM("left", -speed)
            setM("right", -speed)
        elif(direction == 'r'):
            setM("right", -speed)
            setM("left", speed)
        elif(direction == 'l'):
            setM("right", speed)
            setM("left", -speed)
        elif(direction == 'ul'):
            setM("left", 0)
            setM("right", speed)
        elif(direction == 'ur'):
            setM("left", speed)
            setM("right", 0)
        elif(direction == 'dl'):
            setM("left", 0)
            setM("right", -speed)
        elif(direction == 'dr'):
            setM("left", -speed)
            setM("right", 0)
        else:
            print('Error: See move(String direction)')
        
        # Set lift motor value
        if(lift >= 0):
            gpio.write(motor['lift']["pins"][1], 0)
            gpio.set_PWM_dutycycle(motor['lift']["pins"][0], 255 * lift)
        else: 
            gpio.write(motor['lift']["pins"][0], 0)
            gpio.set_PWM_dutycycle(motor['lift']["pins"][1], 255 * -lift)

def checkSwitch(switch):
    try:
        return Robot.get_value(peripherals['switch'], "switch" + str(switch));
    except:
        return True

def pathTime(path):
    time = 0
    for step in path:
        time += step['time']
    return time
def autonomous_setup():
    print("Autonomous mode has started!")
    Robot.run(play_recording)
def autonomous_main():
    pass
async def play_recording():
    data = json.load(open(autonomous['config']['file'], 'r'))
    if len(data) == 0:
        raise Exception('No autonomous recordings found')
    pathIndex = autonomous['config']['pathIndex']
    if pathIndex == 'last': 
        recording = data[-1]
    else:
        recording = data[pathIndex]
    path = recording['path']
    print('')
    print('Executing recording[%s] titled: %s, for %s seconds' % (pathIndex, recording['title'], recording['time']))
    for step in path:
        logging = autonomous['config']['step-logging']
        if(logging == 'explicit'):
            print(step)
        move(step['direction'], step['lift'], step['speed'])
        time.sleep(step['time'])
    
    print('Recording completed')

def teleop_setup(): 
    # Archive autonomous['config']['file'] contents on tele-op run
    if autonomous['archive']['doArchive']:
        config = autonomous['archive']
        archive = json.load(open(config['file'], 'r'))
        archive.append({
            'title': config['title'],
            'timeArchived': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'recordings': json.load(open(autonomous['config']['file'], 'r'))
        })
        json.dump(archive, open(config['file'], 'w'), indent=2)
        
        json.dump([], open(autonomous['config']['file'], 'w'))
        
    if(autonomous['list'] != 'none'):
        option = autonomous['list']
        output = ''
        if option == 'autonomous' or option == 'all':
            recordings = json.load(open(autonomous['config']['file'], 'r'))
            output += 'AUTONOMOUS: %s\n' % autonomous['config']['file']
            for i in range(len(recordings)):
                output += '  %s: title: %s, runtime: %s seconds\n' % (i, recordings[i]['title'], recordings[i]['time'])
        if option == 'archive' or option == 'all':
            archives = json.load(open(autonomous['archive']['file'], 'r'))
            output += 'ARCHIVES: %s\n' % autonomous['archive']['file']
            for i in range(len(archives)):
                output += '  %s: title: %s, timeArchived: %s\n' % (i, archives[i]['title'], archives[i]['timeArchived'])
        if output == '':
            output = 'autonomous[\'list\'] contains an invalid option'
        print(output)

    print("Tele-operated mode has started!")

def teleop_main():
    global autonomous
    
    # Lift values
    global stop_up
    global stop_down
    global start_pos_up

    # Get direction from dpad
    # If you get a KeyError, check to see if your controller is connected
    direction = ''
    direction += 'u' if Gamepad.get_value("dpad_up") else ''
    direction += 'd' if Gamepad.get_value("dpad_down") else ''
    direction += 'l' if Gamepad.get_value("dpad_left") else ''
    direction += 'r' if Gamepad.get_value("dpad_right") else ''

    # Get lift value
    lift = 0
    if Gamepad.get_value("r_trigger") == 1:
        stop_down = 1  # clear stop value
        start_pos_up = 1
        if checkSwitch(0) and stop_up:
            lift = motor["config"]["lift"]# keep going UP
        else: # hit top limit switch, stop and reverse motor
            lift = 0  # stop motor for now
    elif Gamepad.get_value("l_trigger") == 1:
        start_pos_up = 1
        stop_up = 1  # clear stop value
        if checkSwitch(2) and stop_down:
            lift = -motor["config"]["lift"] # keeping going DOWN
        else: # hit bottom limit switch, stop and reverse motor
            lift = 0 # stop motor for now
    elif Gamepad.get_value("button_a") == 1:
        if checkSwitch(1) and start_pos_up :
            lift = motor["config"]["lift"] # go up 
        elif checkSwitch(1) == 0:
            lift = 0# stop
            start_pos_up = 0
    else:
        start_pos_up = 1
        lift = 0

    # Set motor values
    move(direction, lift)

    # Autonomous controls
    if Gamepad.get_value('button_start'):
        if not autonomous['recording']:
            print('Started recording')
            autonomous['startTime'] = time.time()
            autonomous['previousTime'] = autonomous['startTime']
            autonomous['recording'] = True
            autonomous['path'].append({
                'direction': '',
                'speed': 0,
                'lift': 0
            })
        else: 
            print('Already recording')
    if Gamepad.get_value('button_back'):
        if autonomous['recording']:
            currentTime = time.time()

            print("Logging record")
            
            autonomous['path'][-1]['time'] = currentTime - autonomous['previousTime']
            totalTime = currentTime - autonomous['startTime']
            print('Total time of recording: %s seconds' % (totalTime))
            if(autonomous['config']['trim-recording']):
                totalTime -= autonomous['path'][0]['time'] + autonomous['path'][-1]['time']
                autonomous['path'] = autonomous['path'][1:-1]
                autonomous['path'].append({
                    'time': 0,
                    'direction': '',
                    'speed': 0,
                    'lift': 0
                })
                if(autonomous['config']['smart-trim']):
                    for step in autonomous['path']:
                        if step['direction'] == '' and step['lift'] == 0:
                            step['time'] = min(step['time'], autonomous['config']['stop-length'])
                    totalTime = pathTime(autonomous['path'])
                print('Path trimmed, total time of recording: %s seconds' % (totalTime))
            

            autonomous['recording'] = False
        
            data = json.load(open(autonomous['config']['file'], 'r'))
            data.append({
                'title': autonomous['config']['title'],
                'time': totalTime,
                'path': autonomous['path']
            })
            json.dump(data, open(autonomous['config']['file'], 'w'), indent=2)
            autonomous['path'] = []
            print('Record logged')
        else:
            print('Not recording')
    
    # Set Speed
    if Gamepad.get_value("r_bumper"):
        motor["config"]["speed"] = 1
    if Gamepad.get_value("l_bumper"):
        motor["config"]["speed"] = 0
    
    




# Coding challenges (I remember them not working during the competition, someone should work on fixing them)
import math

# Problem 1
def tennis_ball(num):
 for _ in range(5):
   if num % 3 == 0:
     num = num / 3
   elif num % 2 !=0:
     num = num * 4 + 2
   else:
     num = num + 1

 return int(num)

def list_to_integer(l):
 sum = 0
 count = 1
 for i in l:
   sum = sum + int(i) * 10**(len(l)-count)
   count = count + 1
 return sum

# Problem 2
def remove_duplicates(num):
 s = str(num)
 l = []
 for i in s:
   if i not in l:
     l.append (i)
 n = list_to_integer(l)
 return n

# Problem 3
def rotate(num):
  max = 0
  s = str(num)
  s = list(s)
  for i in s:
    if int(i) > max:
      max = int(i)
  for _ in range(max):
    s = [s.pop()] + s
  j = list_to_integer(s)
  return j

# Problem 4
def next_fib(num):
  next = 1
  previous = 0
  while next < num:
    sum = next + previous
    previous = next
    next = sum
  if num == 0:  
    return 0
  return next

# Problem 5
def most_common(num):
  s = str(num)
  d = {}
  return_value = ""
  return_list = []
  for i in s:
    if i in d:
      d[i] = d[i] + 1 
    else:
      d[i] = 1

  if len(s) < 4:
    loop = len(s)
  else:
    loop = 4

  for _ in range(loop):
    max_val = 0
    max_key = ""
    for i in d:
      if d.get(i) > max_val:
        max_val = d.get(i)
        max_key = i

    if max_key in d:
      del d[max_key]
      return_list += [max_key]
    
  return_list.sort(reverse=True)
  return list_to_integer(return_list)

# Problem 6
def get_coins(num):
  X = 25
  Y = 5
  Z = 1
  quarters = num // 25
  num = num - (X * quarters)
  nickels = num // 5
  num = num - (Y * nickels)
  pennies = num
  l = [quarters, nickels, pennies]
  return list_to_integer(l)



