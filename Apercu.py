from tkinter import Canvas, messagebox, NW
from os import chdir
from os.path import exists
from PIL import Image, ImageTk

class Apercu:

    def __init__(self, photos, H_image_reduite, application):
        self.affichage = 0
        self.app = application  # pour accéder à la méthode "face" de la classe Application
        self.photos = photos # mémorisation des images
        self.H_image_reduite = H_image_reduite


    def creer_image_avant(self, repertoire, canevas1: Canvas, L_devant, H_devant):
        """création de l'image de la face avant de la jaquette"""
        
        chdir(repertoire)
        affichage=0 # nbre d'affichage de la boite de dialogue "titre manquant"
        if exists("Image_thumbnails.jpeg") and exists("TitreH.png"):
            self.Devant=self.app.face("Image_thumbnails.jpeg",L_devant, H_devant)
            self.Devant.save("Devant.jpeg","jpeg")
            # création et insertion de l'apercu de l'image "Devant.png"
                # redimensionnement
            im=Image.open("Devant.jpeg")
            out=im.resize((self.H_image_reduite, self.H_image_reduite))  
                # insertion de l'aprecu dans le label
            photo1 = ImageTk.PhotoImage(out)
            canevas1.create_image(0,0,anchor = NW,image=photo1)
            self.photos.append(photo1)    # mémorisation pour éviter l'effacement image (bug ImageTk)
        if exists("Image_thumbnails.jpeg") == False:
            messagebox.showinfo("info","face avant de la jaquette non créée")
        if exists("TitreH.png") == False:
            messagebox.showinfo("Info","titre manquant")
            self.affichage=1
        

    def creer_image_arriere(self, canevas2:Canvas, L_back_cover, H_back_cover): 
        """création de l'image de la face arrière de la jaquette"""   
        if exists("Image_Back_Cover.png") == True and exists("TitreH.png") == True:
            # création de l'image "dos de la jaquette"
            self.Dos=self.app.face("Image_Back_Cover.png",L_back_cover,H_back_cover)
            self.Dos.save("Dos.png","png")
            # création et insertion de l'apercu de l'image "dos"
                # redimensionnement    
            im=Image.open("Dos.png")
            L,H=im.size
            Lf,Hf=float(L),float(H)
            rapport=Lf/Hf
            out=im.resize((int(self.H_image_reduite*rapport),self.H_image_reduite))  
                # insertion de l'aprecu dans le canevas
            photo2 = ImageTk.PhotoImage(out)
            canevas2.create_image(0,0,anchor = NW,image=photo2)
            self.photos.append(photo2)    # mémorisation pour éviter l'effacement image (bug ImageTk)
        if exists("Image_Back_Cover.png") == False:
            messagebox.showinfo("Info","Pour afficher le dos de la jaquette, il faut récupérer les tags et créer l'image correspondante") 
        if (self.affichage==0) and (exists("TitreH.png")==False):
            messagebox.showinfo("Info","titre manquant")