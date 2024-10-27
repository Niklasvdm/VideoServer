# FILELOADER (DIRECTORY,WINDOWS=TRUE/FALSE,SUBS=TRUE/FALSE)
#       Author Niklasvdm
#       Version 1.0.0
#       20/10/2024

from glob import glob
import logging

def importFiles(directory,windows=False,subs=True):
    logging.basicConfig(filename='FileLoader.log', level=logging.INFO)
    if subs:
        return extractMP4FilesAndVTTFiles(directory)
    else:
        (movieNames,movieDirs) = extractMP4Files(directory)
        return (movieNames,movieDirs,None)

def extractMP4Files(directory,windows=False):
    ROOT_VIDEO_DIR = directory
    mp4_files = glob(ROOT_VIDEO_DIR+'/**/*.mp4', recursive=True)
    amoMP4s = len(mp4_files)
    logging.info("Found " + str(amoMP4s) + " MP4 Files!")
    #print(mp4_files)
    
    import re
     # Some lambdas
    searchRegex = lambda regex,string : re.search(regex,string)
    extractRegex = lambda x : x.group()
    applyAndExtractRegex = lambda regex,text : extractRegex(searchRegex(regex,text))

    patternWindows = r'[^\\]+$' 
    patternsUnix = r'[^/]+$' # Unix

    if windows:
        lambdaFileList = lambda x : applyAndExtractRegex(patternWindows,x)
    else:
        lambdaFileList = lambda x : applyAndExtractRegex(patternsUnix,x)

    fileList = list(map(lambdaFileList,mp4_files))
    logging.info(fileList[0])
    #print(fileList)

    removeExtension = lambda x : x[:-4]
    convertdot = lambda x : x.replace('.',' ')
    removeBrackets = lambda x : re.sub(r'\[.*\] *','',x)
    wordpattern = r'[a-zA-Z\-\ ]*(\d\d(E|e)\d\d){0,1}(\d\s){0,1}'
    lambdaNameList = lambda x : applyAndExtractRegex(wordpattern,x)
    removeTrailingWhiteSpace = lambda x : x if x[-1] != " " else x[:-1]

    prettifyFiles = lambda x : removeTrailingWhiteSpace(lambdaNameList(removeBrackets(convertdot(removeExtension(x)))))
    
    nameList = list(map(prettifyFiles,fileList))
    logging.info(nameList[0])
    #print(nameList)

    if windows:
        lambdaSplit = lambda x : tuple(x.rsplit('\\',1))
    else: #Let's assume UNIX
        lambdaSplit =  lambda x : tuple(x.rsplit('/',1))

    fileLocations = list(map(lambdaSplit,mp4_files))

    fileLocationDict = {a:b for (a,b) in list(zip(nameList,fileLocations))}
    logging.info(fileLocationDict)
    #print(fileLocationDict)

    sortedNameList = sorted(nameList)

    return(sortedNameList,fileLocationDict)

def extractMP4FilesAndVTTFiles(directory,windows=False):
    ROOT_VIDEO_DIR = directory
    (movieNames,movieLocations) = extractMP4Files(ROOT_VIDEO_DIR,windows)
    logging.info("== EXTRACTING SUBS ==")
    #print("== EXTRACTING SUBS ==")
    logging.info(str(movieNames[0]) + str(movieLocations[movieNames[0]]))
    #print(movieNames[0],movieLocations[movieNames[0]])
    vtt_files = glob(ROOT_VIDEO_DIR+'/**/*.vtt', recursive=True)

    if windows:
        lambdaSplit = lambda x : tuple(x.rsplit('\\',1))
    else: #Let's assume UNIX
        lambdaSplit =  lambda x : tuple(x.rsplit('/',1))
    
    vttDict = {}

    for currMovie in movieNames:
        #print(currMovie)
        #logging.info("Current Movie: " + currMovie)
        currMovieDots = currMovie.replace(' ','.')
        lambdaMatch = lambda x : x if currMovieDots in x else None
        lambdaFilter = lambda x : True if x is not None else False
        #logging.info("Applying Lambda on the next line" + vtt_files[0])
        reduced = list(filter(lambdaFilter,list(map(lambdaMatch,vtt_files))))
        
        logging.info("Reduced load : " + str(len(reduced)))
        #print(reduced)
        
        if len(reduced) == 0:
            continue

        fileLocations = list(map(lambdaSplit,reduced))
        #logging.info(fileLocations[0])
        #print(fileLocations)

        vttDict[currMovie] = fileLocations

    return(movieNames,movieLocations,vttDict)    

#importFiles("/home/niklas/Videos")