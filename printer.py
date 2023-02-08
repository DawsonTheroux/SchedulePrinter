#!/usr/bin/python
import os
import json
import datetime
import calendarInteraction
import weatherInteraction
import PIL.ImageOps
from PIL import Image
import math
import calendar

DPMM = 8
TOP_PADDING = 160   # Padding in dots
SIDE_PADDING = 30   # Padding in dots
LABEL_WIDTH = 620   # The width of the label

def dateHeader(height):
    dateToday = datetime.datetime.now()
    x = 30
    dateString = f"^FO{x},{height}^ADN,80^FD{dateToday.day}/{str(dateToday.month).strip()}/{dateToday.year} ^FS\n"
    return dateString


def dayOfWeekHeader(height):
    dateToday = datetime.datetime.today()
    x = 30
    dayOfWeekString = f"^FO{x},{height}^ADN,60^FD{calendar.day_name[dateToday.weekday()]}^FS\n"
    return dayOfWeekString


def startOfLabel(labelLength):
    rString = ""
    rString += "^XA\n"                                     # Start of the doc
    rString += "^XB\n"                                     # Remove backfeeding. This gives natural padding.
    rString += "^LLy" + str(labelLength)                   # The label length to begin with.
    rString += "^PWa" + str(LABEL_WIDTH)
    return rString


def addTitle(height, title):
    x = 30
    return f"^FO{x},{height}^ADN,80^FD{title}^FS\n"


def solidBar(height):
    return f"^FO0,{height}^FD^GB650,5,10^FS\n"   # Bar at the Top


def generateText(height, title, fontHeight = 50, fontWidth = 28):
    labelWidth = LABEL_WIDTH - 20
    x = 30                      # The x location of the title
    padding = 10                # The padding to add under the title text
    returnString = ""   
    currentLine = ""
    curWidth = 30                # Current line width used in wrapping logic.
    height = height             # I added this because I don't know if there would be scope issues.
    
    words = title.split(" ")
    while len(words) > 0:
        word = words[0]
        if ((len(word) + 1) * fontWidth)  + curWidth <= labelWidth:
            # ADD A CHECK FOR 1 REALLY LONG WORD
            currentLine += word + " "
            curWidth += (len(word) + 1) * fontWidth
            words.pop(0)
        elif ((len(word) + 1) * fontWidth)  + curWidth > labelWidth and curWidth:
            currentLine += "*LW*"
            curWidth = 30 
            returnString += f"^FO{x},{height}^ADN,{fontHeight},{fontWidth}^FD{currentLine}^FS\n"
            currentLine = ""
            height += fontHeight + padding
        else:
            curWidth = 0
            returnString += f"^FO{x},{height}^ADN,{fontHeight},{fontWidth}^FD{currentLine}^FS\n"
            currentLine = ""
            height += fontHeight + padding
    
    if len(currentLine) > 0:
        returnString += f"^FO{x},{height}^ADN,{fontHeight},{fontWidth}^FD{currentLine}^FS\n"
        currentLine = ""
        height += fontHeight + padding

    return returnString, height


def timeString(time):
    timeArr = time.split("T")[1].split("-")[0].split(":") # Split the time on T and get the second part.
    tHour = timeArr[0]
    tMin = timeArr[1]
    timePeriod = "AM"
    
    # Set the time to PM
    if int(tHour) > 12:
        timePeriod = "PM"
        tHour = str(int(tHour) % 12)
    elif int(tHour) == 0:
        tHour = str(12)

    return f"{tHour}:{tMin} {timePeriod}"
    

def generateEventString(height, event):
    x = 30
    eventString = ""
    titleString = ""
    timeHeight = 30
    titleHeight = 50
    titleWidth = 28

    if "summary" in event.keys():
        #if "-" in event["summary"]:
            #summaryComponents = event["summary"].split('-')
            #if len(summaryComponents) > 1: 
            #    titleString1, height = generateText(height, summaryComponents[0], titleHeight, titleWidth) 
            #    titleString2, height = generateText(height, summaryComponents[1], titleHeight, titleWidth)
            #    titleString = titleString1 + titleString2
            #else:
        titleString, height = generateText(height, event["summary"], titleHeight, titleWidth)
    else:
        titleString, height = generateText(height, "**NO TITLE**", titleHeight, titleWidth)

    eventString += titleString
    
    # Check if the event has a time.
    if "dateTime" in event["start"] and "dateTime" in  event["end"]:
        # Generate start time
        sTime = timeString(event["start"]["dateTime"])
        eventString += f"^FO{x},{height}^ADN,{timeHeight}^FDStart - {sTime}^FS\n"
        height += timeHeight + 10
        # Generate end time
        eTime = timeString(event["end"]["dateTime"])
        eventString += f"^FO{x},{height}^ADN,{timeHeight}^FDEnd   - {eTime}^FS\n"
        height += timeHeight + 10
    else:
        eventString += f"^FO{x},{height}^ADN,{timeHeight}^FDAll Day Event^FS\n"
        height += timeHeight + 10
        
    return eventString, height


