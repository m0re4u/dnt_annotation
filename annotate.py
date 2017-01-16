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
    def __init__(self, folder):
        # Start window
        self.root = tk.Tk()
        self.root.wm_title("DNT Image Annotator")
        # Install a handler for the user explicitly closing a window using the
        # window manager.
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        # Add menu for quit/next
        self.add_menu()
        # Fullscreen window
        self.expand_window()
        # Display images in the window
        self.add_images(folder)
        try:
            self.root.mainloop()
        except KeyboardInterrupt as e:
            # Clean exit of the program when pressing Ctrl-C in command line
            print("Ctrl-C pressed, exiting cleanly..")
            self.exit()

    def expand_window(self):
        """
        Make the window fullscreen.
        """
        max_w = self.root.winfo_screenwidth()
        max_h = self.root.winfo_screenheight()
        self.root.geometry('%dx%d+0+0' % (max_w, max_h))

    def add_menu(self):
        """
        Add a menu stickied at the top of the window. The quit option cleanly
        exits the program
        """
        self.menubar = tk.Menu(self.root)
        self.menubar.add_command(label="Quit", command=self.exit)
        self.root.config(menu=self.menubar)

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
            log.debug("New path: {}".format(new))
            if not os.path.exists(new):
                os.mkdir(new)
            # Create negative destination directory
            new = os.path.join(imdir, neg)
            log.debug("New path: {}".format(new))
            if not os.path.exists(new):
                os.mkdir(new)

        log.debug("tlist: {}".format(tlist))
        # Move selected images to the new directory
        for item, sel in tlist:
            # Only select filename
            imfile = os.path.basename(item)
            if sel == 1:
                new = os.path.join(imdir, pos, imfile)
            else:
                new = os.path.join(imdir, neg, imfile)
                log.debug("Moving {} to {}".format(item, new))
            # Similar to UNIX mv
            os.replace(item, new)

        self.root.destroy()

    def add_images(self, path):
        """
        Load images in a Tkinter window
        """
        # Get a list of images
        imlist = glob.glob(path + "*.png")
        selected = []
        xpos, ypos, nexty = (10, 20, 0)
        for p in imlist:
            im = Image.open(p)
            im = ImageOps.expand(im, border=3, fill='white')
            # If the next image will go beyond the screen height, exit
            if ypos + im.size[1] > self.root.winfo_screenheight() - 100:
                log.debug("Max height")
                break
            # If the next image would go beyond the screen, go to a new row
            if xpos + im.size[0] > self.root.winfo_screenwidth() - 100:
                log.debug("Next row")
                xpos = 10
                ypos += nexty + 20
                nexty = 0
            # Add the image w/ border to a Label
            pim = ImageTk.PhotoImage(im)
            label = tk.Label(self.root, image=pim)
            label.image = im
            label.pimage = pim
            label.path = p
            label.clicked = 0
            # Place image at (x,y)
            label.place(x=xpos, y=ypos)
            selected.append((label.path, label.clicked))
            label.bind(
                "<Button-1>",
                lambda x, y=selected: self.select_image(x, y)
            )
            xpos += im.size[0] + 10
            # Take the highest image height as offset for next row
            if im.size[1] > nexty:
                nexty = im.size[1]
        # Add a menu option to move to the next couple of images
        self.menubar.add_command(
            label="Next", command=lambda x=selected: self.process_selected(x))

    def select_image(self, imp, selected):
        """
        Selects a negative image to be a positive, or a positive image to be a
        negative
        """
        if imp.widget.clicked == 1:
            log.debug("Already clicked {}, unclicking".format(imp.widget.path))
            # Change border to white
            new_im = self.update_border(imp.widget.image, 'white', 3)
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
            new_im = self.update_border(imp.widget.image, 'red', 3)
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        'folder',
        help='data folder for images to be annotated'
    )
    args = parser.parse_args()

    # Set logging configuration
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')
    log = logging.getLogger(__name__)
    # Disable debug msgs from PIL
    logging.getLogger("PIL").setLevel(logging.WARNING)

    # As long as directory is not emty
    file_list = [f for f in os.listdir(args.folder)
                 if os.path.isfile(os.path.join(args.folder, f))]
    while file_list != []:
        GUI(args.folder)
