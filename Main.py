#%%
#!/usr/bin/env python3

from tkinter import *
from tkmagicgrid import *
import os, io, csv, json, config
from datetime import date
from tkscrolledframe import ScrolledFrame
import tkinter as tk

configjson = json.loads(config.readConfig())

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()

    def makeLogo(self):
        myimage = tk.PhotoImage(file='icon.png')
        mylabel = tk.Label(root, image=myimage)
        mylabel.grid(row=1)
        mylabel.image = myimage

    def makeCSVTable(self):
        # Create a ScrolledFrame widget
        sf = ScrolledFrame(root, width=640, height=400)
        sf.grid(row=2, column=3)

        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(root)
        sf.bind_scroll_wheel(root)

        # Create a frame within the ScrolledFrame
        inner_frame = sf.display_widget(Frame)

        downloadedFiles = MagicGrid(inner_frame, bg_color="#1c1c1c", bg_header="#200f21", bg_shade="#171717", fg_color="#cccccc", fg_header="#cccccc", fg_shade="#cccccc")
        downloadedFiles.pack(side=TOP, anchor=NE)
        downloadedFiles.configure_column(1, weight=1)

        with io.open(os.path.expanduser(configjson["endpath"]) + '/duck/2021-01-15/analysis/playlists.csv', "r", newline='') as csv_file:
            reader = csv.reader(csv_file)
            parsed_rows = 0
            for row in reader:
                if parsed_rows == 0:
                    # Display the first row as a header
                    downloadedFiles.add_header(*row)
                else:
                    if downloaded:
                        if row[len(row)-1]:
                            downloadedFiles.add_row(*row)
            parsed_rows += 1

    def create_widgets(self):
        self.makeLogo()
        self.makeCSVTable()

    def say_hi(self):
        print("hi there, everyone!")

root = tk.Tk()
# root.overrideredirect(1)
app = Application(master=root)
app.mainloop()
# %%
