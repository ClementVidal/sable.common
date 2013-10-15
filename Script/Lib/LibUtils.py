import os
import time
import shutil
import _winreg

#return the path to the visual studio compiler according to the version of MSVC specified in the SetupEnvironment.conf
def GetVCDir( ) :

    msvcVersion = os.environ["__MSVCVersion__"]
    reg = _winreg.ConnectRegistry( None, _winreg.HKEY_LOCAL_MACHINE )
    
    try:
        # Try for 32 bit windows System
        key = _winreg.OpenKey( reg, "SOFTWARE\Microsoft\VisualStudio\\"+ msvcVersion +".0\Setup\VC" )
        return os.path.normpath( _winreg.QueryValueEx( key, "ProductDir" )[0] )
    except WindowsError:
        try:
            # Try for 64 bit windows system (Information are in Wow6432Node because Visual Studio run in windows on Windows mode when used in 64bits systems)
            key = _winreg.OpenKey( reg, "SOFTWARE\Wow6432Node\Microsoft\VisualStudio\\"+ msvcVersion +".0\Setup\VC" )
            return os.path.normpath( _winreg.QueryValueEx( key, "ProductDir" )[0] )
        except WindowsError:
            print("Erreur: VisualStudio"+msvcVersion+" n'est probablement pas installe correctement.")
        
    return None
        
def StringifyFile( inFilePath, outFilePath ) :
    inFile = open( inFilePath, 'r' );
    outFile = open( outFilePath, 'w' );

    for line in iter(inFile.readline, ''):
        line = line.strip('\n\r')
        outFile.write( '\"'+line+'\\n'+'\"\n' )

def IsSvnDir( dir ) :
    if dir == u".svn" :
        return True
    return False
    
#This method return the root directory of sable install
def GetScriptDirectory() :
    path = os.path.normpath( "S:/Common/Script" )
    return path
    
def SafeRemoveFile( filename ) :

    if os.path.exists( filename ) == False :
        return
        
    #hack to avoid file permission bug with os.remove (see http://bugs.python.org/issue1425127 )
    done = False
    counter = 0
    while done == False:
        try:
            os.remove(filename)
        except OSError:
            time.sleep(0.1)
            counter = counter + 1
            if counter == 20 :# after n try, give up with this file
                print "Failled to remove file: "+filename
                done = True
        else:
            done =True
            
def SafeRemoveDir( topDir ) :

    for root, dirs, files in os.walk(topDir, topdown=True):
        for name in files:
            SafeRemoveFile(os.path.join(root, name))
        for name in dirs:
            SafeRemoveDir(os.path.join(root, name))
            
    os.rmdir( topDir )        
        
def SafeMakeDir( dirName ) :
    #hack to avoid file permission bug with os.remove (see http://bugs.python.org/issue1425127 )
    done = False
    while done == False:
        try:
            os.mkdir( dirName )
        except OSError:
            time.sleep(0.1)
        else:
            done =True