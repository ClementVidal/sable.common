import os
import shutil
import sys
import LibWorkspace
import LibUtils
import platform

"""
Generate the help documentation for a given workspace.
"""
def Build( wp ) :


    doxygenPath = os.path.normpath( LibUtils.GetRootDir()+"/Common/ThirdParty/Doxygen/" )

    prjDir = os.path.abspath( wp.GetRootDir() )
    if os.path.exists(prjDir) == False:
        print "BuildHelp - Project does not exist: " + prjDir;
        exit()

    configPath = os.path.abspath( prjDir+u"/Help/Config.dox" )

    if os.path.exists(configPath) == False:
        print "BuildHelp - Failled to open doxygen configuration file: " + configPath;
        exit()

    if platform.system() == "Windows":

        if os.path.exists( doxygenPath+"/doxygen.exe" ) == False:
            print "BuildHelp - Doxygen not installed, run UpdateDoxygen.py"
            exit()

        chmPath = os.path.abspath( prjDir+u"/Help/Help.chm"  )
        os.system( doxygenPath+"/doxygen.exe " + configPath )
        os.system( doxygenPath+"/hhc.exe "+doxygenPath+"/Temp/html/index.hhp" )
        shutil.move( doxygenPath+"/Temp/html/Help.chm" , chmPath )
        shutil.rmtree( doxygenPath+"/Temp/html" )
            
    elif platform.system() == "Linux":

        if os.path.exists( doxygenPath+"/doxygen" ) == False:
            print "BuildHelp - Doxygen not installed, run UpdateDoxygen.py"
            exit()

        os.system( doxygenPath+"/doxygen " + configPath )

