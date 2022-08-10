#!/bin/python
import printer
import calendarInteraction as cInteraction
from flask import Flask


# Printing documents will work by generating the file based on actions,
# then running the printer.printDocument() function
# - This may be changed in the future to instead generate files with names.

app = Flask(__name__)

# Prints the Schedule for the day the print request was made.
@app.route("/printSchedule", methods=['POST'])
def printTodaysShcedule():
    print("Received request to print schedule")
    try:
        cInteraction.createPrinterFile()
    except e:
        return f"Failed to create the printer file with exception: {str(e)}", 500

    try:
       printer.printDocument()
    except e:
       return f"Failed to print document with exception: {str(e)}", 500

    return "SUCCESS"


# Prints the string.
@app.route("/printString")
def printString():
    #TODO add a print string function.
    # - Handle data.
    #printer.createFileFromString()
    return "DOES NOT EXIST", 402
    
if __name__ == "__main__":
    app.run(port=8000)
