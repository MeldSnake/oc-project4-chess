[![Python](https://img.shields.io/badge/python-3.11-blue)](https://github.com/MeldSnake/oc_p4)

Application de gestion de tournois d'échecs.

# Description

Application permettant la gestion de plusieurs tournois d'échecs de façons hors ligne.

Cette application permet de gérer différent module représentant des tournois :

- Le descriptif d'un tournoi
- Les rondes et matches d'un tournoi
- La liste des joueurs
- Le score des matches

Elle permet d'organiser des événements de tournois et de gérer le classement de chacun des joueurs.

# Installation

## Prérequis

- [Git](https://git-scm.org/)
- [Python 3.11](https://www.python.org/downloads/) ou supérieur.
- [pip](https://docs.python.org/fr/3/library/ensurepip.html) si non installé par défaut avec Python.

## Environnement virtuel

- Linux / Mac (sh) :
    ```bash
    > python -m venv .venv
    > sh ./.venv/scripts/activate
    ```
- Windows (cmd) :
    ```cmd
    > python -m venv .venv
    > 
    > .\.venv\Scripts\activate.bat
    ```
- Windows (PowerShell) :
    ```powershell
    > python -m venv .venv
    > & .\.venv\Scripts\Activate.ps1
    ```

Activation de l'environnement :
```shell
(.venv) > python -m pip install -r requirements.txt
```

# Utilisation

> *Toute utilisation nécessite l'environnement d'avoir préalablement été activé.*

Dans le repertoire du projet:
```shell
(.venv) > python ./main.py
```

# Generation d'un raport d'erreur de linting

Dans le repertoire du projet:

```shell
# installation des dependences
(.venv) > python -m pip install -r requirements-dev.txt
(.venv) > flake8 --format=html --htmldir=rapport-flake
```

Le raport **HTML** est ainsi generer dans le dossier **raport-flake/index.html** à la racine du projet.