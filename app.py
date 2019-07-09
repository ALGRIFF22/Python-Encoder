import sys
import time  
import logging
import ffmpeg
import os
from time import sleep
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler 

#input path
inputPath = 'P:/_autoEncoder/'
#inputPath = './input/'
#output file path; make sure you change this to your directory
#example C:/your/project/folder/
#output = './output/'
output = 'P:/_autoEncoderOutput/'
#frames-per-second
fps = 25
#bitrate is in bits a second (B/s) : 1kb = 1000b: 1mb = 1000000b etc...
bitrate = 1000000
#video foramt - https://www.ffmpeg.org/general.html 
video_format = '.mp4'
#video resolution
resolutions = ['1920x1080', '640x360', '640x480']

settings = inputPath + 'settings.txt'
#CHECKS FOR EVENTS IN INPUTPATH
def on_created(event):
    print(f'event type: {event.event_type}  path: {event.src_path}')
    update_settings(settings)
    sleep(2)
    check_file_written(event.src_path)
def on_modified(event):
    print(f'event type: {event.event_type}  path: {event.src_path}')
    if event.src_path == settings:
        #write function to update settings
        update_settings(settings)
#CHECKS IF THE FILE IS WRITTEN
def check_file_written(path):
    #this checks if the file currently in there is a temp file and will 
    #reset status until it recognises the file
    check_file = True
    while check_file:
        
        file1 = os.stat(path) # initial file size
        file1_size = file1.st_size
        print('SIZE: '+ str(file1_size))
        # your script here that collects and writes data (increase file size)
        sleep(1)
        file2 = os.stat(path) # updated file size
        file2_size = file2.st_size
        comp = file2_size - file1_size
        print('COMP: ' + str(comp)) # compares sizes
        if comp == 0:
            check_file = False
            print('start encoding')
            start_encoding(path)
        else:
            sleep(10)
#STARTS ENCODING
def start_encoding(path): 
    filepath, file_extension = os.path.splitext(path)
    filename = os.path.basename(filepath)
     #this will encode the input video into the correct folders
    if file_extension == '.mov' or file_extension =='.mp4' or file_extension =='.m4a' or file_extension =='.3gp' or file_extension == '.3g2' or file_extension =='.mj2':
        
        #this creates the base folder directory
        output_path = create_directory(output + filename)
        print(output_path)
        
        r = len(resolutions)
        print(r)
        #this will loop through the amount of videos you want
        for i in range(r):
            #this creates sub-folers for each resolution of video
            base_path = create_directory(output_path + '_'+ resolutions[i])
            print(base_path)
            print(resolutions[i])

            #this encodes video and renames it based on resolution
            video_stream = ffmpeg.input(path)
            audio_stream = ffmpeg.input(path)
            res=resolutions[i].split('x')

            v1 = video_stream['v'].filter_('fps', fps = fps).filter_('scale', resolutions[i], force_original_aspect_ratio=1).filter_('pad', w=res[0] , h = res[1], x='(ow-iw)/2', y='(oh-ih)/2' )
            a1 = audio_stream['a']
            out = ffmpeg.output(v1, a1, base_path + filename + '_' + resolutions[i] + video_format, video_bitrate = bitrate).overwrite_output()
            out.run()
            
        else:
            print("Encoding Complete!")
            return
    else:
        print("You need to put a video file in the folder")
        return
#CREATES DIRECTORY AT DIRPATH
def create_directory(dirPath):
    if not os.path.exists(dirPath):
        os.mkdir(dirPath +'/')
        return dirPath +'/'
    elif os.path.exists(dirPath):
        return dirPath + '/'

def update_settings(settings):
    print('Updating Settings')
    global output
    global fps
    global bitrate
    global video_format
    global resolutions

    file = open(settings, 'r')
    
    lines = []
    for line in file:
        l = line.strip('\n')
        lines.extend([l])

    res = []
    res.clear()
    res = lines[14].split(', ')
    resolutions = res
    
    output = lines[2]
    fps = lines[5]
    bitrate = lines[8]
    video_format = lines[11]
    print('Settings Updated')
    #resolutions = [lines[17]]

if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = True
    case_sensitive = True
    event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    #creation of event handlers can also add on_deleted && on_moved
    event_handler.on_created = on_created
    event_handler.on_modified = on_modified

    #looks for event at path
    observer = Observer()
    observer.schedule(event_handler, path=inputPath, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()