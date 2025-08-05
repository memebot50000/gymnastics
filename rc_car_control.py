from gpiozero import Motor
import time

right_motor = Motor(forward=17, backward=27, enable=12)
left_motor = Motor(forward=22, backward=23, enable=13)
def stop():
    left_motor.stop()
    right_motor.stop()

def move_forward(t, power):
    '''drives car forward for t seconds at specified power percentage'''
    left_motor.forward(power)
    right_motor.backward(power)
    time.sleep(t)
    stop()

def move_backward(t, power):
    '''drives car forward for t seconds at specified power percentage'''
    left_motor.backward(power)
    right_motor.forward(power)
    time.sleep(t)
    stop()

def turn_left(t, power):
    '''turns car left for t seconds at specified power percentage'''
    left_motor.backward(power)
    right_motor.backward(power)
    time.sleep(t)
    stop()

def turn_right(t, power):
    '''turns car right for t seconds at specified power percentage'''
    left_motor.forward(power)
    right_motor.forward(power)
    time.sleep(t)
    stop()

def test(t, power):
    move_forward(t, power)
    move_backward(t, power)
    turn_left(t, power)
    turn_right(t, power)
    stop()
    print("test completed")

print("RC Car Control Ready. Enter W,A,D to control. Enter corresponding times and power percentages after commands. Enter Q to quit. Enter T to test. Remember to put spaces between commands/times/power or the code will break.")

while True:
    kcmds = input("Enter command(s): ").lower()
    tcmds = input("Enter time(s): ")
    pcmds = input("Enter power percentage(s) (0-100): ")
    klst = kcmds.split()
    tlst = [float(t) for t in tcmds.split()]
    plst = [float(p) / 100.0 for p in pcmds.split()]  # Convert power to a scale of 0 to 1
    
    try:
        for i in range(len(klst)):
            if klst[i] == 'w':
                move_forward(tlst[i], plst[i])
            elif klst[i] == 'a':
                turn_left(tlst[i], plst[i])
            elif klst[i] == 's':
                move_backward(tlst[i], plst[i])
            elif klst[i] == 'd':
                turn_right(tlst[i], plst[i])
            elif klst[i] == "t":
                test(tlst[i], plst[i])
            elif klst[i] == 'q':
                stop()
                print("RC Car Control stopped.")
                exit()
            else:
                stop()
    except IndexError:
        print("Error: Number of commands, times, and power percentages do not match.")
    except ValueError:
        print("Error: Invalid input. Please enter numeric values for times and power percentages.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    time.sleep(0.1)  # Short delay to prevent overwhelming the system
