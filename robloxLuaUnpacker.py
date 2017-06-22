#!/usr/bin/python

import os, sys 

import defusedxml.ElementTree as ET

SCRIPT = "Script"
MODULE_SCRIPT = "ModuleScript"
LOCAL_SCRIPT = "LocalScript"

SCRIPT_CLASSES = [SCRIPT, MODULE_SCRIPT, LOCAL_SCRIPT]

def getRobloxXMLFiles(path):
    file_paths =[]
    for root, dirs, files in os.walk(path):
        for name in files:
            # Get the file extension from the name
            filename, file_extension = os.path.splitext(name)
            
            # If it's a Roblox XML file, then we store the path
            if (file_extension == ".rbxlx"):
                file_paths.append(os.path.join(root, name))
    
    return file_paths

def _extractScripts(node, scripts=[], path=""):
    # For all items in this node, check if it's a script
    # If it is, store it to our scripts list
    for item in node.findall("./Item"):
        item_class = item.get("class")

        # All items have properties, so we'll get those now so we can store the
        # name for later
        properties = item.find("./Properties")

        # We need the name later regardless of whether it's a script
        name = properties.find("./string[@name='Name']")

        if (item_class in SCRIPT_CLASSES):
            source = properties.find("./ProtectedString[@name='Source']")

            script = {
                "name": name.text,
                "source": source.text,
                "path": path
            }

            scripts.append(script)
        
        # Update our path to include the current item's class
        _path = os.path.join(path, name.text)
        # Iterate through the the item's children
        scripts = _extractScripts(item, scripts, _path)
    
    return scripts

def getScriptsFromRobloxFile(roblox_file):
    tree = ET.parse(roblox_file)
    root = tree.getroot()

    filename, file_extension = os.path.splitext(roblox_file)

    scripts = _extractScripts(root, path=filename)

    return scripts

def saveScript(script):
    # Create the file name from the path and the name given to it in Roblox
    path = script["path"]
    file_name = script["name"] + ".lua"
    file_path = os.path.join(path, file_name)

    if (not os.path.isdir(path)):
        os.makedirs(path)

    out_file = open(file_path, "wb")
    out_file.write(script["source"])
    out_file.close()

roblox_XML_files = getRobloxXMLFiles("./")

for file in roblox_XML_files:
    scripts = getScriptsFromRobloxFile(file)
    
    for script in scripts:
        saveScript(script)
