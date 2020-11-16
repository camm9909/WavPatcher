from pathlib import Path
from tkinter import * 
from tkinter import filedialog
from tkinter.scrolledtext import * 
from PIL import ImageTk,Image
import threading
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def ro_check():
  cbvar = chkvar.get()
  if cbvar == 1:
    btnrun_txt.set("Check")
    simulate = True
  else:
    btnrun_txt.set("Patch")
    simulate = False
  return simulate

def buttonstate(x):
  if x == False:
    btnrun['state'] = DISABLED
    chkbx['state'] = DISABLED
    btnbrowse['state'] = DISABLED
  else:
    btnrun['state'] = NORMAL
    chkbx['state'] = NORMAL
    btnbrowse['state'] = NORMAL

def startprocthread():
  t = threading.Thread(target=runcmd)
 # t.daemon = True
  t.start()
  return 

def totalfiles():
  totfiles = 0
  for path in Path(gui.BrowseLoc).rglob('*.wav'):
    totfiles = totfiles + 1
  return totfiles

def browsedef():
  gui.BrowseLoc = filedialog.askdirectory(initialdir="/", title="Select Music Folder...")
  if gui.BrowseLoc == '': #don't update if there are no directories selected (ie, pressed cancel)
    return None
  else:
    pass
  st.configure(state = 'normal')
  st.delete('1.0', END)
  st.insert(END, "WavPatcher 0.9.2b \n\nFolder = " + gui.BrowseLoc + "\n\nCalculating total files..\n\n")
  st.configure(state = 'disabled')
  stsbrtxt2.set(gui.BrowseLoc)

  totfiles = totalfiles()

  if totfiles == 0:
    btnrun['state'] = DISABLED
    st.configure(state = 'normal')
    st.insert(END, "No *.wav files could be found!")
    st.configure(state = 'disabled')
  else:
    btnrun['state'] = NORMAL
    st.configure(state = 'normal')
    st.insert(END, "%d *.wav files will be scanned." % totfiles)
    st.configure(state = 'disabled')

def extreport(extfiles):
  if extfiles == 0:
    st.configure(state = 'normal')
    st.insert(END, "No extensible flags detected")
    st.configure(state = 'disabled')
  else:
    pass

def runcmd():
  buttonstate(False)
  processdir = gui.BrowseLoc
  totfiles = totalfiles()
  simulate = ro_check()
  extfiles = 0
  prcfiles = 0
  if simulate == True: 
    rwmode = "rb"
  else:
    rwmode = "rb+"
  for path in Path(processdir).rglob('*.wav'):
    with open(path, rwmode) as f:
      prcfiles = prcfiles + 1
      f.seek(20, 0)
      formatID = f.read(2)
      bint = int.from_bytes(formatID, byteorder='little', signed=False)
      if bint == 65534:
        extfiles = extfiles + 1
        st.configure(state = 'normal')
        st.insert(END, "\next_flag in: %s" % path.name)
        st.configure(state = 'disabled')
        st.see(END)
        if simulate == False:
          f.seek(-2, 1)
          f.write(b'\x01\x00')
        else:
          pass
      else:
        pass
      prgbarmth = prcfiles/totfiles*100
      prgbarint = round(prgbarmth, 1)
      stsbrtxt.set("%i" % (prgbarint) + "% : " + "%d/%d (ext: %d)" % (prcfiles,totfiles,extfiles))
  st.configure(state = 'normal')
  st.insert(END, "\n\n~~~~~~~~DONE~~~~~~~ \n\n")
  st.see(END)
  extreport(extfiles)
  st.configure(state = 'disabled')
  buttonstate(True)

## Tkinter UI 

gui = Tk()
gui.resizable(0,0)
gui.title("WavPatcher 0.9.2 (BETA)")
icon = gui.iconbitmap(resource_path('img/wavico.ico'))    # Works only for NT
bgcanvas = Frame(gui)
bgcanvas.pack()

mainframe = Frame(bgcanvas)
mainframe.pack(padx=(8,4),pady=(8,4))

secframe = Frame(mainframe, width=0, height=500)
secframe.grid(padx=0,
              pady=0,
              row=0,
              column=1,
              sticky=N)

# Main text report
st = ScrolledText(mainframe,
                       wrap=WORD,
                       height=30,
                       width=56,
                       state=DISABLED,
                       takefocus=0)
                       
st.grid(padx=0, pady=0, row=0, column=0)

img = ImageTk.PhotoImage(Image.open(resource_path("img/wp_emboss.png")))
imglable = Label(secframe, image=img)
imglable.grid(row=0, pady=4)
#buttons
btnbrowse = Button(master=secframe, text="Browse...",
                   height=2, width=11,
                   command=lambda:browsedef())
btnbrowse.grid(padx=4,pady=4,row=1,column=0,sticky=N)

btnrun_txt = StringVar()
btnrun = Button(master=secframe, textvariable=btnrun_txt,
                height=2, width=11, state=DISABLED,
                command=startprocthread)
btnrun.grid(padx=4,pady=4,row=2,column=0,sticky=S)

stsbrtxt2 = StringVar()
stsbrtxt2.set("")
stsbr2 = Label(mainframe, textvariable=stsbrtxt2, bd=1, relief=GROOVE)
stsbr2.grid(padx=0, pady=0, row=1, column=0, sticky=NW+E)

stsbrtxt = StringVar()
stsbrtxt.set("")
stsbr = Label(mainframe, textvariable=stsbrtxt, bd=1, relief=GROOVE)
stsbr.grid(padx=0, pady=0, row=2, column=0, sticky=NW+E)

chkvar = IntVar()
chkbx = Checkbutton(secframe, text="Read-only",
                    onvalue = 1, offvalue = 0,
                    variable=chkvar,
                    command=lambda:ro_check())

chkbx.grid(pady=8,row=3,column=0,sticky=S)
chkvar.set(1)
ro_check()

prcfiles,extfiles = 0,0

st.configure(state = 'normal')
st.insert(INSERT, """\
  _    _            ______     _       _               
 | |  | |           | ___ \   | |     | |  0.9.2 (BETA)            
 | |  | | __ ___   _| |_/ /_ _| |_ ___| |__   ___ _ __ 
 | |/\| |/ _` \ \ / /  __/ _` | __/ __| '_ \ / _ \ '__|
 \  /\  / (_| |\ V /| | | (_| | || (__| | | |  __/ |   
  \/  \/ \__,_| \_/ \_|  \__,_|\__\___|_| |_|\___|_|
========================================================

The purpose of WavPatcher is to replace a WAV_EXTENSIBLE header subchunk sometimes found in WAV files that breaks compatibility on some equipment. This tool does not re-encode audio files but writes a 2-byte integer to invoke standard PCM. As such, this tool will not make non-standard multi-channel files compatible. It is merely intended for 2-channel (stereo) files which have otherwise compatible attributes.

It's advisable to first simulate output by selecting 'Ready-only' to check the status of files.

If you are retroactively patching files, connect your Rekordbox drive and select it via the browse dialogue.

Github: https://github.com/ckbaudio/wavpatcher
"""  + "\n")
st.see("end")
st.configure(state = 'disabled')

gui.mainloop()
sys.exit()