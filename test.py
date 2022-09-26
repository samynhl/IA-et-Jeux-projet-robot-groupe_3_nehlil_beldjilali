# Projet "robotique" IA&Jeux 2021
#
# Binome:
#  Prénom Nom: Samy NEHLIL
#  Prénom Nom: Amel BELDJILALI
import numpy as np
import random as random

from pyroborobo import Pyroborobo

def get_team_name():
    return "ESI"

def get_extended_sensors(sensors):
    for key in sensors:
        sensors[key]["distance_to_robot"] = 1.0
        sensors[key]["distance_to_wall"] = 1.0
        if sensors[key]["isRobot"] == True:
            sensors[key]["distance_to_robot"] = sensors[key]["distance"]
        else:
            sensors[key]["distance_to_wall"] = sensors[key]["distance"]
    return sensors

def step(robotId, sensors):

    sensors = get_extended_sensors(sensors)

    # Variables utilisées
    front_left = sensors["sensor_front_left"]
    front_right = sensors["sensor_front_right"]
    front = sensors["sensor_front"]
    s_front_left_w = sensors["sensor_front_left"]["distance_to_wall"]
    s_front_right_w = sensors["sensor_front_right"]['distance_to_wall']
    s_back_right_w = sensors["sensor_back_right"]['distance_to_wall']
    s_back_left_w = sensors["sensor_back_left"]['distance_to_wall']
    s_left_w = sensors["sensor_left"]["distance_to_wall"]
    s_right_w = sensors["sensor_right"]["distance_to_wall"]
    s_front_w = front["distance_to_wall"] 

    # --------------------------------------------------------------------------------- 
    # Comportements de braitenberg développés lors des TMEs 1&2
    # ---------------------------------------------------------------------------------
    def hateAll():
        # Evite tout les obstacles (robots et murs)
        translation = min(front["distance_to_wall"], front["distance_to_robot"])
        rotation = (-1) * (front_left["distance_to_wall"] +  front_left["distance_to_robot"]) + (1) *(front_right["distance_to_wall"] +  front_right["distance_to_robot"]) 
        return translation, rotation
    
    def hateBot():
        # Eviter les robots (même équipe ou équipe différente)
        translation = front["distance_to_robot"]
        rotation = (-1) * front_left["distance_to_robot"] + 1 * front_right["distance_to_robot"]
        return translation, rotation
    
    def hateWall():
        # Eviter les murs
        translation = front["distance_to_wall"]
        rotation = (-1) * front_left["distance_to_wall"] + 1 * front_right["distance_to_wall"]
        return translation, rotation
    
    def loveBot():
        # Aller vers les robots si detecter
        translation = front["distance_to_robot"]
        rotation = 1 * front_left["distance_to_robot"] + (-1) *front_right["distance_to_robot"]
        return translation, rotation
    
    def loveWall():
        # Aller vers les murs si detecter
        translation = front["distance_to_wall"]
        rotation = 1 * front_left["distance_to_wall"] + (-1) *front_right["distance_to_wall"]
        return translation, rotation

    # --------------------------------------------------------------------------------- 
    # Plus de comportements : arbre de subsomption, arbre de décision
    # ---------------------------------------------------------------------------------
    
    # Eviter les robots de la même équipe
    # Ce comportement évitera le blocage de deux ou plusieurs robots de la même équipe
    def hateTeam():
        if front_left["isSameTeam"] or front_right["isSameTeam"] or sensors["sensor_left"]["isSameTeam"] or sensors["sensor_right"]["isSameTeam"] or front["isSameTeam"]:
            if sensors["sensor_left"]["distance_to_robot"]<1: return  1, 0.3
            if sensors["sensor_right"]["distance_to_robot"]<1: return  1, -0.3
            if front["distance_to_robot"]<0.5: return 1, 0.3
            return hateAll()
        return 1, 0
    
    # Comportement de subsomption tme1
    #  Si detecter un robot => aller vers les robots
    #  Sinon eviter les murs si detecter un mur
    #  Sinon aller tout droit
    def subsomption():
        if front_left["distance_to_robot"]<1 or front_right["distance_to_robot"]<1:
            return loveBot()
        elif front_left["distance_to_wall"]<1 or front_right["distance_to_wall"]<1:
            if front_left["distance_to_wall"] == front_right["distance_to_wall"]: return 1, 0.5
            return hateWall()
        else: return 1, 0
    
    # Arbre de subsomption:
    #  Si detecter un robot de la même équipe => hateTeam()
    #  Sinon comportement de subsomption
    def subHateTeam():
        if front_left["isSameTeam"] or front_right["isSameTeam"]: return hateTeam()
        return subsomption()
    
    # Arbre de décision
    # Pour eviter les murs là ou ils sont
    # Traite tous les cas possibles
    def avoidWall():
        def choisirDirection(a, b, va, vb):
            # Choisir la direction en fonction des paramètres d'entrées
            # Choisir de manière aléatoire par quelle direction commencer le choix
            if np.random.random_sample() < 0.5:
                if a: return 1, va
                if b: return 1, vb
            else:
                if b: return 1, vb
                if a: return 1, va
        # Mur en face et sur un des cotes
        d = 0.3
        if (s_front_w<d and s_left_w<d) or (s_front_w<d and s_right_w<d):
            l = s_front_w<d and s_left_w<d
            r = s_front_w<d and s_right_w<d
            return choisirDirection(l, r, 1, -1)
        d = 0.4
        # Mur sur un des cotes ou les deux
        if s_front_left_w<1 or s_front_right_w<1:
            if s_front_left_w - s_front_right_w < 0.1 : return 1, 1
            if s_front_left_w<d or s_front_right_w<d: return hateWall()
            return loveWall()
        d = 0.3
        # Mur derriere droite ou gauche
        if  s_back_right_w<1 or s_right_w<1 or s_back_left_w<1 or s_left_w<1:
            if s_back_right_w<1 and s_back_left_w<1: return 1, 0 
            l = s_back_left_w<1 or s_left_w<1
            r = s_back_right_w<1 or s_right_w<1
            return choisirDirection(l, r, -0.3, 0.3)
        # Mur en face
        if s_front_w < 1:
             if np.random.random_sample() < 0.5: return 1, 0.3
             else: return 1, -0.3
        return 1, 0


    # Comportement simple par defaut
    def default():
        # Si detecter un robot ou un mur à sa droite => aller à gauche
        # Sinon detecter un robot ou un mur à sa gauche => aller à droite
        # Sinon aller tout droit
        translation, rotation = 1, 0
        if sensors["sensor_front_left"]["distance"] < 1 or sensors["sensor_front"]["distance"] < 1:
            rotation = 0.5
        elif sensors["sensor_front_right"]["distance"] < 1:
            rotation = -0.5
        return translation, rotation 
    
    rob = Pyroborobo.get()
    iteration = rob.iterations
    # Changer la strategie des robots en fonction du nombre d'itérations
    # Changer de strategie chaque 400 itérations
    changer_str =  iteration//400 % 2 == 0

    # Affectation de startegies selon le robotID
    # Faire en sorte que tout les robots de la même équipe n'aient pas la même strategie

    # subHateTeam + ( avoidWall / default)
    def str1():
        if front_left["distance_to_robot"]<1 or front_right["distance_to_robot"]<1 or front["distance_to_robot"]<1: return subHateTeam()
        if changer_str: return avoidWall()
        else: return default()
    # ( avoidWall / default)
    def str2():
        if changer_str: return avoidWall()
        else: return default()
    # subHateTeam + default
    def str3():
        if front_left["distance_to_robot"]<1 or front_right["distance_to_robot"]<1 or front["distance_to_robot"]<1: return subHateTeam()
        return default()

    def detect_back(s):
        return s["isRobot"] and (not s["isSameTeam"]) and s["distance"]<1
    # Detecte si il y a un enemie qui le poursuit
    if detect_back(sensors["sensor_back"]): 
        return 0,0
    if front_left["isSameTeam"] or front_right["isSameTeam"] or sensors["sensor_left"]["isSameTeam"] or sensors["sensor_right"]["isSameTeam"] or front["isSameTeam"]: translation, rotation = hateTeam()
    else:
        if robotId<3: return str1()
        elif robotId<5: return str2()
        else: return str3()

    # limiter les valeurs de vitesse de sortie entre -1 et +1
    translation = max(-1,min(translation,1))
    rotation = max(-1, min(rotation, 1))
    
    return translation, rotation