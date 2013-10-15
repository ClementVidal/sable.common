
import urllib2
import sys
import os


def DownloadHTTPFile( fileUrl, localFilePath ) :
    if localFilePath == None :
        localFilePath = os.path.basename( fileUrl )

    # Do HTTP request
    try :
        urlfile = urllib2.urlopen( fileUrl )
    except urllib2.URLError as e:
        print "Download from: " + fileUrl + "failed.\nReason are:" + str( e.reason )
        return    
    
    totalFileSize = int (urlfile.info()['Content-Length'] )
    
    # Check if file already exist
    if os.path.exists(localFilePath) and os.path.getsize(localFilePath) == totalFileSize :
        print "File: "+localFilePath+" already exist, download skipped..."
        return
     
    localFile = open(localFilePath, 'wb')

    print "Downloading: \n\tFrom: " + fileUrl + "\n\tTo: " + localFilePath
    
    #Download file
    data_list = []
    chunk = 4096*10
    size = 0
    while 1:
        data = urlfile.read(chunk)
        if not data:
            print " OK !"
            break
        size += len( data )
        localFile.write(data)
        
        progress = float( size ) / totalFileSize * 100.0        
        sys.stdout.write("\r[%f%%]" %progress )
        
        sys.stdout.flush()
        
    localFile.close()
    
print "Please select MSVC version used (2008, 2010, 2012) :"
msvcVersion = raw_input("\tVersion: " )

installerPath = "../ThirdParty/Installer/"

if os.path.exists(installerPath) == False :
    os.makedirs(installerPath)

DownloadHTTPFile( 'http://www.jrsoftware.org/download.php/ispack.exe?site=1', installerPath+"isetup-5.5.3.exe")
DownloadHTTPFile( 'http://www.sliksvn.com/pub/Slik-Subversion-1.7.9-win32.msi', installerPath+"Slik-Subversion-1.7.9-win32.msi" )
DownloadHTTPFile( 'http://download.microsoft.com/download/A/E/7/AE743F1F-632B-4809-87A9-AA1BB3458E31/DXSDK_Jun10.exe', installerPath+"DXSDK_Jun10.exe")
DownloadHTTPFile( 'http://dl.google.com/android/ndk/android-ndk-r8e-windows-x86_64.zip', installerPath+"android-ndk-r8e-windows-x86_64.zip")
 
if msvcVersion == "2008" :
    DownloadHTTPFile( 'http://download.qt-project.org/official_releases/qt/4.8/4.8.4/qt-win-opensource-4.8.4-vs2008.exe',  installerPath+"qt-win-opensource-4.8.4-vs2008.exe")
    DownloadHTTPFile( 'http://images.autodesk.com/adsk/files/fbx20141_fbxsdk_vs2008_win.exe', installerPath+"fbx20141_fbxsdk_vs2008_win.exe")
elif msvcVersion == "2010" :
    DownloadHTTPFile( 'http://download.qt-project.org/official_releases/qt/4.8/4.8.4/qt-win-opensource-4.8.4-vs2010.exe',  installerPath+"qt-win-opensource-4.8.4-vs2010.exe")
    DownloadHTTPFile( 'http://images.autodesk.com/adsk/files/fbx20141_fbxsdk_vs2010_win.exe',  installerPath+"fbx20141_fbxsdk_vs2010_win.exe" )