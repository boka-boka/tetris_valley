# Tetris - doc technique
J'ai écrit cette implémentation de Tetris pour m'amuser et m'initier à l'utilisation de pygame.
Voici quelques notes sur la façon dont le jeu est implémenté et structuré. Evidemment, j'écris tout ça après avoir fait l'implémentation... no comment !

## Notes sur le style
J'écris tout le programme en anglais. Je trouve que c'est plus simple et la langue est adaptée à écrire du code.

## Principaux fichiers/sources
### les constantes
_tetris_palette.py_ : ce fichier contient les définitions de couleur utilisées dans le rendu du jeu sous forme de tuples rgb.

### main et controleurs
_tetris.py_ : contient l'initialisation du jeu et mise en place de la stack de controleurs dans la boucle d'évènements.


### les classes d'état
State
Shape
Block

### les classes pour la visualisation
Render


