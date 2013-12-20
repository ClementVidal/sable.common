import os
import LibUtils
import platform
import sys

installerPath = os.path.normpath( LibUtils.GetRootDir() + "/Common/ThirdParty/Installer/" )
if os.path.exists(installerPath) == False :
    os.makedirs(installerPath)


if platform.system() == "Windows" :    
    print "Windows platform detected."
    print "Please select MSVC version used (2008, 2010, 2012) :"
    msvcVersion = raw_input("\tVersion: " )

    LibUtils.DownloadHTTPFile( 'http://www.jrsoftware.org/download.php/ispack.exe?site=1', installerPath+"/isetup-5.5.3.exe")
    LibUtils.DownloadHTTPFile( 'http://www.sliksvn.com/pub/Slik-Subversion-1.7.9-win32.msi', installerPath+"/Slik-Subversion-1.7.9-win32.msi" )
    LibUtils.DownloadHTTPFile( 'http://download.microsoft.com/download/A/E/7/AE743F1F-632B-4809-87A9-AA1BB3458E31/DXSDK_Jun10.exe', installerPath+"/DXSDK_Jun10.exe")
    LibUtils.DownloadHTTPFile( 'http://dl.google.com/android/ndk/android-ndk-r8e-windows-x86_64.zip', installerPath+"/android-ndk-r8e-windows-x86_64.zip")
    LibUtils.DownloadHTTPFile( 'ftp://ftp.stack.nl/pub/users/dimitri/doxygen-1.8.5.windows.bin.zip', installerPath+"/doxygen-1.8.5.windows.bin.zip")

    if msvcVersion == "2008" :
        LibUtils.DownloadHTTPFile( 'http://download.qt-project.org/official_releases/qt/4.8/4.8.4/qt-win-opensource-4.8.4-vs2008.exe',  installerPath+"/qt-win-opensource-4.8.4-vs2008.exe")
        LibUtils.DownloadHTTPFile( 'http://images.autodesk.com/adsk/files/fbx20141_fbxsdk_vs2008_win.exe', installerPath+"/fbx20141_fbxsdk_vs2008_win.exe")
    elif msvcVersion == "2010" :
        LibUtils.DownloadHTTPFile( 'http://download.qt-project.org/official_releases/qt/4.8/4.8.4/qt-win-opensource-4.8.4-vs2010.exe',  installerPath+"/qt-win-opensource-4.8.4-vs2010.exe")
        LibUtils.DownloadHTTPFile( 'http://images.autodesk.com/adsk/files/fbx20141_fbxsdk_vs2010_win.exe',  installerPath+"/fbx20141_fbxsdk_vs2010_win.exe" )
        

elif platform.system() == "Linux" :   
    print "Linux platform detected." 
    LibUtils.DownloadHTTPFile( 'http://images.autodesk.com/adsk/files/fbx20141_fbxsdk_linux.tar.gz', installerPath+"/fbx20141_fbxsdk_linux.tar.gz" )
    LibUtils.DownloadHTTPFile( 'ftp://ftp.freedesktop.org/pub/mesa/10.0/MesaLib-10.0.0.tar.gz', installerPath+"/MesaLib-10.0.0.tar.gz" )
    LibUtils.DownloadHTTPFile( 'ftp://ftp.stack.nl/pub/users/dimitri/doxygen-1.8.5.linux.bin.tar.gz', installerPath+"/doxygen-1.8.5.linux.bin.tar.gz" )



