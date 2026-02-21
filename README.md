# scanpng

Analyseur detaillé de fichiers PNG.  
Affiche les chunks, vérifie les CRC, montre les offsets, détecte les données appendées après `IEND`.  

## Installation

pip install scanpng

## Utilisation

scanpng -path fichier.png

## Fonctionnalités

- Vérification de la signature PNG  
- Lecture et affichage de tous les chunks  
- CRC fichier vs CRC calculé  
- Offsets exacts  
- Détection des données appendées  
- Affichage coloré (colorama)

## Dépôt

Ce dépôt contient le code source du package publié sur PyPI.

## Licence

MIT


