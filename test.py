import io
import os
import operator
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
    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        os.path.join(dir,name))
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    response = client.web_detection(image=image)
    allEntities = response.web_detection.web_entities
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
            otherEntities = entities[0:index] + entities[index+1:]
            for related in otherEntities:
                relatedEntities[entity].add(related.description.lower())
        else:
            entityFrequency[entity] =  topEntities - index
            relatedEntities[entity] = Set([])
            otherEntities = entities[0:index] + entities[index+1:]
            for related in otherEntities:
                relatedEntities[entity].add(related.description.lower())

        index += 1


def main():
    dirname = argv[1]
    dirPath = os.path.join(os.path.dirname(__file__),dirname)
    images = []
    for filename in os.listdir(dirPath):
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
            print entity[0] + ":" + ', '.join(folder)

        images = [img for img in images if img not in sortedImages]
        if len(images) == 0 :
            break
        #frequency = entityFrequency[entity]
        # print entity[0] + "," + str(entity[1]) + " related : " + ', '.join(relatedEntities[entity[0]])
    #print blackListed
    #print folders
    #for folder in folders:
    #    print folder + ', '.join(folders[folder])
if __name__ == "__main__":
    main()