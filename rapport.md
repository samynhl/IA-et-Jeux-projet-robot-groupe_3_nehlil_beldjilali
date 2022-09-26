# Rapport de projet  
- Etudiant 1: Samy NEHLIL           21113646
- Etudiant 2: Amel BELDJILALI       21115553 

## I - Comportements implémentés:
### **Comportement de braitenberg** (comportement développés lors du tme-1)
    hateBot
    hateWall
    loveBot
    loveWall
    hateAll
### **hateTeam**:  
    Si un robot de la même équipe est détecté alors Eviter 
    Sinon avancer tout droit
### **subsomption**:  suivre les adversaires (comportement de subsomption tme-1)
    1. Si un robot de l'équipe adverse est détecté alors suivre
    2. Sinon eviter les murs
    3. Sinon aller tout droit
### **subHateTeam**:  suivre les adversaires  et eviter les coequipiers (comportement de subsomption tme-1)
    1. Si un robot de la même équipe est détecté alors Eviter
    2. Sinon comportement de subsomption
### **ADWall**: arbre de décision pour gérer le comportement lorsqu'il y a un mur
    1. Si le robot est proche d'un mur (tout cotés compris) alors s'éloigner du mur
    2. Sinon se rapprocher du mur
### **str_alea**: Une autre stratégie purement aléatoire
    - Choisir de façon aléatoire quelle stratégie utiliser parmi les stratégies 1,2 & 3

## II - __Strategie comportementale__:
    - Si detecter un robot de la même équipe alors Eviter
    - Sinon un robot de l'équipe adverse est détecté de derriere alors s'arrêter pour le bloquer
    
    Puis 03 comportements (stratégies) différents selon le robotId:
    - Suivre les adversaires, sinon gérer le comportement au à coté du mur (AD)
    - Gérer le comportement au à coté du mur (AD)
    - Suivre les adversaires, sinon eviter les murs

 __Remarque__:  
On change de comportement des robots tous les 300 itérations.