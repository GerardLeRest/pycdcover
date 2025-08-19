from reportlab.pdfgen import canvas
from PIL import Image
import tkinter 

class Gabarit:

    def __init__(self, coefficient):
        self.coefficient = coefficient


    def creation_canvas(self):
        self.canv=canvas.Canvas("image_impression.pdf") # instantation d'un objet canevas reportlab
        self.canv.setLineWidth(1)
        self.canv.setDash(6,3)
     
    def creation_lignes_decoupage(self):
        """creation d'un gabarit d'impression: deux images avant et arriere + titres vericaux + trace decoupage dans une page PDF"""
        # création des lignes en 
        # pointillés de découpage
            # lignes verticales
        origines=[(300*self.coefficient,0),(360*self.coefficient,0),(1560*self.coefficient,0),(1740*self.coefficient,0),(1800*self.coefficient,0)]
        H=2970*self.coefficient
        for i in origines:
            xorigine,yorigine=i[0],i[1]
            self.canv.line(xorigine,yorigine,xorigine,yorigine+H)
        # lignes horizontales
        origines=[(0,2860*self.coefficient),(0,1660*self.coefficient),(0,480*self.coefficient)]
        L=2100*self.coefficient
        for i in origines:
            xorigine,yorigine=i[0],i[1]
            self.canv.line(xorigine,yorigine,xorigine+L,yorigine)   
           
    def insertion_images(self, L_devant, H_devant, L_back_cover, H_back_cover):

        try:
            # insertion de l'image Devant.png
            xorigine,yorigine=360*self.coefficient,1660*self.coefficient
            self.canv.drawImage("Devant.jpeg",xorigine,yorigine, width=L_devant*self.coefficient,height=H_devant*self.coefficient,mask=None)
            # insertion de l'image Dos.png
            into=Image.open("Dos.png")
            L,H=into.size
            xorigine,yorigine=360*self.coefficient,480*self.coefficient
            self.canv.drawImage("Dos.png",xorigine,yorigine, width=L_back_cover*self.coefficient,height=H_back_cover*self.coefficient,mask=None)
            # insertion des titres verticaux
            xorigine,yorigine=300*self.coefficient,480*self.coefficient
            self.canv.drawImage("TitreV1.png",xorigine,yorigine, width=60*self.coefficient,height=H_back_cover*self.coefficient,mask=None)
            xorigine,yorigine=1740*self.coefficient,480*self.coefficient
            self.canv.drawImage("TitreV2.png",xorigine,yorigine, width=60*self.coefficient,height=H_back_cover*self.coefficient,mask=None)
            # tracé des rectangles en traits pleins
            self.canv.setDash(1,0)
            self.canv.rect(360*self.coefficient,1660*self.coefficient,L_devant*self.coefficient,H_devant*self.coefficient)
            self.canv.rect(300*self.coefficient,480*self.coefficient,60*self.coefficient,H_back_cover*self.coefficient)
            self.canv.rect(1740*self.coefficient,480*self.coefficient,60*self.coefficient,H_back_cover*self.coefficient)
            self.canv.rect(360*self.coefficient,480*self.coefficient,L_back_cover*self.coefficient,H_back_cover*self.coefficient)
            self.canv.showPage()    # sauvegarde de la page courante
            self.canv.save()    # enregistrement du fichier et fermeture du canveas reportlab
        except IOError:
            tkinter.messagebox.showinfo(title="Info",message="Toutes les images de la jaquette n'ont pas été créées")
