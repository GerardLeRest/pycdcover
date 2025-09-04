#!/usr/bin/env python

# -*- coding:Utf-8 -*-

########################################################################
# Création d'une jaquette pour CD MP3

# Copyright 2010 Gérard LE REST <gerard@infonie.fr>    
        
#   This program is free software: you can redistribute it and/or modify
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
                               
#######################################################################
# Importation de fonctions externes:
from tkinter import *
from Titres import *
from Face_arriere import * # image face arrière du cd (sans le titre)
from Face_avant import * # face avant de la pochette (sans le titre)
from Apercu import * # aperçu de la jaquette (face avant et arrière)
from Gabarit import * # création du gabarit pdf
from PIL import Image, ImageTk, ImageDraw
from reportlab.pdfgen import canvas
from os import chdir, sep, environ, path, mkdir, system
import os, sys, shutil, platform, codecs, Pmw
from os.path import exists
import tkinter.messagebox as messagebox
# cairosvg
# noms des fichiers contenant les icônes (format GIF):
textes =('Titre du CD','Récupérer les tags','Éditer les tags','Face avant de la jaquette', 'Dos de la jaquette','Aperçu','Pdf')
images =('titre.png','recuperer_tags.png','lire_tags.png','avant.png','arriere.png','apercu.png','pdf.png')

