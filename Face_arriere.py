#!/usr/bin/env python
# -*- coding:Utf-8 -*-

############################################
# Creation image et fichier contenant chansons, auteur et titre CD MP3  


# Copyright 2010 Gerard LE REST <gerard@infonie.fr>    
        
# This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
                                                     
############################################


#######################################################################
# Importation de fonctions externes:

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar
#from ID3 import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
from os import chdir, listdir, environ, mkdir, sep 
from os.path import exists, isdir, join
from mutagen import File as MutaFile

import Pmw, tkinter.filedialog, glob, sys, os, requests, webbrowser, urllib.parse, csv
import io
import re


class Face_arriere:
    """creation de la page arrière de la jaquette d'un CD"""
    def __init__(self,repertoire_init="/media/gerard"):
        self.repertoire_init=repertoire_init
        self.envHome=""  # dossier personnel
        self.lecteur=""  # dossier du lecteur CD
        # répertoire du programme : _MEIPASS en one-file, sinon dossier du .py
        if getattr(sys, "frozen", False):
            self.repertoire_fichier = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            self.repertoire_fichier = os.path.dirname(os.path.abspath(__file__))
        self.repertoire_travail=""   # repertoire de travail
        self.dossiers=[]
        # gestion du dossier personnel
        if 'HOME' in environ:
            self.envHome = environ['HOME']
        elif 'HOMEDRIVE' in environ and 'HOMEPATH' in environ:
            self.envHome = join(environ['HOMEDRIVE'],
                            environ['HOMEPATH'])        
        
    def preparation_dossier_tags(self):
        " creation du fichier tags.txt conrenant toutes les lignes à editer"
        self.lecteur=tkinter.filedialog.askdirectory(initialdir=self.repertoire_init, title="choisir le répertoire du lecteur CD")
        chdir (self.lecteur)
        elements=listdir(self.lecteur)
        self.dossiers=[]
        # recuperation des dossiers
        for i in elements:
            if isdir(i)==True:
                self.dossiers.append(i) 
        print (self.dossiers)
        # création de ~/PyCDCover/:
        chdir (self.envHome)
        if exists("PyCDCover")==False:
            mkdir ("PyCDCover")
        self.repertoire_travail=self.envHome+sep+"PyCDCover"
        chdir(self.repertoire_travail)

    def tags(self):
        """préparation des dossiers"""
        # création du fichier tags.txt
        self.fichier=open("tags.txt",'w')
        messagebox.showinfo("Information", "Chargement en cours… (1–2 min)")
        chdir (self.lecteur)
        for i in self.dossiers:
            fichiers_sous_dossiers=listdir(i)
            chdir(i)
            # détection de sous-dossiers
            sous_dossiers=[]
            for j in fichiers_sous_dossiers:
                if isdir(j):
                    sous_dossiers.append(j)
            # s'il existe des sous-dossiers dans le dossier:
            if sous_dossiers!=[]:
                for j in sous_dossiers:
                    print(j)
                    chdir (j)
                    self.ecriture_album_fichier()
                    chdir(self.lecteur+sep+i)
            # s'il existe des *.mp3 dans le dossier et non des sous-dossiers
            if sous_dossiers==[]:
                self.ecriture_album_fichier()
            chdir(self.lecteur)
        self.fichier.close()
        chdir(self.repertoire_travail)
        messagebox.showinfo("Information", "Terminé !")


    def ecriture_album_fichier(self):
        """écriture des lignes de l'album dans le fichier"""
        chansons = sorted(glob.glob("*.mp3"))

        try:
            if not chansons:
                self.fichier.write("Aucun fichier MP3 trouvé\n\n")
                return

            # --- récupérer artiste/album/année/genre de façon robuste ---
            def _get(au, key, default=""):
                return (au.get(key, [default])[0] if au else default) or default

            # recherche de la première chanson valable
            tags0 = None
            for s in chansons:
                try:
                    tags0 = MutaFile(s, easy=True)
                    if tags0:
                        break
                except Exception:
                    pass

            artiste = _get(tags0, "artist", "Inconnu")
            album   = _get(tags0, "album",  "Inconnu")
            date_raw = (_get(tags0, "originaldate") or _get(tags0, "date") or _get(tags0, "year") or "")
            annee = date_raw[:4] if date_raw[:4].isdigit() else "Inconnue"
            genre = _get(tags0, "genre", "Inconnu")

            # Affichage + pochette (inchangé)
            print(artiste, ": ", album); print(annee); print(genre)
            try:
                self.enregistrer_pochette(artiste, album)
            except Exception as e:
                print(f"Erreur enregistrer_pochette : {e}")

            # Entête -> on utilise self.fichier (déjà ouvert par tags())
            self.fichier.write(f"C: {artiste} \n")
            self.fichier.write(f"A: {album} \n")
            self.fichier.write(f"{annee} - {genre} \n")

        except Exception as e:
            print("Erreur lecture tags de l'album :", e)
            self.fichier.write("ERROR\n")

        # Lignes des chansons
        for i, j in enumerate(chansons, 1):
            try:
                au = None
                try:
                    au = MutaFile(j, easy=True)
                except Exception:
                    au = None

                titre = (au.get("title", [""])[0] if au else "") if au else ""
                if not titre:
                    # fallback : titre depuis le nom de fichier
                    base = os.path.splitext(os.path.basename(j))[0]
                    # tente "NN - Titre"
                    m = re.match(r"\s*(\d{1,2})\s*[-_. ]\s*(.+)", base)
                    titre = m.group(2) if m else base

                track = (au.get("tracknumber", [""])[0] if au else "")
                piste = track.split("/", 1)[0].strip() if track else ""
                if piste.isdigit():
                    piste = str(int(piste))  # "02" -> "2"

                num = piste or str(i)
                # À l'écran
                print(f"{num} - {tkinter}\n")
                #dans le fichier
                self.fichier.write(f"{num} - {titre}\n")

            except OSError as e:
                # ex: [Errno 5] Input/output error → continuer
                print(f"Erreur avec le fichier {j} : {e}")
                self.fichier.write(f"{i} - ERROR\n")
            except Exception as e:
                print(f"Erreur avec le fichier {j} : {e}")
                self.fichier.write(f"{i} - ERROR\n")

        self.fichier.write("\n")  # séparation entre albums


    def enregistrer_pochette(self, artist, album, target_px=512):
        """Télécharge la pochette et redimensionne à target_px."""
        outdir = os.path.join(self.envHome, "PyCDCover", "thumbnails")
        os.makedirs(outdir, exist_ok=True)

        safe = "".join(c for c in f"{artist} - {album}" if c not in '\\/:*?"<>|').strip()
        dest = os.path.join(outdir, f"{safe}.jpg")

        if os.path.exists(dest):  # cache
            return dest

        # Recherche release-group
        r = requests.get(
            "https://musicbrainz.org/ws/2/release-group/",
            params={"query": f'artist:"{artist}" AND release:"{album}"', "fmt": "json"},
            headers={"User-Agent": "PyCDCover/1.0"}, timeout=7
        )
        groups = r.json().get("release-groups", [])
        if not groups:
            webbrowser.open(
                f"https://musicbrainz.org/search?query={urllib.parse.quote_plus(artist+' '+album)}&type=release_group"
            )
            return None

        mbid = groups[0]["id"]

        # Téléchargement de l’image
        img = requests.get(
            f"https://coverartarchive.org/release-group/{mbid}/front",
            headers={"User-Agent": "PyCDCover/1.0"}, timeout=7
        )
        if img.status_code != 200:
            webbrowser.open(f"https://musicbrainz.org/release-group/{mbid}")
            return None

        # Redimensionnement
        im = Image.open(io.BytesIO(img.content)).convert("RGB")
        im.thumbnail((target_px, target_px))
        im.save(dest, "JPEG", quality=85)

        return dest

    def preparation_dossier_image(self):
        "création de l'image à partir du fichier texte"
        from os import sep, chdir
        self.repertoire_travail = self.envHome + sep + "PyCDCover"
        self.police1 = self.repertoire_fichier + sep + "polices" + sep + "LiberationMono-Regular.ttf"
        self.police2 = self.repertoire_fichier + sep + "polices" + sep + "LiberationMono-Bold.ttf"
        self.police3 = self.repertoire_fichier + sep + "polices" + sep + "LiberationMono-BoldItalic.ttf"
        # créer l'image
        chdir(self.repertoire_travail)
        self.im = Image.new("RGB", (1380, 930), "white")
        self.im.save("Image_Back_Cover.png", "png")
        self.draw = ImageDraw.Draw(self.im)
        # récupérer les lignes du fichier
        with open("tags.txt", 'r') as fichier:
            self.lignes = fichier.readlines()
        ## calcul du nombre de lignes
        self.nbreLignes = len(self.lignes)
        self.nbreColonnes = 3
        # Taille automatique approximative + sécurité (-2)
        self.taille = 890 / ((self.nbreLignes + 1) / self.nbreColonnes) - 2
        if self.taille > 22:
            self.taille = 22
        # Chargement des polices
        self.font1 = ImageFont.truetype(self.police1, int(self.taille))
        self.font2 = ImageFont.truetype(self.police2, int(self.taille))
        self.font3 = ImageFont.truetype(self.police3, int(self.taille))

    def creation_image(self):
        """Créer l’image de l’arrière du CD avec troncature des titres longs"""

        x, y = 20, 20
        largeur_colonne = 1340 / self.nbreColonnes - 10
        lignes_finales = []

        for ligne in self.lignes:
            ligne = ligne.strip()
            if ligne.startswith("C: "): # auteur
                texte = ligne[3:]
                texte = self.raccourcir_ligne_proprement(texte, self.font2, largeur_colonne)
                lignes_finales.append(("C", texte))
            elif ligne.startswith("A: "): # titre de l'album
                texte = ligne[3:]
                texte = self.raccourcir_ligne_proprement(texte, self.font3, largeur_colonne)
                lignes_finales.append(("A", texte))
            else: # texte
                texte = self.raccourcir_ligne_proprement(ligne, self.font1, largeur_colonne)
                lignes_finales.append(("T", texte))
        # Dessin
        for type_ligne, texte in lignes_finales:
            if type_ligne == "C":
                self.draw.text((x, y), texte, fill="black", font=self.font2)
            elif type_ligne == "A":
                self.draw.text((x, y), texte, fill="darkblue", font=self.font3)
            else:  # titre
                self.draw.text((x, y), texte, fill="#4d4d4d", font=self.font1)
            y += self.taille + 2
            if y > 910 - self.taille:
                y = 20
                x += 1340 / self.nbreColonnes
        self.im.save("Image_Back_Cover.png", "png")

    def raccourcir_ligne_proprement(self, texte, police, largeur_max):
        """Tronque proprement une ligne trop longue avec '...' coupé entre les mots"""
        if self.draw.textbbox((0, 0), texte, font=police)[2] <= largeur_max:
            return texte  # Pas besoin de tronquer

        mots = texte.split()
        texte_court = ""

        for mot in mots:
            if self.draw.textbbox((0, 0), texte_court + " " + mot + "...", font=police)[2] > largeur_max:
                break
            texte_court += (" " if texte_court else "") + mot

        return texte_court.strip() + "..."
    
    def affichage(self,fenetre,image):
        """visualisation de l'aperçu"""
        Pmw.initialise()
        SC=Pmw.ScrolledCanvas(fenetre,usehullsize =1, hull_width =900, hull_height =600,  
                       canvas_bg ='grey40', canvasmargin =10,borderframe =1, borderframe_borderwidth =3)
        # configuration des barres de défilement        
        SC.configure(vscrollmode ='static', hscrollmode ='static')        
        SC.pack(padx =5, pady =5, expand =YES, fill =BOTH)
        SC.can = SC.interior()        # accès au composant canevas
        # Ajout de l'image Dos.png :    
        im=Image.open(image)
        photo= ImageTk.PhotoImage(im)    
        SC.can.create_image(0,0,image=photo)
        self.photo=photo   # mémorisation pour eviter effacement image (bug ImageTk) 
        SC.resizescrollregion()

###############################################################
        
if __name__ == "__main__":
    "creation des groupes"
    # creation de la fenetre et cration de l'objet "conteneur"
    fenetre=Tk()
    face_arriere = Face_arriere()
    face_arriere.preparation_dossier_tags()
    face_arriere.tags()
    face_arriere.preparation_dossier_image()
    face_arriere.creation_image()
    face_arriere.affichage(fenetre,"Image_Back_Cover.png")
    fenetre.mainloop()
