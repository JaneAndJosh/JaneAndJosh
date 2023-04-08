'''
Automated Image Adder for the Jekyll site
Author: Luke Rouleau
Date:   5/10/2022 
'''
import os
import shutil
import codecs
import PIL
from PIL import Image

'''
Insert yaml lines of this format for each image:
 - image_path: /gallery/archive/2021-May-OutWest/IMG_6308.JPEG
   caption: O.W. 01
   copyright: © J.J. Phelan
'''                    
def yaml_insert(abbr, archive_path, gallery_path, files, index):
    # find the second instance of '---' in the file
    # Generate yaml there 
    lineArr = []
    with open(gallery_path + '/index.html', "rt")as fin:
        data = fin.read()
        lineArr = data.split('\n')

        instance = 0
        for i,line in enumerate(lineArr):
            if line.find("---") != -1 and instance == 0:
                instance += 1
            elif line.find("---") != -1 and instance == 1:
                # for each picture insert the yaml
                pos = i
                for j,element in enumerate(files):
                    lineArr.insert(pos,  " - image_path: " + archive_path + "/" + element)
                    lineArr.insert(pos+1,"   caption: " + abbr + " " + str(j + int(index)))
                    lineArr.insert(pos+2,"   copyright: © J.J. Phelan")
                    pos += 3
                break
        fin.close()

    with codecs.open(gallery_path + '/index.html', 'w', 'utf-8') as fout:
        assembled = '\n'.join(lineArr)
        fout.write(assembled)
        fout.close()



'''
Add to existing gallery:

1. Add images to the correct gallery folder in /img/...
2. Add the images to the correct gallery folder in /gallery/archive/... 
3. Add the yaml additions to the correct index.html for the /gallery/gallery-...
'''
def add_to_existing(img_files):
    # 1. Add images to the correct gallery folder in /img/...
    # 2. Add the images to the correct gallery folder in /gallery/archive/...
    archive_path = ''
    gallery_path = ''
    while(1):
        img_galleries_name = input("\nType the /img/galleries/... folder name.\n\tFORMAT EXAMPLE: '2021-May-Landscapes'\n\t")
        inserted = 0
        directory = '../img/galleries'
        for root, dirs, files in os.walk(directory):
            for folder in dirs:
                if (img_galleries_name == folder):
                    # Copy images over
                    archive_path = '../gallery/archive/'+folder
                    for f in img_files:
                        shutil.copy('pics_to_add/' + f, '../img/galleries/'+folder)
                        shutil.copy('pics_to_add/' + f, archive_path)
                    inserted = 1
        if not inserted:
            print("Make a valid selection.")
        else:
            break

    # 3. Add the yaml additions to the correct index.html in /gallery/gallery-...
    while(1):
        gallery_name = input("\nType the /gallery/... folder name.\n\tFORMAT EXAMPLE: 'gallery-21May-Landscapes'\n\t")
        inserted = 0
        directory = '../gallery'
        for root, dirs, files in os.walk(directory):
            for folder in dirs:
                if (gallery_name == folder):
                    # Make yaml insertion for each file
                    gallery_path = '../gallery/' + folder
                    abbrev = input("\nType the image abbreviation.\n\tFORMAT EXAMPLE: for 'Out West', O.W. \n\t")
                    index = input("\nType the starting index for the images.\n\t")
                    yaml_insert(abbrev, archive_path[2:], gallery_path, img_files, index)
                    inserted = 1
        if not inserted:
            print("Make a valid selection.")
        else:
            break
    return