def convertImage(imagePath, imageHeight, imageWidth):
    image = Image.open(imagePath)
    alpha = image.convert("RGBA").split()[-1]
    bg = Image.new("RGBA", image.size, (255,255,255))
    bg.paste(image,mask=alpha)
    image = bg
    image = image.resize((int(imageWidth), int(imageHeight)), PIL.Image.NEAREST)
    image = PIL.ImageOps.invert(image.convert('L')).convert('1')
    return image.tobytes().hex()


def generateImage(height, icon):
    x = 450
    imageString = ""
    imageHeight =110 
    imageWidth = 110 
    imagePath = "/home/dawson/SchedulePrinter/weatherIcons/"

    totalBytes = math.ceil(imageWidth / 8.0) * imageHeight
    bytesperrow = math.ceil(imageWidth / 8.0)
    
    # Look for the filename containing the iconNumber.
    fileList = os.listdir(imagePath) 
    foundFile = False
    for fileName in fileList:
        # BUG: This will think that icon 1 is 11.
        numbersInFile = fileName.split(".")[0].split("-")
        if str(icon) in numbersInFile:
            imagePath += fileName
            foundFile = True
            break

    if not foundFile:
        imagePath += "notFound.png"
        
    print(f"Using file at path: {imagePath}")
    data = convertImage(imagePath, imageHeight, imageWidth)

    imageString += f"^FO{x},{height-10}^GFA,{len(data)}, {totalBytes}, {bytesperrow}, {data}\n"
    # Trying not to change height so that the text can print beside it.
    #height += imageHeight + 10

    return imageString, height


def generateWeather(height):
    # Generates the icon, high, and low.
    tempHeight = 30
    x = 30
    weatherString = ""
    dailyHigh, dailyLow, dailyDescription, icon = weatherInteraction.getDayTemperature()
    # Debug as to not waste API calls:
    #dailyHigh = 20
    #dailyLow = 10
    #dailyDescription = "Partly sunny"
    #icon = 1

    weatherString += f"^FO{x},{height}^ADN,{tempHeight}^FD{dailyDescription}^FS\n"
    height += tempHeight + 10
   
    weatherString += f"^FO{x},{height}^ADN,{tempHeight}^FDHigh: {dailyHigh}^FS\n"
    imageString, height = generateImage(height, icon)
    weatherString += imageString
    height += tempHeight + 10
    weatherString += f"^FO{x},{height}^ADN,{tempHeight}^FDLow: {dailyLow}^FS\n"
    height += tempHeight + 30
    return weatherString, height


def documentFromString(inputStr):
    # TODO: Needs to be implemented:
     # Split the string using \n
     # Using the label width and height using my wrapping functionality
     # Output the string. Maybe think about adding some font size functionality.
    height = TOP_PADDING
    labelString = ""
    

def printDocument():
    ''' print the document in output_files/output.txt using lp '''
    os.system("lp -d ZebraTextOnly output_files/output.txt")
    
def createDocument(eventsArray):
    height = TOP_PADDING
    labelString = ""

    labelString += dateHeader(height)   # Bar at the end of the ticket.
    height += (8 * 8) + 10                  # 

    labelString += dayOfWeekHeader(height)
    height += 50 + 20
    
    weatherString, height = generateWeather(height)
    labelString += weatherString

    labelString += solidBar(height)     # Bar at the top of the ticket
    height += 30

    for event in eventsArray:
        eventString, height = generateEventString(height, event)
        labelString += eventString
        labelString += solidBar(height)
        height += 30


    # Add all necesary stuff to the end of the document
    labelString = startOfLabel(height + 30) + labelString
    labelString += "\n^XZ"
    #print("labelString:      {s}".format(s=labelString))
    
    f = open("output_files/output.txt", "w")
    f.write(labelString)

    return labelString

def main():
    calendarInteraction.createPrinterFile()
    printDocument()


if __name__ == "__main__":
    main()

