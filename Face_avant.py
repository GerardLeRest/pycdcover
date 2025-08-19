import os
import shutil
from tkinter import *
import tkinter.filedialog, tkinter.messagebox, Pmw
from math import ceil, sqrt
from PIL import Image, ImageDraw, ImageTk

formats_3 = ('bmp','gif','jpg','msp','pcx','png','ppm','xbm')
formats_4 = ('jpeg','tiff')

class Face_avant:
    def __init__(self, largeur=300, hauteur=300, env_home=None, repertoire=None):
        self.largeur = largeur
        self.hauteur = hauteur
        self.env_home = env_home                     # Ex: /home/gerard
        self.repertoire = repertoire                 # Ex: /home/gerard/PyCDCover
        self.thumbnail_path = os.path.join(self.repertoire, "thumbnails")
        self.dossier = ""
        self.fichiers = []
        self.photos = []

    def preparation_dossier(self):
        # Supprime puis recrée le dossier thumbnails
        if os.path.exists(self.thumbnail_path):
            shutil.rmtree(self.thumbnail_path)
        os.mkdir(self.thumbnail_path)

    def preparation_images(self):
        self.dossier = tkinter.filedialog.askdirectory(
            initialdir=self.env_home,
            title="Choisir le répertoire des images"
        )
        if not self.dossier:
            return

        fichiers = os.listdir(self.dossier)
        N = 1
        for fichier in fichiers:
            ext = fichier.lower().split('.')[-1]
            if ext in formats_3 or ext in formats_4:
                chemin_image = os.path.join(self.dossier, fichier)
                try:
                    im = Image.open(chemin_image)
                    out = im.resize((self.largeur, self.hauteur))
                    nom_image = f"im{N}.jpeg"
                    out.save(os.path.join(self.thumbnail_path, nom_image), "jpeg")
                    N += 1
                except Exception as e:
                    print(f"Erreur sur {fichier} : {e}")

    def preparation_assemblage_photos(self):
        self.fichiers = os.listdir(self.thumbnail_path)
        total = len(self.fichiers)
        self.NiL = ceil(sqrt(total))
        self.NiH = ceil(total / self.NiL)
        self.NiD = total % self.NiL
        self.Larg_Im_fin = self.NiL * self.largeur + (self.NiL + 1) * 10
        self.Haut_Im_fin = self.NiH * self.hauteur + (self.NiH + 1) * 10

    def assemblage_photos(self):
        try:
            im = Image.new("RGB", (self.Larg_Im_fin, self.Haut_Im_fin), "white")
            index = 0
            for j in range(self.NiH):
                for i in range(self.NiL):
                    if index >= len(self.fichiers):
                        break

                    chemin_image = os.path.join(self.thumbnail_path, self.fichiers[index])
                    into = Image.open(chemin_image)

                    if j == self.NiH - 1 and self.NiD != 0:
                        marge = int((self.Larg_Im_fin - self.NiD * (self.largeur + 10) + 10) / 2)
                        x = marge + (self.largeur + 10) * i
                    else:
                        x = 10 + (self.largeur + 10) * i

                    y = 10 + (self.hauteur + 10) * j
                    im.paste(into, (x, y, x + self.largeur, y + self.hauteur))
                    index += 1

            sortie = os.path.join(self.repertoire, "Image_thumbnails.jpeg")
            im.save(sortie, "jpeg")
            shutil.rmtree(self.thumbnail_path)

        except ZeroDivisionError:
            tkinter.messagebox.showinfo("Info", "Aucune image trouvée")

    def affichage(self, fenetre, image):
        Pmw.initialise()
        H, L = fenetre.winfo_screenheight(), fenetre.winfo_screenwidth()

        SC = Pmw.ScrolledCanvas(
            fenetre,
            usehullsize=1,
            hull_width=L-60,
            hull_height=H-60,
            canvas_bg='grey40',
            canvasmargin=10,
            borderframe=1,
            borderframe_borderwidth=3
        )
        SC.configure(vscrollmode='static', hscrollmode='static')
        SC.pack(padx=5, pady=5, expand=YES, fill=BOTH)

        SC.can = SC.interior()
        im = Image.open(image)
        photo = ImageTk.PhotoImage(im)
        SC.can.create_image(0, 0, image=photo)
        self.photos.append(photo)  # Empêche la perte de référence à l’image
        SC.resizescrollregion()




    #########################################################################     
if __name__ == "__main__":
    fen = Tk()
    face_avant = Face_avant(300, 300, "/home/gerard", "/home/gerard/PyCDCover")
    face_avant.preparation_dossier()
    face_avant.preparation_images()
    face_avant.preparation_assemblage_photos()
    face_avant.assemblage_photos()
    image_finale = os.path.join(face_avant.repertoire, "Image_thumbnails.jpeg")
    face_avant.affichage(fen, image_finale)
    fen.mainloop()