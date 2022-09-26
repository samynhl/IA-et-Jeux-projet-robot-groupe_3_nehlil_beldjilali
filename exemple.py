# Projet "robotique" IA&Jeux 2021
#
# Binome:
#  Prénom Nom: Samy NEHLIL
#  Prénom Nom: Amel BELDJILALI
import numpy as np
import random as random

import subsomption as subsomption
import braitenberg_avoider as braitenberg_avoider

def get_team_name():
    return "ESI-ALG"

scores = {i:0 for i in range(8)}

def step(robotId, sensors):
    global scores
    translation, rotation = strategy4(robotId, sensors)
    scores[robotId]+= translation*(1-abs(rotation))
    return strategy4(robotId, sensors)
    if (sensors["sensor_front_left"]["isSameTeam"] 
            or sensors["sensor_front_right"]["isSameTeam"] 
            or sensors["sensor_front"]["isSameTeam"]
            or sensors["sensor_left"]["isSameTeam"]
            or sensors["sensor_right"]["isSameTeam"]
            or sensors["sensor_back_left"]["isSameTeam"]
            or sensors["sensor_back_right"]["isSameTeam"]):
        return braitenberg_avoider.step(robotId, sensors)
    if ((sensors["sensor_back_right"]["isRobot"] and not sensors["sensor_back_right"]["isSameTeam"]) or
         (sensors["sensor_back_left"]["isRobot"] and not sensors["sensor_back_left"]["isSameTeam"]) or
            (sensors["sensor_back"]["isRobot"] and not sensors["sensor_back"]["isSameTeam"])) :
        return 0,0
    return subsomption.step(robotId, sensors)

def best_robot():
    global scores
    return np.argmax(scores.values()),scores[np.argmax(scores.values())]

def strategy1(robotId, sensors):
    if sensors["sensor_front_left"]["distance"] < 1 or sensors["sensor_front"]["distance"] < 1:
        rotation = 0.5  # rotation vers la droite
    elif sensors["sensor_front_right"]["distance"] < 1:
        rotation = -0.5  # rotation vers la gauche
    else:
        rotation = 0
    return 1, rotation

def strategy2(robotId, sensors):
    translation = 1
    rotation = 0
    if sensors["sensor_front_right"]["distance"] < 1 or sensors["sensor_front"]["distance"] < 1:
        rotation = -0.5
    elif sensors["sensor_front_left"]["distance"] < 1:
        rotation = 0.5
    return translation, rotation

def strategy3(robotId, sensors):
    if sensors["sensor_front_left"]["distance"]<1 or sensors["sensor_front_right"]["distance"]<1 or sensors["sensor_front"]["distance"]<1:
        return braitenberg_avoider.step(robotId,sensors)
    else:
        return 1,np.random.random()*2 - 1

def strategy4(robotId, sensors):
    # Eviter les robots de la meme equipe
    if (sensors["sensor_front"]["isSameTeam"]
            or sensors["sensor_front_left"]["isSameTeam"] 
            or sensors["sensor_left"]["isSameTeam"]):
        return 1,0.5

    if (sensors["sensor_front"]["isSameTeam"]
            or sensors["sensor_front_right"]["isSameTeam"] 
            or sensors["sensor_right"]["isSameTeam"]):
        return 1,-0.5
    
    # Suivre les robots de l'autre equipe
    if (sensors["sensor_back"]["isRobot"] and not sensors["sensor_back"]["isSameTeam"]) :
        return 0,0

    if (sensors["sensor_back_right"]["isRobot"] and not sensors["sensor_back_right"]["isSameTeam"]) :
        return 1,0.5

    if (sensors["sensor_back_left"]["isRobot"] and not sensors["sensor_back_left"]["isSameTeam"]) :
        return 1,-0.5        
    
    # Sinon suivre l'architecture de subsomption
    return subsomption.step(robotId, sensors)
