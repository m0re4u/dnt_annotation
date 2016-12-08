import os
import glob
import tkinter as tk
import argparse
from PIL import Image, ImageOps, ImageTk


def add_images(path, root):
    imlist = glob.glob(path+"*.png")
    print(imlist)
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
            label.bind("<Button-1>", lambda x: select_image(x))


def select_image(imp):
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
        imp.widget.clicked = 0
    else:
        print("Clicked {}".format(imp.widget.path))
        new_im = ImageOps.expand(imp.widget.image, border=5, fill='red')
        new_pim = ImageTk.PhotoImage(new_im)
        imp.widget.configure(image=new_pim)
        imp.widget.pimage = new_pim
        imp.widget.image = new_im
        imp.widget.clicked = 1

    # pos = "true_positive"
    # # Folder
    # imdir = os.path.dirname(imp)
    # print(imdir)
    # # Filename
    # imfile = os.path.basename(imp)
    # print(imfile)
    # new = os.path.join(imdir, pos, imfile)
    # if not os.path.exists(new):
    #     os.mkdir(os.path.dirname(new))
    # os.replace(imp, new)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('folder', help='data folder for images to be annotated')
    args = parser.parse_args()

    root = tk.Tk()
    add_images(args.folder, root)
    root.mainloop()
