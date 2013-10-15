import os
import shutil
import sys
import LibWorkspace


"""
Generate the help documentation for a given workspace.
"""
def Build( wp ) :

    prjDir = os.path.abspath( wp.GetRootDir() )
    if os.path.exists(prjDir) == False:
        print "BuildHelp - Project does not exist: " + prjDir;
        
    configPath = os.path.abspath( prjDir+u"/Help/Config.dox" )
    if os.path.exists(configPath) :
        chmPath = os.path.abspath( prjDir+u"/Help/Help.chm"  )
        os.system( "S:\Common\ThirdParty\Doxygen\doxygen.exe " + configPath )
        os.system( "S:\Common\ThirdParty\Doxygen\hhc.exe S:\Common\ThirdParty\Doxygen\Temp\html\index.hhp" )
        shutil.move( "S:\Common\ThirdParty\Doxygen\Temp\html\Help.chm" , chmPath )
        shutil.rmtree( "S:\Common\ThirdParty\Doxygen\Temp\html" )
    else :
        print "BuildHelp - Failled to open doxygen configuration file: " + configPath;
