switchID = "31081732471476003969"
count = 1
time_count = 0
switch0 = False
switch1 = False
switch2 = False

lift_motor_speed = 1
stop_down=1
stop_up=1
drive_motor_speed = 0.5

start_pos_up = 1

lift="47247648891492862812797"
right_motor = "56692008314550567751418"
left_motor = "56695389584535285373953"

def autonomous_setup():
    # Runs one time1
    print("Autonomous mode has started!")
    Robot.run(autonomous_actions)
    
def autonomous_main():
    # this repeats 20 times a second
    pass
    
async def autonomous_actions():
    # Runs one time
    print("Autonomous action sequence started")

def teleop_setup():
    print("Tele-operated mode has started!")

def teleop_main():
    global stop_up
    global stop_down
    global start_pos_up
    global lift_motor_speed
    
    Robot.set_value(left_motor, "duty_cycle", (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") + Gamepad.get_value("dpad_right") - Gamepad.get_value("dpad_left")) * drive_motor_speed)
    Robot.set_value(right_motor, "duty_cycle", (Gamepad.get_value("dpad_up") - Gamepad.get_value("dpad_down") - Gamepad.get_value("dpad_right") + Gamepad.get_value("dpad_left")) * drive_motor_speed)
   
        
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