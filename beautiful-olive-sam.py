import time
import random
import pyttsx3

#say positive things every ten minutes
#say positive things
def sayPositiveThings():
    #print("You are going to get your kip soon!")
    robotVoice = pyttsx3.init()
    robotVoice.say(random.choice(positiveThings))
    engine.runAndWait()


#main program
positiveThings = ["You are going to get your kip soon!", "blah blah blah blah", "oogah shakah nah", "koalas are cute", "rorororrororo"]
numberOfNewThings= int(input("How many new positive things would you like me to say?"))

# i = 0
# while (i <= numberOfNewThings):
#     newThing = str(input("Input new positive thing here:"))
#     positiveThings.append(newThing)
#     i += 1 
# print(positiveThings)

for i in range (0, numberOfNewThings):
    newThing = str(input("Input new positive thing here:"))
    positiveThings.append(newThing)
print(positiveThings)

while True:
    #time.sleep(6000)
    time.sleep(6)
    sayPositiveThings()




#control LEDs
#control speakers

