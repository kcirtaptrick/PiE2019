import time
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

lift="56692415489952440942506"
right_motor = "56692008314550567751418"
left_motor = "56695389584535285373953"
def setM(motor, speed):
    Robot.set_value(motor, "duty_cycle", speed)
def autonomous_setup():
    # Runs one time1
    print("Autonomous mode has started!")
    Robot.run(autonomous_actions)
    
def autonomous_main():
    # this repeats 20 times a second
    pass
def move(duration, power = 1):
    Robot.set_value(right_motor, "duty_cycle", power)
    Robot.set_value(left_motor, "duty_cycle", power)
    time.sleep(duration)
    Robot.set_value(right_motor, "duty_cycle", 0)
    Robot.set_value(left_motor, "duty_cycle", 0)
def turn(duration, power = 1):
    Robot.set_value(right_motor, "duty_cycle", -power)
    Robot.set_value(left_motor, "duty_cycle", power)
    time.sleep(duration)
    Robot.set_value(right_motor, "duty_cycle", 0)
    Robot.set_value(left_motor, "duty_cycle", 0)

def auto1():
    move(2, 1)
    Robot.set_value(right_motor, "duty_cycle", -1)
    Robot.set_value(left_motor, "duty_cycle", 1)
    # move(2.7 * foot, -1)
    # turn(rotation * 0.3)
async def autonomous_actions():
    global foot
    # Runs one time
    auto1()
    print("Autonomous action sequence started")

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
    if Gamepad.get_value("r_bumper"):
        drive_motor_speed = 1
    if Gamepad.get_value("l_bumper"):
        drive_motor_speed = 0.5
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
        
        
    # Robot.set_value(left_motor, "duty_cycle", (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") + Gamepad.get_value("dpad_right") - Gamepad.get_value("dpad_left")) * drive_motor_speed)
    # Robot.set_value(right_motor, "duty_cycle", (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") - Gamepad.get_value("dpad_right") + Gamepad.get_value("dpad_left")) * drive_motor_speed)
   
    if Gamepad.get_value("r_bumper"):
        drive_motor_speed = 1
    if Gamepad.get_value("l_bumper"):
        drive_motor_speed = 0.5
    if Gamepad.get_value("r_trigger") == 1:
        stop_down = 1  # clear stop value
        start_pos_up = 1
        if Robot.get_value(switchID,"switch2") and stop_up:
            Robot.set_value(lift, "duty_cycle", lift_motor_speed)# keep going UP
        else: # hit top limit switch, stop and reverse motor
            Robot.set_value(lift,"duty_cycle", 0.0)  # stop motor for now
    elif Gamepad.get_value("l_trigger") == 1 :
        start_pos_up = 1
        stop_up = 1  # clear stop value
        if Robot.get_value(switchID,"switch0") and stop_down:
            Robot.set_value(lift, "duty_cycle", -lift_motor_speed)# keeping going DOWN
        else: # hit bottom limit switch, stop and reverse motor
            Robot.set_value(lift,"duty_cycle", 0.0)  # stop motor for now
    elif Gamepad.get_value("button_a") == 1:
        if Robot.get_value(switchID,"switch1") and start_pos_up :
            Robot.set_value(lift,"duty_cycle", lift_motor_speed) # go up 
        elif Robot.get_value(switchID,"switch1") == 0  :
            Robot.set_value(lift, "duty_cycle", 0.0)# stop
            start_pos_up = 0
    else:
        start_pos_up = 1
        Robot.set_value(lift, "duty_cycle", 0.0)