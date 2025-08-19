# PyCDCover

[dossier github]([GitHub - GerardLeRest/pycdcover: Logiciel de création de jaquettes CD](https://github.com/GerardLeRest/pycdcover))

## 1. Linux

### installation de l'environnement

- installation des paquets:
  
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip python3-venv -y
  ```

- créer l'environnement mon_env
  
  ```bash
  python3 -m venv mon_env
  ```

- activer l'environnement
  
  ```bash
  source mon_env/bin/activate
  ```

### installation des paquets

- pour installer les principaux paquets "pip": pillow, pmw, eyed3, reportlab
  Il suffit d'effectuer:
  
  ```bash
  pip install -r requirements.txt
  ```
  
   requirements.txt contient la liste des paquets du projet
  
  ```bash
  pip install requests pillow
  ```

- installer les trois autres paquets.

# 2. Windows

- Télécharger le dossier github (voir en haut de la page)
- extraire le fichier exécutable PyCDCover.exe présent dans le dossier dist
- double-cliquer sur PyCDCover.exe
- Détruire le dossier téléchargé et garder le fichier exécutable.
