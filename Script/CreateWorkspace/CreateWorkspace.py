import os
import shutil
import sys
import optparse
import Utils
from io import open

prjName = "DefaultProject"
prjDir = "S:/"
prjNamespace = "Sable"
dico = {}

def OnError( error ):
    print u"\nFailled to create project:\n"
    print error
    sys.exit()  
    
u"""
Replace all occurence of words by and word in text.
Use dic to specify which word souhld be replaced by which other
"""
def ReplaceInString( text ) :
    for i, j in dico.items() :
        text = text.replace(i, j)
    return text

u"""
Taken a given input file, translate it's content using a specified dico
write it down to an output path
"""
def ProcessFile( inPath, outPath ) :
    input = open(inPath)
    output = open(outPath, u'w')
    buffer = u""
    for s in input:
        buffer = buffer+ReplaceInString( s )
    output.write( buffer )

u"""
Process a whole directory, and copy it to a destination path by 
translating every files
"""
def CopyDirectory( templatePath, outputPath) :
    for f in os.listdir( templatePath ) :
        if os.path.isfile( templatePath+f ) :
            ProcessFile( templatePath+f, outputPath+ReplaceInString( f ) )
        else :
            if Utils.IsSvnDir( f ) == False:
                nextDir = outputPath+ReplaceInString( f )+"/"
                os.makedirs( nextDir )
                CopyDirectory( templatePath+f+"/", nextDir)
                

u"""
Create the new project and check that arguments are valid.
"""
def Create( templateName, outputPath, name, namespace ):
    global prjName
    global prjDir
    global dico

    prjName = name
    prjDir = os.path.normpath( outputPath+u"/"+prjName )
    prjDir = prjDir.replace(u'\\', u'/')
    prjNamespace = namespace
    print prjDir
    if os.path.exists(prjDir) :
        shutil.rmtree(prjDir)
    os.makedirs( prjDir)
    templatePath = u"./Templates/"+templateName+u"/"
    if os.path.exists(templatePath) :
        dico["__PRJNAME__"] = prjName
        dico["__PRJDIR__"] = prjDir
        dico["__PRJNAMESPACE__"] = prjNamespace
        
        CopyDirectory( templatePath, prjDir+u"/" )
    else :
        OnError("Template \""+templateName+u"\" Does not exist.\nUse -h to list available template." )
        

u"""
Start the application from a command line, parse arguments and start it
"""
def StartFromCommandLine( argv ) :
    templateList = u""
    for f in os.listdir( u"./Templates/" ) :
        if Utils.IsSvnDir( f ) == False: 
            templateList = u"\n"+templateList+u"\t- "+f
        
    usage = "Use this tool te create empty project using a given template configuration. \n\n\
Available templates values are: "+templateList
    
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(u"-t", u"--Template", help="Specify the template name" , default="Sample", action="store", type="string", dest="template")
    parser.add_option(u"-o", u"--Output", help="Specify the output directory for the generated template", default=prjDir ,action="store", type="string", dest="output")
    parser.add_option(u"-n", u"--Name", help="Specify the name for the generated template" ,action="store", default=prjName, type="string", dest="name")
    parser.add_option(u"-s", u"--Namespace", help="Specify the C++ namespace used to generate code and directory", default=prjNamespace, action="store", type="string", dest="namespace")
    (options, args) = parser.parse_args()
    Create( options.template, options.output, options.name, options.namespace )

u"""
Start the application in interactive mode, ask user to input info
"""
def StartInteractive( ) :
    template = raw_input("Template name: " )
    output = raw_input("Output path: " )
    name = raw_input("Project name: " )
    namespace = raw_input("Namespace: " )   
    Create( template, output, name, namespace)

u"""
Main entry point
"""
def Main( argv ) :
    if len( argv ) == 1 :
        StartInteractive()
    else :
        StartFromCommandLine( argv )
    print "Project succesfully created in: "+prjDir


		
		
Main( sys.argv )
