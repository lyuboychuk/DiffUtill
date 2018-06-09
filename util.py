from subprocess import run, PIPE
from parse import *

root_folder = "/Users/lyubomyr.boychuk/Documents"
root_forlder_tree = "/Work Documents"
OneDrive = "/OneDrive"
one_drive_folder = root_folder + OneDrive + root_forlder_tree
local_mac_folder = root_folder + root_forlder_tree
work_folder ="/Users/lyubomyr.boychuk/Documents/SourceCode/DiffUtil"

# Files OneDrive/Work Documents/Appraisals/.DS_Store and Work Documents/Appraisals/.DS_Store differ
def RuleFilesDifferent (line):
    rule = "Files {file1} and {file2} differ"
    return parse(rule,line)

# Only in OneDrive/Work Documents/Appraisals: Copy of Sokolovska Yuliia 04-18.xlsx
def RuleOnlyThisFoderContainsFile (line):
    rule = "Only in {folder}: {file}"
    return parse(rule,line)

def IsOnOneDrive (path):
    return OneDrive in path

def DiffAnalysesDump():
    proc = run(["diff", "-rq", one_drive_folder, local_mac_folder], universal_newlines = False, stdout = PIPE)
    return map (lambda x, : x.decode('UTF-8'),  proc.stdout.splitlines())

def Analyses(): 
    NumberOfDifferent = 0
    NumberOfDifferentList = []
    
    OnMacOnly = 0
    OnMacOnlyList = []

    OnOneDriveOnly = 0
    OnOneDriveOnlyList = []

    UnderfineLines = 0
    UnderfinedLinesList = []

    for line in DiffAnalysesDump():
        el1 = RuleFilesDifferent(line) 
        el2 = RuleOnlyThisFoderContainsFile(line) 
        if el1 is not None:
            if el1["file1"].split(r"/")[-1] != ".DS_Store":
                NumberOfDifferent+=1
                NumberOfDifferentList.append(el1["file2"])
        else:
            if el2 is not None:
                if IsOnOneDrive(el2["folder"]):
                    OnOneDriveOnly+=1
                    fullFilePath = el2["folder"]+r"/"+el2["file"]
                    OnOneDriveOnlyList.append(fullFilePath)
                else:
                    fullFilePath = el2["folder"]+r"/"+el2["file"]
                    if el2["file"] != ".DS_Store" and el2["file"] != "Thumbs.db" and "~$" not in el2["file"] and el2["file"] != "desktop.ini" :
                        OnMacOnly+=1
                        OnMacOnlyList.append(fullFilePath)
            else:
                UnderfineLines+=1
                UnderfinedLinesList.append(line)

    ActionList = []
    NumberOfActions = 0
    for macFile in OnMacOnlyList:
        fileTreeTrunk = macFile.split(r"/Work Documents")[-1]
        fileWithoutExtention = ('.').join(fileTreeTrunk.split('.')[:-1])
        if fileWithoutExtention is not '':
            res = list(filter(lambda x: fileWithoutExtention in x,OnOneDriveOnlyList))
        else:
            res = []
        NumberOfActions+=1
        if res == [] :
            ActionList.append(["macOnly", macFile])
        else :
            ActionList.append(["collision",macFile]+res)

    abnormalCollision = list(filter(lambda x: len(x)!=4,ActionList))

    print ("#================================")
    print ("# Number Of Different: %d" % NumberOfDifferent)
    print ("# On Mac Only: %d" % OnMacOnly)
    print ("# On OneDrive Only: %d"% OnOneDriveOnly)
    print ("# Undefine Lines: %d" % UnderfineLines)
    print ("# Number of actions required: %d" % NumberOfActions)
    print ("# Number of abnormal collisions: %d" % len(abnormalCollision))

    return ActionList

def MacOnlyCommandMaker(action):
    if action[0] is "macOnly":
        fileTreeTrunk = action[1].split(r"/Work Documents")[-1]
        destinationDir = "\""+('/').join((root_folder + OneDrive + r"/Work Documents" +fileTreeTrunk).split('/')[:-1])+"\""
    return (["cp", "-R", "\""+action[1]+"\"", destinationDir])

def CopyCommandsMaker (actions):
    commands = []
    for action in actions:
        commands.append(MacOnlyCommandMaker(action))
    return commands


def fileChecker(baseFile, checkFile):
    baseFile = ('.').join(baseFile.split('/')[-1].split('.')[:-1])
    checkFile= ('.').join(checkFile.split('/')[-1].split('.')[:-1])
    return checkFile.replace(baseFile,'')

def fileChecker2(baseFile, checkFile1, checkFile2):
    return [fileChecker(baseFile,checkFile1), fileChecker(baseFile,checkFile2)]  

def CollisionCommandsMaker(actions):
    commands = []
    tmp =[]
    # for action in filter(lambda x: len(x)==3,actions) :
    # for action in filter(lambda x: len(x)==4,actions) :
    for action in actions :
        if len(action)==3:
            action.append('')
        if action[0]=="collision":
            action[0]= "macOnly"
            commands.append(MacOnlyCommandMaker(action))
            command = ["rm", "-f"]
            tmpEl = []
            for _file in action[2:]:
                command.append("\""+_file+"\"")
                tmpEl.append(fileChecker(action[1],_file))
            commands.append(command)
            tmp.append(tmpEl)
    return commands

for command in CollisionCommandsMaker(Analyses()):
    print (*command)

print ("exit 1")

        

