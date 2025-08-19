from tkinter import *      
import tkinter.simpledialog, os
from PIL import Image, ImageFont, ImageDraw


class Titre:

    def __init__(self, L_devant, H_back_cover, rep_programme):
        self.titre = ""
        self.L_devant = L_devant
        self.rep_programme = rep_programme
        self.H_back_cover = H_back_cover
        self.x = 0 # position x de l'élément à placer
        self.y = 0 # position y de l'élément à placer
        
        
    def titre_horizontal(self, parent=None) : # parent: fenêtre parente
        """création de l'image horizontale"""

        # création de la boite de dialogue
        self.titre=tkinter.simpledialog.askstring(title="titre", prompt="Saisir le nom du CD :",parent=parent)    

        # titre horizontal
        self.imageH=Image.new("RGB", (self.L_devant,220), "white")
        self.imageH.save("TitreH.png", "png")
        self.draw = ImageDraw.Draw(self.imageH)
        police1 = self.rep_programme+ os.sep + "polices" +os.sep+"FreeSerif.ttf"
        taille=60
        self.font1 = ImageFont.truetype(police1,taille)
        taille=taille+1
        self.font1 = ImageFont.truetype(police1,taille)
        self.x = (self.L_devant - (self.draw.textbbox((0, 0), self.titre, font=self.font1)[2] - self.draw.textbbox((0, 0), self.titre, font=self.font1)[0])) / 2
        self.y=60
        self.draw.text((self.x,self.y),self.titre, fill="black",anchor=None, font=self.font1)
        return self.imageH

    def encadrement_titre(self) -> Image.Image:
        """ Création de de l'encadrement du titre horizontal"""
        # tracé de cinq rectangles = rectangle intérieur épais
        for e in range(4):
            bbox = self.draw.textbbox((self.x, self.y), self.titre, font=self.font1)
            self.draw.rectangle([(bbox[0]-10-e, bbox[1]-10-e), (bbox[2]+10+e, bbox[3]+10+e)], outline="#4e3728")
           
        # Tracé du rectangle extérieur
        bbox = self.draw.textbbox((self.x, self.y), self.titre, font=self.font1)
        self.draw.rectangle([(bbox[0] - 16, bbox[1] - 16), (bbox[2] + 16, bbox[3] + 16)], outline="#4e3728")
        ##self.imageH.save("TitreH.png", "png") # sauvegarde de l'image
        return self.imageH
       

    def titre_vertical1(self) -> Image.Image:
        """Création du premier titre vertical"""
        # titre vertical
        self.imageV=Image.new("RGB", (self.H_back_cover,60), "white")
        self.draw = ImageDraw.Draw(self.imageV)
        police1 = self.rep_programme+os.sep+"polices"+os.sep+"FreeSerif.ttf"
        self.font1 = ImageFont.truetype(police1,40)
        self.draw.text((40,5),self.titre, fill="black",anchor=None, font=self.font1)
        out1 = self.imageV.rotate(90, expand=True)
        return out1
         
    def titre_vertical2(self) ->Image.Image:
        """Création du deuxième titre vertical"""
        # titre vertical2
        out2=self.imageV.rotate(270, expand=True)
        return out2