'''
Automated Image Adder for the Jekyll site; Perform Optimization & Auto-Addition, All-in-one!

Note: this could be drastically improved in numerous ways in a re-write, but at point, 
I'm just cobbling together the two scripts. Youu could add functionality to queue up any number of album jobs, for example

Author: Luke Rouleau
Date:   6/27/2022 
'''
from selenium import webdriver  # So we can webscrape
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.chrome.options import Options
from os import walk,path,remove,listdir,mkdir
from zipfile import ZipFile
from PIL import Image
from pathlib import Path
import time                     # So we can delay loading
import shutil
import codecs

'''
=================================== PARAMS ===================================
    downloads_path      : Set this equal to your downloads folder path.
    compressed_zip_name : Set this equal to the name of the zip from https://imagecompressor.com/. This could change in the future...
    compression_dir     : Set this equal to the local path for the working post-compression directory
    conversion_dir      : Set this equal to the local path for the working post-conversion directory
'''
downloads_path = 'C:/Users/lucas/Downloads'
compressed_zip_name = 'C:/Users/lucas/Downloads/imagecompressor.zip'
compression_dir = './post_compression'
conversion_dir = './post_conversion'
pre_process_dir = './pics_to_compress'
#smallest_dir = './maximally_minimized' # This is what it used to be, but I'm am causing myself pointless work.
smallest_dir = './pics_to_add'

