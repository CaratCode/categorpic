import io
import os
import Tkinter as tk
import tkFileDialog 
from sys import argv
from sets import Set


# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

# Instantiates a client
client = vision.ImageAnnotatorClient()
imageEntities = {}
entityFrequency = {}
relatedEntities = {}
topEntities = 7
folders={}

def annotateImage(dir,name):
    #print "starting image processing"
    # The name of the image file to annotate
    file_name = os.path.join(dir,name)
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.web_detection(image=image)
    allEntities = response.web_detection.web_entities
    #print "done image processing"

    entities = allEntities#[0:topEntities]
    imageEntities[name] = list(map(lambda entity : entity.description.lower(),entities))
    index = 0
    for ent in entities:
        if index >= topEntities or ent.score < 0.5: 
            break
        entity = ent.description.lower()
        if(entity == ""): 
            continue 
        if(entityFrequency.get(entity)):
            entityFrequency[entity] += topEntities - index
            otherEntities = entities[0:index] + entities[index+1:topEntities]
            for related in otherEntities:
                relatedEntities[entity].add(related.description.lower())
        else:
            entityFrequency[entity] =  topEntities - index
            relatedEntities[entity] = Set([])
            otherEntities = entities[0:index] + entities[index+1:topEntities]
            for related in otherEntities:
                relatedEntities[entity].add(related.description.lower())

        index += 1


def categorize(dirPath):
    images = []
    for filename in os.listdir(dirPath):
        filePath = os.path.join(dirPath,filename)
        if(os.path.isfile(filePath)):
            annotateImage(dirPath,filename)
            images.append(filename)
    
    sorted_entities = sorted(entityFrequency.items(), reverse=True, key=lambda tuple : tuple[1])
    blackListed = []
    relatedstuff = []
    for entity in sorted_entities:
        #go through entities starting with highest frequency, ignore entities related to those already mentioned
        if entity[0] in blackListed:
            continue
        for related in relatedEntities[entity[0]]:
            blackListed.append(related)
            relatedstuff.append(related)

        #push all images that have this entity to this entity's folder
        folder = []
        sortedImages = []
        for image in images:
            if entity[0] in imageEntities[image]:
                folder.append(image)
                sortedImages.append(image)
        if len(folder) > 0 :
            folderPath = os.path.join(dirPath,entity[0])
            os.mkdir(folderPath)
            for imageFile in folder:
                os.rename(os.path.join(dirPath,imageFile),os.path.join(folderPath,imageFile))
            #print entity[0] + ":" + ', '.join(folder)

        images = [img for img in images if img not in sortedImages]
        if len(images) == 0 :
            break
    

class Application(tk.Frame): 
    def __init__(self, master=None):
        #member vars
        self.directoryPath = ""
        #setup window
        tk.Frame.__init__(self, master)
        self.master.geometry('700x500')
        top=self.winfo_toplevel()                
        top.rowconfigure(0, weight=1)            
        top.columnconfigure(0, weight=1)         
        self.rowconfigure(0, weight=1)           
        self.columnconfigure(0, weight=1) 

        self.grid()                    
        self.createWidgets()

    def setDirectory(self):
        self.directoryPath = tkFileDialog.askdirectory()
        self.directoryField.delete(0, 'end')
        self.directoryField.insert(0, self.directoryPath)


    def createWidgets(self):
        self.logoImg = tk.PhotoImage(file= os.path.join(os.path.dirname(__file__),"assets/logo.gif"))
        self.imageLabel = tk.Label(image=self.logoImg)
        self.imageLabel.grid()
        self.intro = tk.Label(self, text="""
        Choose a folder, categorpic will organize the pictures in it into groups by relation
        """)
        self.intro.grid()
        self.browseButton = tk.Button(self, text='Browse',
            command= self.setDirectory)         
        self.browseButton.grid()
        self.directoryField = tk.Entry(self, width=30)
        self.directoryField.grid()
        self.categorizeButton = tk.Button(self, text='Categorpic it!',
            command= self.categorizeClick)      
        self.categorizeButton.grid() 
        self.warning = tk.Label(self, text="", foreground="#ff0000")
        self.warning.grid()
        self.done = tk.Label(self, text="", foreground="#0000ff")
        self.done.grid()

    def categorizeClick(self):
        self.warning['text'] = ""
        self.done['text'] = ""
        dirPath = self.directoryField.get()
        if(dirPath and os.path.isdir(dirPath)):
            categorize(dirPath)
            self.done['text'] = "Finished!"
        else:
            self.warning['text'] = "not a valid folder"
app = Application()                    
app.master.title('Categorpic') 
app.mainloop()                        
#if __name__ == "__main__":
#    main()