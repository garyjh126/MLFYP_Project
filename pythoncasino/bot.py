import logging
import sys
import time  
from watchdog.observers import Observer  
from watchdog.events import PatternMatchingEventHandler  
from watchdog.events import LoggingEventHandler


file_modified = ''
dict_files = {}
my_set = {''}
class MyHandler(PatternMatchingEventHandler):
    #patterns = ["*.txt"]
    count = -1
    
    def process(self, event):
        MyHandler.count += 1
        global file_modified
        #file_modified = ''
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        if MyHandler.count == 1:
            pass
        
        elif MyHandler.count != 0 and file_modified != "" and MyHandler.count % 2 == 0: 
            #print("File Modified: ", file_modified)  # print now only for degug
            #print(MyHandler.count)
            #file_modified = ''
            pass

    def on_modified(self, event):
       
        self.process(event)
        global file_modified, dict_files, my_set
        if MyHandler.count % 2 == 0:
            print(my_set, MyHandler.count/2)
        milli_sec = int(round(time.time() * 1000))
        name_to_dict = '{} {}'.format(milli_sec,event.src_path) 
        file_modified = event.src_path
        f=open(file_modified, "r")
        if f.mode == 'r':
         	#dict_files[name_to_dict] = f.read()
             my_set.add(file_modified)


    def on_created(self, event):
        self.process(event)



if __name__ == '__main__':
    
    path = "C:\\Users\\garyh\\Desktop\\Project\\MLFYP_Project\\pokercasino\\botfiles"
    #args = sys.argv[1:]
    observer = Observer()
    event_handler = LoggingEventHandler()

    observer.schedule(MyHandler(), path=path if path else '.')
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()