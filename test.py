import os
import glob
import tkinter as tk
import argparse
from PIL import Image, ImageOps, ImageTk


def process_selected(tlist):
    # !
    pos = "true_positive"

    # Make the folder the true positives should be in
    if len(tlist) > 0:
        # Current folder
        imdir = os.path.dirname(tlist[0])
        print(imdir)
        new = os.path.join(imdir, pos)
        if not os.path.exists(new):
            os.mkdir(new)
        print(new)

    # Move selected images to the new directory
    for item in tlist:
        # Filename
        imfile = os.path.basename(item)
        print(imfile)
        new = os.path.join(imdir, pos, imfile)
        os.replace(item, new)


def add_images(path, root):
    imlist = glob.glob(path+"*.png")
    trues = []
    for i in range(0, 10):
        for j in range(0, 10):
            imindex = (i * 10) + j
            print(imindex, len(imlist))
            if imindex >= len(imlist):
                break
            p = imlist[imindex]

            im = Image.open(p)
            pim = ImageTk.PhotoImage(im)
            print("showing {}".format(p))
            label = tk.Label(root, image=pim)
            label.image = im
            label.pimage = pim
            label.path = p
            label.clicked = 0
            label.grid(row=i, column=j)
            label.bind("<Button-1>", lambda x, y=trues: select_image(x, y))

    ha = tk.Button(
        root,
        text="Done",
        command=lambda x=trues: process_selected(x)).grid(row=10, sticky="S")


def select_image(imp, trues):
    """
    Selects an image to be a true positive
    """
    if imp.widget.clicked == 1:
        print("Already clicked {}, unclicking".format(imp.widget.path))
        new_im = imp.widget.image.crop(
            (5, 5, imp.widget.image.size[0]-5, imp.widget.image.size[1]-5))
        new_pim = ImageTk.PhotoImage(new_im)
        imp.widget.configure(image=new_pim)
        imp.widget.pimage = new_pim
        imp.widget.image = new_im
        trues.remove(imp.widget.path)
        imp.widget.clicked = 0
    else:
        print("Clicked {}".format(imp.widget.path))
        new_im = ImageOps.expand(imp.widget.image, border=5, fill='red')
        new_pim = ImageTk.PhotoImage(new_im)
        imp.widget.configure(image=new_pim)
        imp.widget.pimage = new_pim
        imp.widget.image = new_im
        trues.append(imp.widget.path)
        imp.widget.clicked = 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        'folder',
        help='data folder for images to be annotated'
    )
    args = parser.parse_args()

    root = tk.Tk()
    add_images(args.folder, root)
    root.mainloop()