'''
=================================== FUNCTIONS ===================================
'''
def drag_and_drop_file(drop_target, path):
    JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
    """
    # The injection script

    # Use the injection script to simulate a drag and drop
    driver = drop_target.parent
    file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(path)

def convert_to_webp(source, dest):
    """Convert image to WebP.

    Args:
        source (pathlib.Path): Path to source image

    Returns:
        pathlib.Path: path to new image
    """
    destination = Path(dest + '/' + source).with_suffix(".webp")
    image = Image.open(compression_dir + '/' + source)  # Open image
    image.save(destination, format="webp")  # Convert image to webp
    return destination

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

'''
=================================== IMG COMPRESSION ===================================
'''
def optimize():
    web = webdriver.Chrome()        # The Chrome Driver
    #web.get('https://imagecompressor.com/')

    # Empty the working directories
    for f in listdir(compression_dir):
        remove(path.join(compression_dir, f))

    for f in listdir(conversion_dir):
        remove(path.join(conversion_dir, f))


    # XPATHS for https://imagecompressor.com/ :
    drag_and_drop = '//*[@id="app"]/section[1]/div[2]/div[2]'
    download_all = '//*[@id="app"]/section[1]/div[3]/button'
    # Try with JS injection


    dir_path = path.abspath(pre_process_dir) 
    files = next(walk(pre_process_dir), (None, None, []))[2]  # [] if no file

    print('Uploading the pictures to https://imagecompressor.com/, please wait...')
    #drag_drop = web.find_element(By.XPATH, drag_and_drop)
    for group in chunker(files, 20):
        web.get('https://imagecompressor.com/')
        drag_drop = web.find_element(By.XPATH, drag_and_drop)
        for file in group:
            drag_and_drop_file(drag_drop, path.join(dir_path, file))

        print('Waiting for the compression to occur, please wait...')
        # Wait until all have finished processing so that you can download them automatically:
        download_btn = WebDriverWait(web, 500).until(
        EC.element_to_be_clickable((By.XPATH, download_all)))
        download_btn.click();

        # Wait until the zip is done downloading
        print('Waiting for the zip to download, please wait...')
        while not path.exists(compressed_zip_name):
            time.sleep(1)

        if path.isfile(compressed_zip_name):
            print('Compressed images downloaded as ' + compressed_zip_name)
            
            # extract file
            print('Extracting compressed images to ./post_compression...')
        
            # Extract all the contents of zip file in different directory
            with ZipFile(compressed_zip_name, 'r') as zipObj:
                zipObj.extractall(compression_dir)

            # delete zip
            print('Deleting the zip...')
            remove(compressed_zip_name)

        else:
            raise ValueError("%s isn't a file!" % compressed_zip_name)

        # Now, convert the images to the webp type
        print('Converting the compressed images to webp type, please wait...')
        files = next(walk(compression_dir), (None, None, []))[2]  # [] if no file
        for file in files:
            convert_to_webp(file, conversion_dir)

        # Determine the Maximally Minimized Versions & Write out:
        files = next(walk(compression_dir), (None, None, []))[2]  # [] if no file
        for file in files:
            no_ext = path.splitext(file)[0]
            compressed_size = path.getsize(path.join(compression_dir,file))
            webp_compressed_size = path.getsize(path.join(conversion_dir,no_ext + '.webp'))
            if compressed_size < webp_compressed_size:
                # Copy file to the maximally_minimized
                shutil.move(compression_dir + '/' + file, smallest_dir + '/' + file)
            else:
                # Copy the webp file to the maximally_minimized
                curr_file = no_ext + '.webp'
                shutil.move(conversion_dir + '/' + curr_file, smallest_dir + '/' + curr_file)

        # Empty the working directories
        for f in listdir(compression_dir):
            remove(path.join(compression_dir, f))

        for f in listdir(conversion_dir):
            remove(path.join(conversion_dir, f))

    print('Success...')


    '''
    Total Reduction Calculation 
    '''
    pre_compressed_sum = 0
    post_compressed_sum = 0

    files = next(walk(pre_process_dir), (None, None, []))[2]  # [] if no file
    for file in files:
        pre_compressed_sum += path.getsize(path.join(pre_process_dir,file))

    files = next(walk(smallest_dir), (None, None, []))[2]  # [] if no file
    for file in files:
        post_compressed_sum += path.getsize(path.join(smallest_dir,file))

    reduction_val = ((pre_compressed_sum - post_compressed_sum) / pre_compressed_sum) * 100
    print('The images have been reduced by ', end='')
    print(reduction_val, end='')
    print('%')

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

def add_to_existing(img_files):
    # 1. Add images to the correct gallery folder in /img/...
    # 2. Add the images to the correct gallery folder in /gallery/archive/...
    archive_path = ''
    gallery_path = ''

    # Get input and check it for error:
    folder_match = 0
    while(not folder_match):
        img_galleries_name = input("\nType the /img/galleries/... folder name.\n\tFORMAT EXAMPLE: '2021-May-Landscapes'\n\t")        
        directory = '../img/galleries'
        for _, dirs, _ in walk(directory):
            for folder in dirs:
                if (img_galleries_name == folder):
                    folder_match = 1
        if (not folder_match):
            print("Make a valid selection.")


    gallery_match = 0
    while(not gallery_match):
        gallery_name = input("\nType the /gallery/... folder name.\n\tFORMAT EXAMPLE: 'gallery-21May-Landscapes'\n\t")
        for root, dirs, files in walk(directory):
            for gallery in dirs:
                if (gallery_name == gallery):
                    gallery_match = 1
        if (not gallery_match):
            print("Make a valid selection.")

    # optimize the images, then add them...
    optimize()


    # Copy images over
    archive_path = '../gallery/archive/'+folder
    for f in img_files:
        shutil.copy('pics_to_add/' + f, '../img/galleries/'+folder)
        shutil.copy('pics_to_add/' + f, archive_path)


    # Add the yaml additions to the correct index.html in /gallery/gallery-...
    gallery_path = '../gallery/' + gallery
    abbrev = input("\nType the image abbreviation.\n\tFORMAT EXAMPLE: for 'Out West', O.W. \n\t")
    index = input("\nType the starting index for the images.\n\t")
    yaml_insert(abbrev, archive_path[2:], gallery_path, img_files, index)

    return

def add_to_existing2(img_files, tup):
    # 1. Add images to the correct gallery folder in /img/...
    # 2. Add the images to the correct gallery folder in /gallery/archive/...
    archive_path = ''
    gallery_path = ''

    abbrev = input("\nType the image abbreviation.\n\tFORMAT EXAMPLE: for 'Out West', O.W. \n\t")
    index = input("\nType the starting index for the images.\n\t")

    optimize()


    while(1):
        #img_galleries_name = input("\nType the /img/galleries/... folder name.\n\tFORMAT EXAMPLE: '2021-May-Landscapes'\n\t")
        img_galleries_name = tup[0]
        inserted = 0
        directory = '../img/galleries'
        for root, dirs, files in walk(directory):
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
        for root, dirs, files in walk(directory):
            for folder in dirs:
                if (gallery_name == folder):
                    # Make yaml insertion for each file
                    gallery_path = '../gallery/' + folder
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
    mkdir('../img/galleries/'+img_galleries_name)
    
    print('Making directory: /gallery/archive/'+img_galleries_name)
    mkdir('../gallery/archive/'+img_galleries_name)

    print('Making directory: /gallery/'+gallery_name)
    mkdir('../gallery/'+gallery_name)

    print('Copying an empty index.html into /gallery/'+gallery_name)
    shutil.copyfile('index.html','../gallery/'+gallery_name+'/index.html')
        
    print('\nRemember to modify the index.html file inside of /gallery/'+gallery_name+' with title and header information, and to add an album header image.')
    return (img_galleries_name, gallery_name)

def auto_add():
    '''
    Iterate through the image files in the pics_to_add directory getting all of thier filenames
    '''
    img_files = []
    directory = 'pics_to_add'
    for root, dirs, files in walk(directory):
        for filename in files:
            img_files.append(filename)

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

auto_add()