import os
import shutil
import subprocess
import LibWorkspace

"""
Get the current revision of a given project 

The version number will be a single number if the working
copy is single revision, unmodified.  If the working
copy is unusual the version number will be more complex:

 4123:4168     mixed revision working copy
 4168M         modified working copy
 4123S         switched working copy
 4123P         partial working copy, from a sparse checkout
 4123:4168MS   mixed revision, modified, switched working copy
 
"""
def GetSvnRevision( path ) :

    if os.path.exists( path ) :
        svnPath = ""
        if os.environ.has_key( "__Svn__" ) :
            svnPath = os.environ.get("__Svn__")
        else :
            print "SvnRevision.GetSvnRevision - __Svn__ environment variable not set"
            return -1
        
        svnPath = svnPath+"/svnversion.exe"
        if os.path.exists( svnPath ) == False :
            print "SvnRevision.GetSvnRevision - svnversion.exe unreachable at: " + svnPath
            return -1
            
        cmd = os.path.normpath( "\""+svnPath+"\" -n "+ path )
        
        pid = subprocess.Popen( cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
        pid.wait()   
        revision = ( pid.stdout.read() )
        return revision
    else :
        print "GetSvnRevision - Invalid path ";
        return -1
