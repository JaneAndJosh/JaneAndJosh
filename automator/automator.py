'''
Luke's Travel Blog Automator GUI Tool
7/24/2022 
'''
#***********************************IMPORT***********************************************
import os
import shutil
from tkinter import *
from PIL import Image
#***********************************FUNCTION DEFINITIONS*********************************

# Confirm proper directory structure before running anything.
# If the directory does not exist, notify the user and create it.
# Here are the directories that need to be checked relative to the script's location:
# ../gallery/archive/
# ../gallery/albums/
def confirm_dir():
    # Set the current directory to the location of the script:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.exists('../gallery/archive/'):
        print('Weird. "../gallery/archive/" does not exist. Please confirm that the directory structure matches the github repo.')
        #os.mkdir('../gallery/archive/')
    if not os.path.exists('../gallery/albums/'):
        print('Weird. "../gallery/albums/" does not exist. Please confirm that the directory structure matches the github repo.')
        #os.mkdir('../gallery/albums/')
        
# Make the yaml insertions to the necessary files
def yaml_insert(abbr, archive_path, gallery_path, files, index, inputs):
    if(inputs):
        lineArr = []
        with open(gallery_path + '/index.html', "rt", encoding='utf-8')as fin:
            data = fin.read()
            lineArr = data.split('\n')
            instance = 0
            for i,line in enumerate(lineArr):
                if line.find("---") != -1 and instance == 0:
                    instance += 1 # Skip past the yaml opening
                elif line.find("REPLACE__TITLE__") != -1:
                    lineArr[i] = line.replace("REPLACE__TITLE__", inputs['title'])
                elif line.find("REPLACE__DESCRIP__") != -1:
                    lineArr[i] = line.replace("REPLACE__DESCRIP__", inputs['description'])
                elif line.find("REPLACE__DATE__") != -1:
                    lineArr[i] = line.replace("REPLACE__DATE__", inputs['date'])
                elif line.find("---") != -1 and instance == 1:
                    pos = i
                    for j,element in enumerate(files):
                        lineArr.insert(pos,  " - image_path: " + archive_path + "/" + element)
                        lineArr.insert(pos+1,"   caption: " + abbr + " " + str(j + int(index)))
                        lineArr.insert(pos+2,"   copyright: © J.J. Phelan")
                        pos += 3
                    break
            fin.close()

        with open(gallery_path + '/index.html', 'w', encoding='utf-8') as fout:
            assembled = '\n'.join(lineArr)
            fout.write(assembled)
            fout.close()

        lineArr = []
        with open('../gallery/index.html', "rt", encoding='utf-8') as fin:
            data = fin.read()
            lineArr = data.split('\n')

            for i,line in enumerate(lineArr):
                # Insert the images' yaml parts...
                if line.find("images:") != -1:
                    pos = i + 1
                    lineArr.insert(pos, ' - image_path: /gallery/albums/' + os.path.basename(thumbnailName))
                    lineArr.insert(pos+1, '   gallery-folder: ' + gallery_path[2:] + '/')
                    lineArr.insert(pos+2, '   gallery-name: ' + inputs['thumbnailAbbrv'])
                    lineArr.insert(pos+3, '   gallery-date: '+ inputs['date'])
                    break
            fin.close()

        with open('../gallery/index.html', 'w', encoding='utf-8') as fout:
            assembled = '\n'.join(lineArr)
            fout.write(assembled)
            fout.close()
    else:
        lineArr = []
        with open(gallery_path + '/index.html', "rt", encoding='utf-8')as fin:
            data = fin.read()
            lineArr = data.split('\n')
            instance = 0
            for i,line in enumerate(lineArr):
                if line.find("---") != -1 and instance == 0:
                    instance += 1 # Skip past the yaml opening
                elif line.find("---") != -1 and instance == 1:
                    pos = i
                    for j,element in enumerate(files):
                        lineArr.insert(pos,  " - image_path: " + archive_path + "/" + element)
                        lineArr.insert(pos+1,"   caption: " + abbr + " " + str(j + int(index)))
                        lineArr.insert(pos+2,"   copyright: © J.J. Phelan")
                        pos += 3
                    break
            fin.close()

        with open(gallery_path + '/index.html', 'w', encoding='utf-8') as fout:
            assembled = '\n'.join(lineArr)
            fout.write(assembled)
            fout.close()

