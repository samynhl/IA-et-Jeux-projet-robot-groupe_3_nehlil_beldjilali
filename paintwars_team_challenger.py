# Projet "robotique" IA&Jeux 2021
#
# Binome:
#  Prénom Nom: Samy NEHLIL      21113646
#  Prénom Nom: Amel BELDJILALI  21115553
from re import sub
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

    # Renommer les dictionnaires utilisés
    front = sensors["sensor_front"]
    front_left = sensors["sensor_front_left"]
    front_right = sensors["sensor_front_right"]  
    back = sensors["sensor_back"]
    back_left = sensors["sensor_back_left"]
    back_right = sensors["sensor_back_right"]
    left = sensors["sensor_left"]
    right = sensors["sensor_right"]
    
    front_w = front["distance_to_wall"]
    front_left_w = sensors["sensor_front_left"]["distance_to_wall"]
    front_right_w = sensors["sensor_front_right"]['distance_to_wall']
    back_right_w = sensors["sensor_back_right"]['distance_to_wall']
    back_left_w = sensors["sensor_back_left"]['distance_to_wall']
    left_w = sensors["sensor_left"]["distance_to_wall"]
    right_w = sensors["sensor_right"]["distance_to_wall"]

    front_r = front["distance_to_robot"]
    front_left_r = sensors["sensor_front_left"]["distance_to_robot"]
    front_right_r = sensors["sensor_front_right"]['distance_to_robot']
    back_right_r = sensors["sensor_back_right"]['distance_to_robot']
    back_left_r = sensors["sensor_back_left"]['distance_to_robot']
    left_r = sensors["sensor_left"]["distance_to_robot"]
    right_r = sensors["sensor_right"]["distance_to_robot"]

    # -------------------------------------------------------------------------------------------------- 
    # Comportements de braitenberg développés lors du TME 01
    # --------------------------------------------------------------------------------------------------
    def hateBot():
        # Eviter les robots (même équipe ou équipe différente)
        translation = front_r
        rotation = (-1) * front_left_r + 1 * front_right_r
        return translation, rotation
    
    def hateWall():
        # Eviter les murs
        translation = front_w
        rotation = (-1) * front_left_w + 1 * front_right_w
        return translation, rotation
    
    def loveBot():
        # Aller vers les robots
        translation = front_r
        rotation = 1 * front_left_r + (-1) *front_right_r
        return translation, rotation
    
    def loveWall():
        # Aller vers les murs
        translation = front_w
        rotation = 1 * front_left_w + (-1) *front_right_w
        return translation, rotation

    def hateAll():
        # Evite tout les obstacles (robots et murs) comportement braitenberg_avoider
        translation = min(front_w, front_r)
        rotation = (-1) * (front_left_w +  front_left_r) + (1) *(front_right_w +  front_right_r) 
        return translation, rotation
    
    # Eviter les robots de la même équipe
    # Ce comportement évitera le blocage de deux ou plusieurs robots de la même équipe
    def hateTeam():
        if front_left["isSameTeam"] or front_right["isSameTeam"] or left["isSameTeam"] or right["isSameTeam"] or front["isSameTeam"]:
            if left_r<1: return  1, 0.5
            if right_r<1: return  1, -0.5
            if front_r<0.5: return 1, 0.5
            return hateAll()
        return 1, 0

    # --------------------------------------------------------------------------------------------------
    # Plus de comportements : arbre de subsomption, arbre de décision pour éviter les murs
    # --------------------------------------------------------------------------------------------------

    #--------------------------------------------------------------------------------------------------   
    # Comportement de subsomption tme1
    #--------------------------------------------------------------------------------------------------
    #  Si detecter un robot => aller vers ce robot
    #  Sinon eviter les murs si detecter un mur
    #  Sinon aller tout droit
    def subsomption():
        if front_left_r<1 or front_right_r<1: return loveBot()
        elif front_left_w<1 or front_right_w<1: return hateWall()
        else: return 1, 0
    
    # Arbre de subsomption:
    #  Si detecter un robot de la même équipe => hateTeam()
    #  Sinon comportement de subsomption
    def subHateTeam():
        if front_left["isSameTeam"] or front_right["isSameTeam"] or front["isSameTeam"]: return hateTeam()
        return subsomption()

    #--------------------------------------------------------------------------------------------------
    # Arbre de décision
    #--------------------------------------------------------------------------------------------------
    # Pour eviter les murs là ou ils sont
    # Traite tous les cas possibles
    def choisirDirection(l, r, vl, vr):
        # Choisir la direction en fonction des paramètres d'entrées
        if l: return 1, vl
        if r: return 1, vr
    def ADWall():
        d = 0.4
        # Wall en face et sur un des cotes
        if (front_w<d and left_w<d) or (front_w<d and right_w<d):
            return choisirDirection(front_w<d and left_w<d, front_w<d and right_w<d, 1, -1)
        # Wall sur un des cotes ou les deux
        if front_left_w<1 or front_right_w<1:
            if front_left_w<d or front_right_w<d: return hateWall()
            return loveWall()
        # Wall en face
        if front_w < 1:
             if np.random.rand() < 0.5: return 1, 0.5
             return 1, -0.5
        # Wall derriere droite ou gauche
        if  back_right_w<1 or right_w<1 or back_left_w<1 or left_w<1:
            if back_right_w<1 and back_left_w<1: return 1, 0
            return choisirDirection(back_left_w<1 or left_w<1, back_right_w<1 or right_w<1, -0.5, 0.5)
        # Si aucun wall detecté
        return 1, 0

    # Comportement simple par defaut
    # Stratégie utilisée par robot champion
    def default_str():
        # Si detecter un robot ou un mur à sa droite => aller à gauche
        # Sinon detecter un robot ou un mur à sa gauche => aller à droite
        # Sinon aller tout droit
        translation, rotation = 1, 0
        if front_left["distance"] < 1 or front["distance"] < 1: rotation = 0.5
        elif front_right["distance"] < 1: rotation = -0.5
        return translation, rotation 
    
    # Changer la strategie des robots chaque 300 itérations
    # Permet de libérer les robots bloqués aux murs du plan
    # Permet de libérer les robots bloqués avec d'autres robots
    rob = Pyroborobo.get()
    iteration = rob.iterations
    changer_str = (iteration//300 % 2 == 0)

    # subHateTeam | ADWall | default
    def str1():
        if front_left_r<1 or front_right_r<1 or front_r<1: return subHateTeam()
        if changer_str: return ADWall()
        else: return default_str()
    # ADWall | default
    def str2():
        if changer_str: return ADWall()
        return default_str()
    # subsomption | default
    def str3():
        if front_left_r<1 or front_right_r<1 or front_r<1: return subsomption()
        return default_str()
    # subsomption
    def str4():
        return subsomption()
    # default
    def str5():
        return default_str()

    # Strategies purement aléatoire
    # A tester dans le tournoi
    # Retourne une stratégie aléatoire pour chaque robot
    # Permet de voir l'impact de jouer aléatoirement sur le score final
    def str_alea():
        n = np.random.randint(1,5)
        if n==1: return str1()
        elif n==2: return str2()
        elif n==3: return str3()
        elif n==4: return str4()
        else: return str5()

    # Retourne vrai si un robot est poursuivi par un robot de l'équipe adverse
    def isFollowed(sensor):
        return sensor["isRobot"] and (not sensor["isSameTeam"]) and sensor["distance_to_robot"]<1

    # --------------------------------------------------------------------------------------------------
    # Comportements réalisés lors de cette étape du jeu par le robot robotID
    # --------------------------------------------------------------------------------------------------
    # Détecter si il y a un robot de la même équipe => Eviter
    if front_left["isSameTeam"] or front_right["isSameTeam"] or left["isSameTeam"] or right["isSameTeam"] or front["isSameTeam"]: translation, rotation = hateTeam()
    # Détecter si il y a un enemi qui le poursuit => s'arrêter afin de le bloquer (se bloquer aussi)
    if isFollowed(back):
        return 0,0
    # Exécuter pour chaque robot une strategie différente 
    # Affectation de strategies selon le robotID
    # Faire en sorte que tout les robots de la même équipe n'aient pas la même strategie   
    else:
        if robotId<3: return str1()
        elif robotId<6: return str2()
        else: return str3()
    
    '''
    # Comportement réalisé lors de cette étape du jeu par le robot robotID
    # Détecter si il y a un enemi qui le poursuit => s'arrêter afin de le bloquer (se bloquer aussi)
    if isFollowed(sensors["sensor_back"]): 
        return 0,0
    # Détecter si il y a un robot de la même équipe => Eviter
    if front_left["isSameTeam"] or front_right["isSameTeam"] or sensors["sensor_left"]["isSameTeam"] or sensors["sensor_right"]["isSameTeam"] or front["isSameTeam"]: translation, rotation = hateTeam()
    # Exécuter pour chaque robot une strategie différente  choisie aléatoirement   
    else:
        return str_alea()
    '''