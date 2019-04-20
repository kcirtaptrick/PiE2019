import time
import os 
import sys

sys.path.insert(0, '/home/pi/.local/lib/python2.7/site-packages/')

import pigpio
# from RPLCD.gpio import CharLCD 

gpio = pigpio.pi();

# lcd = CharLCD(pin_rs=4, pin_rw=7, pin_e=8, pins_data=[25,24,23,18])


switchID = "31081732471476003969"
count = 1
time_count = 0
switch0 = False
switch1 = False
switch2 = False
foot = 0.73469387748
rotation = 2.45
lift_motor_speed = 1
stop_down=1
stop_up=1
drive_motor_speed = 0.5

start_pos_up = 1

lift=[19, 26]
left_motor = [21, 20]
right_motor = [12, 16]

def setM(motor, speed):
    if(speed >= 0):
        gpio.write(motor[1], 0)
        gpio.set_PWM_dutycycle(motor[0], 255 * speed)
    else:
        gpio.write(motor[0], 0)
        gpio.set_PWM_dutycycle(motor[1], 255 * -speed)
    # setM(motor, speed)
def autonomous_setup():
    print("Autonomous mode has started!")
    Robot.run(autonomous_actions)

def autonomous_main():
    pass
    #print("m")
    #Robot.set_value(left_motor, "duty_cycle", -1.0)
    #Robot.set_value(right_motor, "duty_cycle",1.0)
    #Robot.set_value(servo_arm_id, "servo1", 1.0) 
    #Robot.set_value(servo_arm_id, "servo0", -1.0) 
    #await Actions.sleep(3.0)
    #autonomous_move()
    
    
async def autonomous_actions():
    #Robot.set_value(servo_arm_id, "servo1", 1.0) 
    #Robot.set_value(servo_arm_id, "servo0", 1.0) 
    #await Actions.sleep(2.0)
    #Tells robot to move forward:
    Robot.run(autonomous_move())
    
    
async def autonomous_move():
    #Tells robot to move forward:
    #Opposite to go forward, same to turn.
    print("Starting forward")
    setM(left_motor,0.3)
    setM(right_motor,0.3)
    await Actions.sleep(2.0)
    print("Starting right turn 90 degrees")
    #Robot.set_value(left_motor, "duty_cycle", 0.3)
    #Robot.set_value(right_motor, "duty_cycle", 0.3)
    setM(left_motor,-0.3)
    setM(right_motor,0.3)
    await Actions.sleep(3.3)
    print("Starting foward")
    #Robot.set_value(left_motor, "duty_cycle", 0.5)
    #Robot.set_value(right_motor, "duty_cycle", -0.5)
    setM(left_motor,0.3)
    setM(right_motor,0.3)
    await Actions.sleep(2.0)
    print("Ending")
    
async def autonomous_follow_line():
    print("Starting forward")
    #Tells robot to move along line (More than 0.9 is black, less is white):
    if(Robot.get_value(line_follower_id, "center") <= 0.9):
        #Tells robot to move forward if on white line
        Robot.set_value(left_motor, "duty_cycle", 0.4)
        Robot.set_value(right_motor, "duty_cycle", -0.4)
        print("Go straight")
    elif (Robot.get_value(line_follower_id, "center") > 0.9):
        #Tells robot to turn if not on white line
        Robot.set_value(left_motor, "duty_cycle", -0.4)
        Robot.set_value(right_motor, "duty_cycle", -0.4)
        print("Turn")

async def autonomous_pick_up_center_box():
    #Tells robot to move forward:
    setM(right_motor, 0.4)
    setM(left_motor, 0.4)
    await Actions.sleep(0.5)
    #Lift up box
    lift_motor_speed = 1
    await Actions.sleep(1.5)
    lift_motor_speed = 0 
    #Tells Roboto to move backwards
    setM(right_motor, -0.4)
    setM(left_motor, -0.4)
    #Unload box
    lift_motor_speed = -1
    await Actions.sleep(1.5)
    lift_motor_speed = 0 
    setM(right_motor, 0.1)
    setM(left_motor, 0.5)
    await Actions.sleep(1.0) 
