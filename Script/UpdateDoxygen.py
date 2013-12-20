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

installerPath = os.path.normpath( LibUtils.GetRootDir() + "/Common/ThirdParty/Installer/" )
if os.path.exists(installerPath) == False :
    os.makedirs(installerPath)


if platform.system() == "Windows" :    
    print "Windows platform detected."
    destPath = installerPath+"/doxygen-1.8.5.windows.bin.zip"
    LibUtils.DownloadHTTPFile( 'ftp://ftp.stack.nl/pub/users/dimitri/doxygen-1.8.5.windows.bin.zip', destPath)

elif platform.system() == "Linux" :   
    print "Linux platform detected." 
    # Download file
    destPath =  installerPath+"/doxygen-1.8.5.linux.bin.tar.gz"
    LibUtils.DownloadHTTPFile( 'ftp://ftp.stack.nl/pub/users/dimitri/doxygen-1.8.5.linux.bin.tar.gz', destPath)
    #install It
    cmd = "gunzip "+destPath
    os.system(cmd)

    destPath =  installerPath+"/doxygen-1.8.5.linux.bin.tar"
    cmd = "tar -xvf"+destPath+" -C "+installerPath
    os.system(cmd)

    destPath =  installerPath+"/doxygen-1.8.5/bin/doxygen"
    cmd = "mv "+destPath+" "+LibUtils.GetRootDir()+"/Common/ThirdParty/Doxygen/"
    os.system(cmd)

