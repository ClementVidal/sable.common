import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
import pickle
import platform
import LibWorkspace
import LibUtils


if platform.system() != "Windows" :
    print "Angle can be builded only on a Windows System with MSVC installed."
    exit()

# Return directly if VC is not installed
if LibUtils.GetVCDir() == None :
    print "Visual studio is apparently not instaled, failed to build Angle"
    exit()
	
vcDir = os.path.normpath( LibUtils.GetVCDir()+ "/../Common7/IDE/devenv.exe"  )
svnDir = os.path.normpath( os.environ["__Svn__"] + "/svn.exe" )

if not os.path.exists( vcDir ) :
    print( vcDir + " does not exist !")
    exit()
    
if not os.path.exists( svnDir ) :
    print( svnDir + " does not exist !")
    exit()
    
#delete previous working copy
if os.path.exists( "angleproject-read-only" ) :
    LibUtils.SafeRemoveDir( "angleproject-read-only" )
    
# Checkout svn prject from google
cmdLine = svnDir + " checkout http://angleproject.googlecode.com/svn/trunk/ angleproject-read-only"
if subprocess.call( cmdLine ) == 0:
    print("SVN checkout, OK")
else :
    print("SVN checkout, failed")
    exit()
    
#build lib
cmdLine = vcDir + " /build Debug \"angleproject-read-only/src/ANGLE.sln\" /project libEGL"
subprocess.call( cmdLine ) 
print("libEGL Debug, OK")
cmdLine = vcDir + " /build Release \"angleproject-read-only/src/ANGLE.sln\" /project libEGL"
subprocess.call( cmdLine ) 
print("libEGL Release, OK")
cmdLine = vcDir + " /build Debug \"angleproject-read-only/src/ANGLE.sln\" /project libGLESv2"
subprocess.call( cmdLine ) 
print("libGLESv2 Debug, OK")
cmdLine = vcDir + " /build Release \"angleproject-read-only/src/ANGLE.sln\" /project libGLESv2"
subprocess.call( cmdLine ) 
print("libGLESv2 Release, OK")

# Copy  directory
if os.path.exists( LibUtils.GetRoorDir()+"/Common/ThirdParty/Angle/include" ) :
    LibUtils.SafeRemoveDir( LibUtils.GetRoorDir()+"/Common/ThirdParty/Angle/include" )
    
if os.path.exists( LibUtils.GetRoorDir()+"/Common/ThirdParty/Angle/Lib" ) :
    LibUtils.SafeRemoveDir( LibUtils.GetRoorDir()+"/Common/ThirdParty/Angle/lib" )
    
shutil.copytree( "angleproject-read-only/include", LibUtils.GetRoorDir()+"/Common/ThirdParty/Angle/include" )
shutil.copytree( "angleproject-read-only/lib", LibUtils.GetRoorDir()+"/Common/ThirdParty/Angle/lib" )
print("Deployment OK")