# Create the necessary directories
def create_new(inputs):
    archiveName = inputs['archiveName']
    galleryName = inputs['galleryName']
    os.mkdir('../gallery/archive/'+archiveName)
    os.mkdir('../gallery/'+galleryName)
    shutil.copyfile('index.html','../gallery/'+galleryName+'/index.html')

# Put the images in the right directories and call yaml_insert
def add_to_new(inputs):
    # Grab all the filenames from the selected directory
    img_files = next(os.walk(inputFolderName), (None, None, []))[2]  # [] if no file

    # Compress the input images and put them in their correct dest directories 
    for image in img_files:
        try:
            img_path = inputFolderName + '/' + image
            img = Image.open(img_path)
            image_name = image.split('.', 1)[0]
            img.save('../gallery/archive/'+ inputs['archiveName'] + '/' + image_name + '.webp', 'webp', optimize=True, quality=inputs['quality'])
            # Copy the thumbnail to albums too
            if img_path == thumbnailName:
                img.save('../gallery/albums/' + image_name + '.webp', 'webp', optimize=True, quality=inputs['quality'])
        except:
            print('Error opening ' + image + ', dropping it from processing')

    # Add the yaml additions to the correct index.html in /gallery/gallery-...
    while(1):
        gallery_name = inputs['galleryName']
        inserted = 0
        directory = '../gallery'
        for root, dirs, files in os.walk(directory):
            for folder in dirs:
                if (gallery_name == folder) and inserted == 0:
                    # Make yaml insertion for each file
                    gallery_path = '../gallery/' + folder
                    abbrev = inputs['thumbnailAbbrv']
                    index = 1
                    yaml_insert(abbrev, '/gallery/archive/' + inputs['archiveName'] , gallery_path, img_files, index, inputs)
                    inserted = 1
        if not inserted:
            print("Make a valid selection.")
        else:
            break
    return

def get_caption_and_index(indexFile):
    # Open and loop through the file to find the abbrev (caption) and last image index
    with open(indexFile, "rt")as fin:
        data = fin.read()
        lineArr = data.split('\n')
        for i,line in enumerate(lineArr):
            if line.find("caption:") != -1:
                abbrev = line.split(' ')[-2]
                index = int(line.split(' ')[-1])
        fin.close()
    return abbrev, index

def add_to_existing(inputs):
    # Grab all the filenames from the selected directory
    img_files = next(os.walk(inputFolderName2), (None, None, []))[2]  # [] if no file

    # Compress the input images and put them in their correct dest directories
    for image in img_files:
        try:
            img_path = inputFolderName2 + '/' + image
            img = Image.open(img_path)
            image_name = image.split('.', 1)[0]
            img.save(inputs['archiveName'] + '/' + image_name + '.webp', 'webp', optimize=True, quality=inputs['quality'])
        except:
            print('Error opening ' + image + ', dropping it from processing')

    # 3. Add the yaml additions to the correct index.html in /gallery/gallery-...
    while(1):
        # get the name of the last folder in the path rather than the entire path
        gallery_name = inputs['galleryName'].split('/', -1)[-1]
        archive_path = '/gallery/archive/' + inputs['archiveName'].split('/', -1)[-1]
        
        inserted = 0
        index = 0
        directory = '../gallery'
        # Set the current directory to the gallery folder
        for root, dirs, files in os.walk(directory):
            for folder in dirs:
                if (gallery_name == folder) and inserted == 0:
                    # Make yaml insertion for each file
                    gallery_path = '../gallery/' + folder
                    [abbrev, index] = get_caption_and_index(gallery_path + '/index.html')
                    index += 1
                    yaml_insert(abbrev, archive_path, gallery_path, img_files, index, [])
                    inserted = 1
        if not inserted:
            print("Make a valid selection.")
        else:
            break
    return