class Application(Tk):

    @staticmethod
    def _app_base_dir():
        # exe one-file : _MEIPASS ; exe one-dir : dossier de l'exe ; dev : dossier du .py
        if getattr(sys, "frozen", False):
            return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        return os.path.dirname(os.path.abspath(__file__))
    
    def __init__(self):
        Tk.__init__(self) # constructeur de la classe parente
        self.rep_programme = self._app_base_dir()
        self.L_devant,self.H_devant=1200,1200 # dimensions de l'image de devant
        self.L_back_cover,self.H_back_cover=1380,1180 # dimensions de l'image de derrière
        self.H_image_reduite=450
        # listes des boutons
        self.boutons=[]
        # variables de création
        self.titre =0
        self.images=0
        self.tag=0
        # initialisation du menu fichier
        self.fichier = None  
        # création de l'interface
        self.menus()
        self.barre_outils()
        self.canevas()
        self.photos=[]  # mémorisation pour éviter l'effacement image (bug ImageTk)
        self.coefficient=72.0/254 # coef pour pdf (résolution=72ppp; 1 pouce=254mm)
        # gestion du dossier personnel
        if 'HOME' in os.environ:
            self.envHome = os.environ['HOME']
        elif 'HOMEDRIVE' in os.environ and 'HOMEPATH' in os.environ:
            self.envHome = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        os.chdir(self.envHome)
        # effacement du dossier ~/PyCDCover précédent:
        if exists("PyCDCover"):
            shutil.rmtree("PyCDCover")
        os.mkdir("PyCDCover")
        self.repertoire = self.envHome + os.sep + "PyCDCover"
       
    def menus(self):
        """création de l'interface graphique"""
        # Création de la barre de menu (objet Menu):
        menu1 = Menu(self)
        # menu fichier:
        self.fichier = Menu(menu1, tearoff=0)
        menu1.add_cascade(label="Fichier",menu=self.fichier)
        self.fichier.add_command(label="Titre", command=self.titres_CD)
        self.tags = Menu(self.fichier, tearoff=0)
        self.fichier.add_cascade(label="Tags",menu=self.tags)
        self.tags.add_command(label="Créer", command=self.recuperer_tags)
        self.tags.add_command(label="Éditer", command=self.edition, state="disabled")
        self.fichier.add_command(label="Face avant", command=self.face_avant, state="disabled")
        self.fichier.add_command(label="Dos", command=self.face_arriere, state="disabled")
        self.fichier.add_separator()
        self.fichier.add_command(label="Apercu", command=self.apercu_jaquette, state="disabled")
        self.fichier.add_command(label="pdf", command=self.pdf, state="disabled")
        self.fichier.add_separator()
        self.fichier.add_command(label="Quitter", command=self.quit)
        # menu aide
        infos = Menu(menu1, tearoff=0)
        menu1.add_cascade(label="Aide",menu=infos)
        infos.add_command(label="A propos",command=self.a_propos)
        # afficher le menu
        self.config(menu=menu1)

    def barre_outils(self):
        # Création de la barre d'outils
        fonctions = [self.titres_CD, self.recuperer_tags,
                     self.edition,self.face_avant, self.face_arriere, self.apercu_jaquette, self.pdf]

        self.toolbar = Frame(self, bd=4)
        self.toolbar.pack(expand=YES, fill=X)

        nBou = len(images)
        self.photoI = [None] * nBou
        self.boutons = []

        # dossier des icônes (images/icones32x32 sous le répertoire du programme)
        icons_dir = os.path.join(self.rep_programme, "images", "icones32x32")

        for b in range(nBou):
            img_path = os.path.join(icons_dir, images[b])
            im = Image.open(img_path)
            self.photoI[b] = ImageTk.PhotoImage(im)  # garder une réf dans self.photoI

            bouton = Button(self.toolbar, image=self.photoI[b], relief=GROOVE, command=fonctions[b])
            self.boutons.append(bouton)
            bouton.pack(side=LEFT)

            bulle = Pmw.Balloon(self)
            bulle.bind(bouton, textes[b])

            if b > 1:  # désactivation initiale si besoin
                bouton.config(state="disabled")
        
    def canevas(self):
        # Nouveau conteneur pour aligner proprement les canvas
        cadre = Frame(self, bg="white")
        cadre.pack()

        # Canevas pour la face avant
        self.can1 = Canvas(cadre, width=self.H_image_reduite, height=self.H_image_reduite, bg="white", bd=0, highlightthickness=0)
        self.can1.pack(side=LEFT, padx=0, pady=0)
        self.can1.bind("<Double-Button-1>", lambda event: self.zoom('Devant.jpeg', 'Face avant de la jaquette'))

        # Canevas pour la face arrière
        L = int(self.H_image_reduite * 1.169491)
        self.can2 = Canvas(cadre, width=L, height=self.H_image_reduite, bg="white", bd=0, highlightthickness=0)
        self.can2.pack(side=RIGHT, padx=0, pady=0)
        self.can2.bind("<Double-Button-1>", lambda event: self.zoom('Dos.png', 'Dos de la jaquette'))

        # blocage du redimensionnement de la fenêtre principale
        self.resizable(width=False, height=False)

        
    def titres_CD(self):
        """création des images des titres horizontal et verticaux"""
        titre = Titre(self.L_devant, self.H_back_cover, self.rep_programme)
        chdir(self.repertoire)
        #titre.titre_horizontal()
        #outH = titre.encadrement_titre()
        outH = titre.titre_horizontal()
        outH.save("TitreH.png", "png")
        outV1 = titre.titre_vertical1()
        outV1.save("TitreV1.png", "png")
        outV2 = titre.titre_vertical2()
        outV2.save("TitreV2.png", "png")
          
    def face_avant(self):
        """création de l'image de la face avant - Image_thumbnails.png"""
        # Instanciation de la classe Face_avant
        fa = Face_avant(150, 150, env_home=self.envHome, repertoire=self.repertoire) 
        fa.preparation_assemblage_photos()
        fa.assemblage_photos()
        self.boutons[4].configure(state="normal")
        self.fichier.entryconfig("Dos", state="normal")
        

    def recuperer_tags(self):
        """création du fichier tag.csv"""
        self.tg=Face_arriere()
        self.tg.preparation_dossier_tags()
        self.tg.tags()
        # édition des tags
        self.boutons[2].configure(state="normal")
        self.tags.entryconfig("Éditer", state="normal")
        # face avant de la pochette
        self.boutons[3].configure(state="normal")
        self.fichier.entryconfig("Face avant", state="normal")

    def edition(self):
        """édition du fichier de tags"""
        chdir(self.repertoire)
        if exists("tags.txt")==True:
            top_fenetre=Toplevel()  # u"création d'une nouvelle fenêtre"
            top_fenetre.title("tags.txt")
            # blocage dimensionnement fenêtre
            top_fenetre.resizable(width=False, height=False)
            self.zone_texte = Pmw.ScrolledText(top_fenetre,usehullsize = 1,hull_width = 300,
                hull_height = 300,text_padx =10, text_pady =10, text_font='Times 11 normal',
                text_bg ='white')
            self.zone_texte.pack()
            # fichier=codecs.open("tags.txt",'r',locale.getdefaultlocale()[1])   #ouvrir un fichier encode en "encodgae du syst d'exploitation"
            fichier=open("tags.txt",'r')
            lignes=fichier.readlines()     # les lignes du fichier sont en unicode
            fichier.closed  
            for i in lignes:               # ajout des lignes dans la zone texte
                self.zone_texte.appendtext(i)
            boutong = Button(top_fenetre, text="Enregistrer", command=self.modif_tags)
            boutong.pack(side=LEFT,padx=2, pady=2)
            boutond = Button(top_fenetre, text="Quitter", command=top_fenetre.destroy)
            boutond.pack(side=RIGHT,padx=2, pady=2)
        else:
            tkinter.messagebox.showinfo("Info","Le fichier texte tags.txt n'a pas été créé")
    

    def modif_tags(self):
        """Enregistrement des modifications des tags"""
        with open("tags.txt", "w", encoding="utf-8") as fichier:
            fichier.write(self.zone_texte.get("1.0", "end"))

             

    def face_arriere(self):
        """création de Imagefrom os import chdir _Back_Cover.png"""
        try:
            # Instanciation de la classe Face_arriere
            self.tg=Face_arriere()
            self.tg.preparation_dossier_image()
            self.tg.creation_image()
            self.boutons[5].configure(state="normal")
            self.fichier.entryconfig("Apercu", state="normal")
            self.boutons[6].configure(state="normal")
            self.fichier.entryconfig("pdf", state="normal")
        except (IOError):
            messagebox.showinfo("Info","tags non récupérés")

    def apercu_jaquette(self):
        """création des apercus des couvertures à l'écran"""
        apercu = Apercu(self.photos, self.H_image_reduite, self)
        apercu.creer_image_avant(self.repertoire, self.can1, self.L_devant, self.H_devant)
        apercu.creer_image_arriere(self.can2, self.L_back_cover, self.H_back_cover)


    def face(self,image_originale,largeur, hauteur):
        """création des images (face avant et face_arrière sans titres verticaux) à imprimer"""
        chdir(self.repertoire)
        im=Image.new("RGB", (largeur,hauteur), "white")
        draw = ImageDraw.Draw(im)
        into1=Image.open("TitreH.png")
        L,H=into1.size
        marge_x=(largeur-L)/2
        im.paste(into1,(0+int(marge_x),0,L+int(marge_x),H))
        im2=Image.open(image_originale)
        # redimensionnement
        L,H=im2.size
        Lf,Hf=float(L),float(H)
        rapport=Hf/Lf        # rapport hauteur/longueur de l'image
        if (L==self.L_back_cover) and (H<=930):
            out=im2 #image Image_Back_Cover.png
        elif Hf>Lf:
            L_modifie=int(960/rapport)
            out=im2.resize((L_modifie,960))
        else:
            H_modifie=int(960*rapport)
            out=im2.resize((960,H_modifie))
        L,H=out.size
        marge_x=(largeur-L)/2
        im.paste(out,(0+int(marge_x),220,L+int(marge_x),H+220))
        return im


    def zoom(self,image,titre):
        """zoom de l'aperçu"""
        chdir(self.repertoire)
        if exists(image)==True:
            fen_zoom=Toplevel()
            fen_zoom.title(titre)
            H,L=self.winfo_screenheight(), self.winfo_screenwidth() # résolution de l'écran
            Sc=Pmw.ScrolledCanvas(fen_zoom,
                 usehullsize =1, hull_width =(L-60), hull_height=(H-60),
                 borderframe =1, borderframe_borderwidth =3)
        # configuration des barres de défilement:         
            Sc.configure(vscrollmode ='dynamic', hscrollmode ='dynamic')        
            Sc.pack(padx =5, pady =5, expand =YES, fill =BOTH)
            # Ajout de l'image
            Sc.can=Sc.interior()        # accès au composant canevas
            im=Image.open(image)
            photo_dos=ImageTk.PhotoImage(im)   
            Sc.can.create_image(0,0,image=photo_dos)
            self.photos.append(photo_dos) # mémorisation - bug ImageTk    
            Sc.resizescrollregion()
        else:
            messagebox.showinfo("Info","L'image de la face n'a pas été créée.")
        

    def pdf(self):
        """impression de la jaquette"""
        chdir(self.repertoire)
        self.creation_gabarit()
        if platform.system() == "Windows":
        # windows
            os.startfile("image_impression.pdf") # ouverture du fichier pdf
        else:
        # linux
            os.system('xdg-open "image_impression.pdf" 2>/dev/null')  # Ouverture du fichier PDF
    

    def creation_gabarit(self): # pas de self, à cause de 
        """creation d'un gabarit d'impression: deux images avant et arriere + titres vericaux + trace decoupage dans une page PDF"""
        gabarit = Gabarit(self.coefficient)
        gabarit.creation_canvas()
        gabarit.creation_lignes_decoupage()
        gabarit.insertion_images(self.L_devant, self.H_devant, self.L_back_cover, self.H_back_cover)
       
       
    def a_propos(self):
        """fenêtre indiquant l'auteur et le type de licence"""
        fen_propos=Toplevel()
        fen_propos.title("À propos de: ")
        fram1=Frame(fen_propos,padx=5,pady=5)
        fram1.pack()
        Message(fram1, width=200, aspect=50, justify=CENTER,pady=5, 
                text=" PyCDCover\n\nCopyrigth G LE REST 2010-2025.\n"\
                "Licence GNU-GPL\n\n Version 0.18.0 \n\n https://logiciels-python.pm/pycdcover/").pack()
        bou = Button(fram1,text ="Quitter", 
                     command =fen_propos.destroy).pack()
        #blocage du dimensionnement de la fenêtre
        fen_propos.resizable(width=False, height=False)


#########################################################################      

if __name__ == "__main__":
    app = Application()
    app.title('PyCDCover')
    app.mainloop()
