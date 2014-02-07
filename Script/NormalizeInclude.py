import sys
import optparse
import fnmatch
import os 

import LibWorkspace
import LibBuildCode
import LibGenerateCode
import LibUtils

def NormalizeInclude( file ):
    
    tmpBuffer = ""
    f1 = open(file, 'r')
    for line in f1:
        if line.find( "#include" ) != -1 :
            line = line.replace('\\', '/')
            
        tmpBuffer += line
        
    f1.close()
    
    f1 = open(file, 'w')
    f1.write( tmpBuffer )
    f1.close()
    
    None
    
def ParseDirectory( dir ) :
    path = ""

    for f in os.listdir( dir ) :
        path = os.path.abspath( os.path.join( dir, f ) )
        if os.path.isfile( path ) :
            if fnmatch.fnmatch(path, '*.h') or fnmatch.fnmatch(path, '*.cpp') or fnmatch.fnmatch(path, '*.hpp'):
                NormalizeInclude( path )
        else :
            ParseDirectory( path  )
            
            
ParseDirectory( LibUtils.GetRootDir() + "/Dune/" )