#***********************************FRONT END DEFINITION*********************************
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

        # Styling:
        self['width'] = 30
        self['bg'] = 'white'

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


inputFolderName     = ''
inputFolderName2     = ''
thumbnailName       = ''
existingGallery     = ''
existingArchive     = ''
def GUI():
    # Grab some imports
    from tkinter import ttk # To manage the collection of windows
    from tkinter import filedialog
    from tkinter import messagebox

    # Store some styles
    dark_BG = "#1e1e1e"
    light_grey_BG = "#404040"
    light_text = "#cccccc"
    TI_red = "#ee0d0d"
    select_green = "#5ece77"

    # Start root frame
    root = Tk()
    root.title('Travel Blog Image Automator')
    root.resizable(width=True, height=True) # I just fixed the size to what it is, unalterable

    style1 = ttk.Style()
    style1.configure("BW.TLabel", foreground=light_text, background=dark_BG)
    style1.configure("Test.TLabel", foreground=light_text, background=light_grey_BG)

    # Create tabs for each view
    tabControl = ttk.Notebook(root, style="Test.TLabel")
    tab1 = ttk.Frame(tabControl, style="BW.TLabel")
    tab2 = ttk.Frame(tabControl, style="BW.TLabel")
    tab3 = ttk.Frame(tabControl, style="BW.TLabel")


    tabControl.add(tab1, text ='Add Photos to a New Album')
    tabControl.add(tab2, text ='Add Photos to Existing Album')
    tabControl.add(tab3, text ='Tips & Help')
    tabControl.pack(expand = 1, fill ="both")
    
    def selectDirectory():
        global inputFolderName
        inputFolderName = filedialog.askdirectory(
            title='Select a folder containing input images',
            initialdir= str(os.getcwd())
        )
        print('inputFolderName is: ' + str(inputFolderName))
        Label(inputDirLabelFrame, text=inputFolderName, bg=dark_BG, fg=select_green).grid(row=0, column=1)

    def selectDirectory2():
        global inputFolderName2
        inputFolderName2 = filedialog.askdirectory(
            title='Select a folder containing input images',
            initialdir= str(os.getcwd())
        )
        Label(inputDirLabelFrame2, text=inputFolderName2, bg=dark_BG, fg=select_green).grid(row=0, column=1)
    
    def selectThumbnail():
        global thumbnailName
        thumbnailName = filedialog.askopenfilename(
            title='Select a folder containing input images',
            initialdir= inputFolderName
        )
        Label(thumbnailLabelFrame, text=thumbnailName, bg=dark_BG, fg=select_green).grid(row=0, column=1)

    def selectArchive():
        global existingArchive
        existingArchive = filedialog.askdirectory(
            title='Select an existing archive to add pictures to',
            initialdir= '../gallery/archive'
        )
        Label(archiveToAddToFrame, text=existingArchive, bg=dark_BG, fg=select_green).grid(row=0, column=1)

    def selectGallery():
        global existingGallery
        existingGallery = filedialog.askdirectory(
            title='Select an existing galleries to add pictures to',
            initialdir= '../gallery'
        )
        Label(galleryToAddToFrame, text=existingGallery, bg=dark_BG, fg=select_green).grid(row=0, column=1)


    def disable(widget):
        for child in widget.winfo_children():
            try:
                child.configure(state=DISABLED)
            except:
                continue

    def enable(widget):
        for child in widget.winfo_children():
            try:
                child.configure(state=NORMAL)
            except:
                continue

    def run1():
        confirm_dir()
        disable(main_frame)
        runBtn['text'] = 'Processing...'

        inputs = {
            'archiveName': archiveName.get(), 
            'galleryName': galleryName.get(), 
            'title': title.get(), 
            'description': description.get(), 
            'date': date.get(),
            'thumbnailAbbrv': thumbnailAbbrv.get(),
            'quality': scale.get()
        }

        create_new(inputs)
        add_to_new(inputs)
        enable(main_frame)
        runBtn['text'] = 'Run'


    def run2():
        confirm_dir()
        disable(main_frame2)
        runBtn2['text'] = 'Processing...'

        inputs2 = {
            'archiveName': existingArchive, 
            'galleryName': existingGallery, 
            'quality': scale2.get()
        }

        add_to_existing(inputs2)
        enable(main_frame2)
        runBtn2['text'] = 'Run'        


    # The structure of the tool:
    
    # View 1: Add Photos to a New Album
    main_frame = Frame(tab1, bg=dark_BG, padx=10, pady=10)
    main_frame.grid(row=0, column=0, sticky="nswe")

    ## Select Input Folder
    inputDirLabelFrame = LabelFrame(main_frame, text="Select Input Folder: ", padx=5, pady=5, bg=dark_BG, fg=light_text)
    inputDirLabelFrame.grid(row=0, column=0, sticky=NW)
    inputDirSelectBtn = Button(inputDirLabelFrame, text="Browse Folders", activebackground=light_text, bg=light_grey_BG, fg=light_text, borderwidth=0.5, command=selectDirectory)
    inputDirSelectBtn.grid(row=0, column=0, padx=3)

    thumbnailLabelFrame = LabelFrame(main_frame, text="Select Thumbnail Image: ", padx=5, pady=5, bg=dark_BG, fg=light_text)
    thumbnailLabelFrame.grid(row=1, column=0, sticky=NW)
    inputDirSelectBtn = Button(thumbnailLabelFrame, text="Browse Files", activebackground=light_text, bg=light_grey_BG, fg=light_text, borderwidth=0.5, command=selectThumbnail)
    inputDirSelectBtn.grid(row=0, column=0, padx=3)
    
    ## Separator
    sep = Canvas(main_frame, bg=light_text, height=1, bd=0, highlightthickness=0)
    sep.grid(row=2,column=0, sticky=W+E, pady=5)

    ## Input Album Creation Fields
    albumCreationParamsLabelFrame = LabelFrame(main_frame, text='Backend Album Parameters: ', padx=5, pady=5, bg=dark_BG, fg=light_text)
    albumCreationParamsLabelFrame.grid(row=3, column=0, sticky=W)
    Label(albumCreationParamsLabelFrame, text='Archive Folder Name', bg=light_grey_BG, fg=light_text).grid(row=0, column=0, sticky=E+W)
    Label(albumCreationParamsLabelFrame, text='Webpage File Name', bg=light_grey_BG, fg=light_text).grid(row=1, column=0, sticky=E+W)
    archiveName = EntryWithPlaceholder(albumCreationParamsLabelFrame, placeholder='Ex: 2022-May-Lakeland', color=light_text)
    archiveName.grid(row=0, column=1)
    galleryName = EntryWithPlaceholder(albumCreationParamsLabelFrame, placeholder='Ex: gallery-22May-Lakeland', color=light_text)
    galleryName.grid(row=1, column=1)

    ## Input Album Param Fields
    albumFrontendLabelFrame = LabelFrame(main_frame, text='Frontend Album Parameters: ', padx=5, pady=5, bg=dark_BG, fg=light_text)
    albumFrontendLabelFrame.grid(row=4, column=0, sticky=W)
    Label(albumFrontendLabelFrame, text='City or Location', bg=light_grey_BG, fg=light_text).grid(row=0, column=0, sticky=E+W)
    Label(albumFrontendLabelFrame, text='State or Country', bg=light_grey_BG, fg=light_text).grid(row=1, column=0, sticky=E+W)
    Label(albumFrontendLabelFrame, text='Date', bg=light_grey_BG, fg=light_text).grid(row=2, column=0, sticky=E+W)
    title = EntryWithPlaceholder(albumFrontendLabelFrame, placeholder='Ex: Yosemite National Park', color=light_text)
    title.grid(row=0, column=1)
    description = EntryWithPlaceholder(albumFrontendLabelFrame, placeholder='Ex: California, USA', color=light_text)
    description.grid(row=1, column=1)
    date = EntryWithPlaceholder(albumFrontendLabelFrame, placeholder='Ex: June 6-10, 2022', color=light_text)
    date.grid(row=2, column=1)
    Label(albumFrontendLabelFrame, text='Thumbnail Text', bg=light_grey_BG, fg=light_text).grid(row=3, column=0, sticky=E+W)
    thumbnailAbbrv = EntryWithPlaceholder(albumFrontendLabelFrame, placeholder='Ex: Yosemite', color=light_text)
    thumbnailAbbrv.grid(row=3, column=1)
    
    ## Compression Scale
    compressionLabelFrame = LabelFrame(main_frame, text='Select Image Quality %', padx=5, pady=5, bg=dark_BG, fg=light_text)
    compressionLabelFrame.grid(row=5, column=0, sticky=W)
    scale = Scale(compressionLabelFrame, from_=0, to=100, orient=HORIZONTAL, bg=dark_BG, fg='white')
    scale.grid(row=0, column=0)
    scale.set(80)

    # Run button
    runBtn = Button(main_frame, text='Run', activebackground=light_text, bg=select_green, fg='black', command=run1, width=10, state=NORMAL)
    runBtn.grid(row=6, column=0)

    ## Separator
    sep = Canvas(main_frame, bg=light_text, height=1, bd=0, highlightthickness=0)
    sep.grid(row=8,column=0, sticky=W+E, pady=5)

    ## Status Bar
    Label(main_frame, text="Developed by Luke Rouleau - 2022", bg=TI_red, fg="white", anchor=W).grid(row=9, column=0, sticky=W+E)

    # Tool tips
    CreateToolTip(inputDirLabelFrame, 'Select a folder containing the images you want to make into a new album.')
    CreateToolTip(thumbnailLabelFrame, 'Choose an image to be the thumbnail image on the gallery page.')
    CreateToolTip(albumCreationParamsLabelFrame, 'Follow the suggested format and name the folders that will store your images for the website.')
    CreateToolTip(albumFrontendLabelFrame, 'Type in the text you want displayed for this gallery on the webpage.')
    CreateToolTip(compressionLabelFrame, 'Reducing the quality of your images will decrease their size, making your pages load faster.\n80% Quality is recommended.')


    # View 2: Add Photos to Existing Album
    main_frame2 = Frame(tab2, bg=dark_BG, padx=10, pady=10)
    main_frame2.grid(row=0, column=0, sticky="nswe")

    ## Select Input Folder
    inputDirLabelFrame2 = LabelFrame(main_frame2, text="Select Input Folder: ", padx=5, pady=5, bg=dark_BG, fg=light_text)
    inputDirLabelFrame2.grid(row=0, column=0, sticky=NW)
    inputDirSelectBtn = Button(inputDirLabelFrame2, text="Browse Folders", activebackground=light_text, bg=light_grey_BG, fg=light_text, borderwidth=0.5, command=selectDirectory2)
    inputDirSelectBtn.grid(row=0, column=0, padx=3)

    # Choose Archive to Add to Button
    archiveToAddToFrame = LabelFrame(main_frame2, text="Select Existing Archive Folder: ", padx=5, pady=5, bg=dark_BG, fg=light_text)
    archiveToAddToFrame.grid(row=1, column=0, sticky=NW)
    gallertToAddToBtn = Button(archiveToAddToFrame, text="Browse Folders", activebackground=light_text, bg=light_grey_BG, fg=light_text, borderwidth=0.5, command=selectArchive)
    gallertToAddToBtn.grid(row=0, column=0, padx=3)
    
    # Choose Gallery to Add to Button
    galleryToAddToFrame = LabelFrame(main_frame2, text="Select Existing Gallery Folder: ", padx=5, pady=5, bg=dark_BG, fg=light_text)
    galleryToAddToFrame.grid(row=2, column=0, sticky=NW)
    gallertToAddToBtn = Button(galleryToAddToFrame, text="Browse Folders", activebackground=light_text, bg=light_grey_BG, fg=light_text, borderwidth=0.5, command=selectGallery)
    gallertToAddToBtn.grid(row=0, column=0, padx=3)

    ## Separator
    sep = Canvas(main_frame2, bg=light_text, height=1, bd=0, highlightthickness=0)
    sep.grid(row=3,column=0, sticky=W+E, pady=5)

    ## Compression Scale
    compressionLabelFrame2 = LabelFrame(main_frame2, text='Select Image Quality %', padx=5, pady=5, bg=dark_BG, fg=light_text)
    compressionLabelFrame2.grid(row=4, column=0, sticky=W)
    scale2 = Scale(compressionLabelFrame2, from_=0, to=100, orient=HORIZONTAL, bg=dark_BG, fg='white')  #, command=updateScale)
    scale2.grid(row=0, column=0)
    scale2.set(80)

    # Run Button 2
    runBtn2 = Button(main_frame2, text='Run', activebackground=light_text, bg=select_green, fg='black', command=run2, width=10, state=NORMAL)
    runBtn2.grid(row=5, column=0)

    ## Separator
    sep = Canvas(main_frame2, bg=light_text, height=1, bd=0, highlightthickness=0)
    sep.grid(row=6,column=0, sticky=W+E, pady=5)

    ## Status Bar
    Label(main_frame2, text="Developed by Luke Rouleau - 2022", bg=TI_red, fg="white", anchor=W).grid(row=7, column=0, sticky=W+E)

    # Tool tips
    CreateToolTip(inputDirLabelFrame2, 'Select a folder containing the images you want to add to an existing album.')
    CreateToolTip(archiveToAddToFrame, 'Select the relevant archive you want to add the images to.')
    CreateToolTip(galleryToAddToFrame, 'Select the relevant gallery you want to add the images to.')
    CreateToolTip(compressionLabelFrame2, 'Reducing the quality of your images will decrease their size, making your pages load faster.\n80% Quality is recommended.')

    # View 3: Tips & Help
    main_frame3 = Frame(tab3, bg=dark_BG, padx=10, pady=10)
    main_frame3.grid(row=0, column=0, sticky="nswe")

    Label(main_frame3, text='1. Hover over something to figure out what it does.\n', fg=light_text, bg=dark_BG).grid(row=0, column=0, sticky=W)
    Label(main_frame3, text='2. Use the Add Photos to a New Album tab when you want to add', fg=light_text, bg=dark_BG).grid(row=1, column=0, sticky=W)
    Label(main_frame3, text='   photos to an album that does not exist yet and you need to create it.\n', fg=light_text, bg=dark_BG).grid(row=2, column=0, sticky=W)
    Label(main_frame3, text='3. Use the Add Photos to Existing Album when you want to just', fg=light_text, bg=dark_BG).grid(row=3, column=0, sticky=W)
    Label(main_frame3, text='   add pictures to the bottom of an already existing collection.\n', fg=light_text, bg=dark_BG).grid(row=4, column=0, sticky=W)
    Label(main_frame3, text='4. Verify that there are no errors in the terminal that opens', fg=light_text, bg=dark_BG).grid(row=5, column=0, sticky=W)
    Label(main_frame3, text='   with the tool before moving on to adding more things.\n', fg=light_text, bg=dark_BG).grid(row=6, column=0, sticky=W)
    Label(main_frame3, text='5. Send Luke a text if there are errors. One source of error', fg=light_text, bg=dark_BG).grid(row=7, column=0, sticky=W)
    Label(main_frame3, text='   is if you type something in that already exists.\n', fg=light_text, bg=dark_BG).grid(row=8, column=0, sticky=W)
    Label(main_frame3, text='6. Travel on breathren!', fg=light_text, bg=dark_BG).grid(row=9, column=0, sticky=W)

    #   # Separator
    sep = Canvas(main_frame3, bg=light_text, height=1, bd=0, highlightthickness=0)
    sep.grid(row=10,column=0, sticky=W+E+S, pady=5)



    #   # Status Bar
    Label(main_frame3, text="Developed by Luke Rouleau - 2022", bg=TI_red, fg="white", anchor=W).grid(row=11, column=0, sticky=W+E)


    root.mainloop()



if __name__ == '__main__':
    GUI()
