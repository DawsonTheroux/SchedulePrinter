import os
import json
import datetime


DPMM = 8
TOP_PADDING = 160   # Padding in dots
SIDE_PADDING = 30   # Padding in dots


def dateHeader(height):
    dateToday = datetime.datetime.now()
    x = 30
    dateString = f"^FO{x},{height}^ADN,80^FD{dateToday.day}/{str(dateToday.month).strip()}/{dateToday.year} ^FS\n"
    return dateString

def startOfLabel(labelWidth, labelLength):
    rString = ""
    rString += "^XA\n"                                     # Start of the doc
    rString += "^XB\n"                                     # Remove backfeeding. This gives natural padding.
    rString += "^LLy" + str(labelLength)                   # The label length to begin with.
    rString += "^PWa" + str(labelWidth)
    return rString


def addTitle(height, title):
    x = 30
    return f"^FO{x},{height}^ADN,80^FD{title}^FS\n"


def solidBar(height):
    return f"^FO0,{height}^FD^GB620,5,10^FS\n"   # Bar at the Top


def generateText(height, title, fontHeight = 50, fontWidth = 28):
    labelWidth = 80 * DPMM - 10 # minus 10 for padding
    x = 30                      # The x location of the title
    padding = 10                # The padding to add under the title text
    returnString = ""   
    currentLine = ""
    curWidth = 0                # Current line width used in wrapping logic.
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
            curWidth = 0
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
    timeHeight = 30
    titleHeight = 50
    titleWidth = 28

    if "summary" in event.keys():
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

def documentFromString(inputStr):
    labelWidth = 80 * DPMM
    height = TOP_PADDING
    labelString = ""

    # Split the string using \n
    # Using the label width and height using my wrapping functionality
    # Output the string. Maybe think about adding some font size functionality.
    

def printDocument():
    ''' print the document in output_files/output.txt using lp '''
    os.system("lp -d ZebraTextOnly output_files/output.txt")
    
def createDocument(eventsArray):
    labelWidth =  80 * DPMM
    height = TOP_PADDING
    labelString = ""

    labelString += dateHeader(height)   # Bar at the end of the ticket.
    height += (8 * 8)                  # 
    labelString += solidBar(height)     # Bar at the top of the ticket
    height += 30

    for event in eventsArray:
        eventString, height = generateEventString(height, event)
        labelString += eventString
        labelString += solidBar(height)
        height += 30


    # Add all necesary stuff to the end of the document
    labelString = startOfLabel(labelWidth, height + 30) + labelString
    labelString += "\n^XZ"
    print("labelString:      {s}".format(s=labelString))
    
    f = open("output_files/output.txt", "w")
    f.write(labelString)

    return labelString

def main():
    testEvent = {}
    testEvent["summary"] = "Test Event Title"
    testEvent["start"] = {}
    testEvent["start"]["dateTime"] = "2022-07-31T20:30:00-04:00"
    testEvent["end"] = {}
    testEvent["end"]["dateTime"] = "2022-07-31T21:30:00-04:00"
    createDocument([testEvent])


if __name__ == "__main__":
    main()

