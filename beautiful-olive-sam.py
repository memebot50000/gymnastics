import time
import random
import pygame
#say positive things every ten minutes
#say positive things
def sayPositiveThings():
    #print("You are going to get your kip soon!")
    #print(random.choice(positiveThings))
    try:
        pygame.mixer.init()
        sound = pygame.mixer.Sound(random.choice(positiveThings))
        sound.play()
        # Wait for the sound to finish playing
        while pygame.mixer.get_busy():
            pygame.time.wait(100)
    except Exception as e:
        print(f"Error playing sound: {e}")



#main program
#positiveThings = ["You are going to get your kip soon!", "blah blah blah blah", "oogah shakah nah", "koalas are cute", "rorororrororo"]
#numberOfNewThings= int(input("How many new positive things would you like me to say?"))
numberOfThings = 3
positiveThings = []
for r in range(0, numberOfThings): # :)
    positiveThings.append("thing" + str(r) + ".mp3")

# i = 0
# while (i <= numberOfNewThings):
#     newThing = str(input("Input new positive thing here:"))
#     positiveThings.append(newThing)
#     i += 1 
# print(positiveThings)

# for i in range (0, numberOfNewThings):
#     newThing = str(input("Input new positive thing here:"))
#     positiveThings.append(newThing)
# print(positiveThings)

while True:
    #time.sleep(6000)
    time.sleep(2)
    sayPositiveThings()