def move(duration, power = 1):
    setM(right_motor, power)
    setM(left_motor, power)
    time.sleep(duration)
    setM(right_motor, 0)
    setM(left_motor, 0)
def turn(duration, power = 1):
    setM(right_motor, -power)
    setM(left_motor, power)
    time.sleep(duration)
    setM(right_motor, 0)
    setM(left_motor, 0)

#def auto1():
#    move(2, 1)
#    setM(right_motor, -1)
#    setM(left_motor, 1)
    # move(2.7 * foot, -1)
    # turn(rotation * 0.3)
#async def autonomous_actions():
 #   global foot
    # Runs one time
  #  auto1()
   # print("Autonomous action sequence started")

def teleop_setup():
    print("Tele-operated mode has started!")

def teleop_main():
    global stop_up
    global stop_down
    global start_pos_up
    global lift_motor_speed
    global drive_motor_speed
    dup = Gamepad.get_value("dpad_up")
    ddown = Gamepad.get_value("dpad_down")
    dleft = Gamepad.get_value("dpad_left")
    dright = Gamepad.get_value("dpad_right")
    
    if Gamepad.get_value("button_y"):
        gpio.write(16, 1)
    if Gamepad.get_value("button_b"):
        gpio.write(16, 0)
    if Gamepad.get_value("button_x"):
        print(__file__)
    
    if Gamepad.get_value("r_bumper"):
        lift_motor_speed = 1
    if Gamepad.get_value("l_bumper"):
        lift_motor_speed = 0.5
    if dup:
        if dleft:
            setM(left_motor, 0)
            setM(right_motor, drive_motor_speed)
        elif dright:
            setM(left_motor, drive_motor_speed)
            setM(right_motor, 0)
        else:
            setM(left_motor, drive_motor_speed)
            setM(right_motor, drive_motor_speed)
    elif ddown:
        if dleft:
            setM(left_motor, 0)
            setM(right_motor, -drive_motor_speed)
        elif dright:
            setM(left_motor, -drive_motor_speed)
            setM(right_motor, 0)
        else:
            setM(left_motor, -drive_motor_speed)
            setM(right_motor, -drive_motor_speed)
    elif dright:
        setM(right_motor, -drive_motor_speed)
        setM(left_motor, drive_motor_speed)
    elif dleft:
        setM(right_motor, drive_motor_speed)
        setM(left_motor, -drive_motor_speed)
    else:
        setM(right_motor, 0)
        setM(left_motor, 0)
        
        
    # setM(left_motor, (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") + Gamepad.get_value("dpad_right") - Gamepad.get_value("dpad_left")) * drive_motor_speed)
    # setM(right_motor, (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") - Gamepad.get_value("dpad_right") + Gamepad.get_value("dpad_left")) * drive_motor_speed)
   
    if Gamepad.get_value("r_bumper"):
        drive_motor_speed = 1
    if Gamepad.get_value("l_bumper"):
        drive_motor_speed = 0.5
    if Gamepad.get_value("r_trigger") == 1:
        stop_down = 1  # clear stop value
        start_pos_up = 1
        if Robot.get_value(switchID,"switch0") and stop_up:
            setM(lift, lift_motor_speed)# keep going UP
        else: # hit top limit switch, stop and reverse motor
            setM(lift, 0.0)  # stop motor for now
    elif Gamepad.get_value("l_trigger") == 1 :
        start_pos_up = 1
        stop_up = 1  # clear stop value
        if Robot.get_value(switchID,"switch2") and stop_down:
            setM(lift, -lift_motor_speed)# keeping going DOWN
        else: # hit bottom limit switch, stop and reverse motor
            setM(lift, 0.0)  # stop motor for now
    elif Gamepad.get_value("button_a") == 1:
        if Robot.get_value(switchID,"switch1") and start_pos_up :
            setM(lift, lift_motor_speed) # go up 
        elif Robot.get_value(switchID,"switch1") == 0  :
            setM(lift, 0.0)# stop
            start_pos_up = 0
    else:
        start_pos_up = 1
        setM(lift, 0.0)




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