def add_to_existing2(img_files, tup):
    # 1. Add images to the correct gallery folder in /img/...
    # 2. Add the images to the correct gallery folder in /gallery/archive/...
    archive_path = ''
    gallery_path = ''
    while(1):
        #img_galleries_name = input("\nType the /img/galleries/... folder name.\n\tFORMAT EXAMPLE: '2021-May-Landscapes'\n\t")
        img_galleries_name = tup[0]
        inserted = 0
        directory = '../img/galleries'
        for root, dirs, files in os.walk(directory):
            for folder in dirs:
                if (img_galleries_name == folder):
                    # Copy images over
                    archive_path = '../gallery/archive/'+folder
                    for f in img_files:
                        shutil.copy('pics_to_add/' + f, '../img/galleries/'+folder)
                        shutil.copy('pics_to_add/' + f, archive_path)
                    inserted = 1
        if not inserted:
            print("Make a valid selection.")
        else:
            break

    # 3. Add the yaml additions to the correct index.html in /gallery/gallery-...
    while(1):
        #gallery_name = input("\nType the /gallery/... folder name.\n\tFORMAT EXAMPLE: 'gallery-21May-Landscapes'\n\t")
        gallery_name = tup[1]
        inserted = 0
        directory = '../gallery'
        for root, dirs, files in os.walk(directory):
            for folder in dirs:
                if (gallery_name == folder):
                    # Make yaml insertion for each file
                    gallery_path = '../gallery/' + folder
                    abbrev = input("\nType the image abbreviation.\n\tFORMAT EXAMPLE: for 'Out West', O.W. \n\t")
                    index = input("\nType the starting index for the images.\n\t")
                    yaml_insert(abbrev, archive_path[2:], gallery_path, img_files, index)
                    inserted = 1
        if not inserted:
            print("Make a valid selection.")
        else:
            break
    return
            

def create_new():
    img_galleries_name = input("\nType the /img/galleries/... folder name.\n\tFORMAT EXAMPLE: '2021-May-Landscapes'\n\t")
    gallery_name = input("\nType the /gallery/... folder name.\n\tFORMAT EXAMPLE: 'gallery-21May-Landscapes'\n\t")
    
    # Create the necessary directories
    print('Making directory: /img/galleries/'+img_galleries_name)
    os.mkdir('../img/galleries/'+img_galleries_name)
    
    print('Making directory: /gallery/archive/'+img_galleries_name)
    os.mkdir('../gallery/archive/'+img_galleries_name)

    print('Making directory: /gallery/'+gallery_name)
    os.mkdir('../gallery/'+gallery_name)

    print('Copying an empty index.html into /gallery/'+gallery_name)
    shutil.copyfile('index.html','../gallery/'+gallery_name+'/index.html')
        
    print('\nRemember to modify the index.html file inside of /gallery/'+gallery_name+' with title and header information, and to add an album header image.')
    return (img_galleries_name, gallery_name)


def compress_images(images, quality=30):
    # 1. If there is a directory then change into it, else perform the next operations inside of the 
    # current working directory:
    #if directory:
    #    os.chdir(directory)

    # 2. Extract all of the .png and .jpeg files:
    #files = os.listdir()

    # 3. Extract all of the images:
    #images = [file for file in files if file.endswith(('jpg', 'png'))]
    # I am actually just going to pass in the images because I've already made them into a list

    # 4. Loop over every image:
    for image in images:
        print(image)

        # 5. Open every image:
        # TODO FIX THIS UGLYNESS
        img = Image.open('pics_to_add/' + image)

        # 5. Compress every image and save it with a new name:
        image_name = image.split('.', 1)[0]
        img.save('post_compression/' + image_name + '.webp', 'webp', optimize=True, quality=quality)


'''
1. Iterate through the image files in th pics_to_add directory getting all of thier filenames
'''
img_files = []
directory = 'pics_to_add'
for root, dirs, files in os.walk(directory):
    for filename in files:
        img_files.append(filename)

# Error check the input:
if (len(files) == 0):
    exit("No files in the pics_to_add directory")


# Compress the images here
print('Compressing images...')
compress_images(img_files, 80) # This seems to be the secret sauce right here
print('Compression finished...')

# Get user input:
while(1):
    res = input("Choose mode of operation:\n\t(1) Add images to existing gallery\n\t(2) Add images to new gallery\n\t(3) Exit\n")
    if res == '1':
        add_to_existing(img_files)
        exit("Success.")
    elif res == '2':
        tup = create_new()
        add_to_existing2(img_files,tup)
        exit("Success.")
    elif res == '3':
        exit("Bye.")
    else:
        print("Make a valid selection.")

