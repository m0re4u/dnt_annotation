import os
import glob
import logging
import argparse
import tkinter as tk
from PIL import Image, ImageOps, ImageTk


class GUI():
    """
    GUI that displays the to-be-clicked images
    """
    def __init__(self, folder, n):
        self.root = tk.Tk()
        self.imgn = n
        self.add_images(folder, self.root)
        self.root.wm_title("DNT Image Annotator")
        # Install a handler for the user explicitly closing a window using the
        # window manager.
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        try:
            self.root.mainloop()
        except KeyboardInterrupt as e:
            print("Ctrl-C pressed, exiting cleanly..")
            self.exit()

    def process_selected(self, tlist):
        """
        Move positive and negative images to their respective folders
        """
        # !
        pos = "positive"
        neg = "negative"
        # Make the folder the true positives should be in
        if len(tlist) > 0:
            # Current folder
            imdir = os.path.dirname(tlist[0][0])
            # Create positive destination directory
            new = os.path.join(imdir, pos)
            if not os.path.exists(new):
                os.mkdir(new)
            # Create negative destination directory
            new = os.path.join(imdir, neg)
            if not os.path.exists(new):
                os.mkdir(new)

        # Move selected images to the new directory
        for item, sel in tlist:
            # Only select filename
            imfile = os.path.basename(item)
            if sel == 1:
                new = os.path.join(imdir, pos, imfile)
            else:
                new = os.path.join(imdir, neg, imfile)
            # Similar to UNIX mv
            os.replace(item, new)

        self.root.destroy()

    def add_images(self, path, root):
        """
        Load images in a Tkinter window
        """
        # Get a list of images
        imlist = glob.glob(path+"*.png")
        selected = []
        for i in range(0, self.imgn):
            for j in range(0, self.imgn):
                imindex = (i * 4) + j
                if imindex >= len(imlist):
                    break
                p = imlist[imindex]
                im = Image.open(p)
                im = ImageOps.expand(im, border=5, fill='white')
                pim = ImageTk.PhotoImage(im)
                log.debug("showing {}".format(p))
                label = tk.Label(root, image=pim)
                label.image = im
                label.pimage = pim
                label.path = p
                label.clicked = 0
                label.grid(row=i, column=j)
                selected.append((label.path, label.clicked))
                label.bind(
                    "<Button-1>",
                    lambda x, y=selected: self.select_image(x, y)
                )

        tk.Button(
                root,
                text="Done",
                command=lambda x=selected: self.process_selected(x)
            ).grid(row=10, column=0, sticky="S")
        tk.Button(
                root,
                text="Quit",
                command=self.exit
            ).grid(row=10, column=1, sticky="E")

    def select_image(self, imp, selected):
        """
        Selects a negative image to be a positive, or a positive image to be a
        negative
        """
        if imp.widget.clicked == 1:
            log.debug("Already clicked {}, unclicking".format(imp.widget.path))
            # Change border to white
            new_im = self.update_border(imp.widget.image, 'white', 5)
            # Process and show image with updated border
            new_pim = ImageTk.PhotoImage(new_im)
            imp.widget.configure(image=new_pim)
            imp.widget.pimage = new_pim
            imp.widget.image = new_im
            # Update click variables
            selected.remove((imp.widget.path, 1))
            imp.widget.clicked = 0
            selected.append((imp.widget.path, 0))
        else:
            log.debug("Clicked {}".format(imp.widget.path))
            # Change border to red
            new_im = self.update_border(imp.widget.image, 'red', 5)
            # Process and show image with updated border
            new_pim = ImageTk.PhotoImage(new_im)
            imp.widget.configure(image=new_pim)
            imp.widget.pimage = new_pim
            imp.widget.image = new_im
            # Update click variables
            selected.remove((imp.widget.path, 0))
            imp.widget.clicked = 1
            selected.append((imp.widget.path, 1))

    def update_border(self, im, color, bsize):
        # Remove old border
        new_im = im.crop((bsize, bsize, im.size[0]-bsize, im.size[1]-bsize))
        # Place new border
        new_im = ImageOps.expand(new_im, border=bsize, fill=color)
        return new_im

    def exit(self):
        self.root.destroy()
        exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        'folder',
        help='data folder for images to be annotated'
    )
    parser.add_argument(
        'imgn',
        metavar='N',
        type=int,
        help='N x N image display'
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')
    log = logging.getLogger(__name__)

    # As long as directory is not emty
    while os.listdir(args.folder):
        GUI(args.folder, args.imgn)
