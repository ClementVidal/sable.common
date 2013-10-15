import os
import shutil
import sys
import subprocess
from io import open

import LibWorkspace
import LibUtils
        
"""
Base interface for generator classes
"""
class CGenerator(object) :
   
    Workspace = None
   
    def PrintDesc( self ) :
        None
        
    def __init__( self, workspace ) :
        self.Workspace = workspace
        
    def ProcessFile( self, path ) :
        None
        
    def BeginCodePackage( self, package ) :
        None

    def EndCodePackage( self, package ) :
        None

    def BeginDirectory( self, package, path ) :
        return True

    def EndDirectory( self, path ) :
        None
        
    def Initialize( self ) :
        None
        
    def RecursiveParseDirectory( self, package, dir ) :
        path = ""
        
        if self.BeginDirectory( package, dir ) :

            for subName in os.listdir( dir ) :
                subPath = os.path.abspath( os.path.join( dir, subName ) )
                if os.path.isfile( subPath ) :
                    self.ProcessFile( subPath )

            self.EndDirectory( dir )    

            for subName in os.listdir( dir ) :
                subPath = os.path.abspath( os.path.join( dir, subName ) )
                if os.path.isfile( subPath ) == False :
                
                    if LibUtils.IsSvnDir( subName ) == False and subName != "CodeBuilder":
                        self.RecursiveParseDirectory( package, subPath  )
                    
    def Generate( self ):

        self.PrintDesc()
        self.Initialize()

        for project in self.Workspace.GetProjectList() :
            for buildConfig in project.GetBuildConfigList() : 
                for package in buildConfig.GetCodePackageList() :   
                
                    # Create code package buildfile only if it's content is agregated.
                    # otherwise, cpp file in the package will be compiled independently
                    if package.GetIsAgregated() == True :
                    
                        self.BeginCodePackage( package )
                            
                        self.RecursiveParseDirectory( package, package.Path )
                        
                        self.EndCodePackage( package )  
                    
            
"""
Generator class used to create header files
"""
class CGeneratorHeader( CGenerator ) :

    FileList = []
    
    def PrintDesc( self ) :
        print "Generating header files for: " + self.Workspace.Name
        
    def BuildPreprocessorGuards( self, path ) :
        guard = path.upper()

        guard = guard.replace( "\\", "_" )
        guard = guard.replace( ":", "_" )
        
        return  guard + "_HEADER_ "
        
    def ProcessFile( self, path ) :
        if os.path.splitext( path )[1] == ".h" :
            self.FileList.append( path )

    def BeginDirectory( self, package, path ) :
        self.FileList = []
        return True

    def EndDirectory( self, path ) :
        
        # Do not generate header file in Impl directory
        if path.find("Impl") != -1 :
            return
        
        fileName = os.path.join( path, "Header.h" )
        if os.path.exists( fileName ) == True :
            LibUtils.SafeRemoveFile( fileName )
            
        guard = self.BuildPreprocessorGuards( path )
            
        file = open( fileName, "w+t" ) 
        file.write( u"#ifndef " + guard + u"\n" )
        file.write( u"#define " + guard + u"\n" )
        file.write( u"\n" )
        
        # try to find BuildFileHeader.h 
        # if we find it, store it first in the output file
        buildFileHeader = ""
        for f in self.FileList :
            if f.find( "BuildFileHeader.h" ) != -1 :
                buildFileHeader = f
                file.write( u"#include <" + f + u">\n" )
                
        # then store all other header
        for f in self.FileList :
            if f != buildFileHeader :
                file.write( u"#include <" + f + u">\n" )
            
        file.write( u"\n" )
        file.write( u"#endif" )
        file.close()

"""
Generator class used to create QT's moc files
"""
class CGeneratorQtMocFile( CGenerator ) :

    FileList = []
        
    def PrintDesc( self ) :
        print "Generating Qt Moc files for: " + self.Workspace.Name
        
    def ProcessFile( self, path ) :
        if os.path.splitext( path )[1] == ".h" :
            
            #Try to find a Q_OBJECT string within the file
            infile = open( path ,"r")
            fileContent = infile.read()
            infile.close()
            
            if fileContent.find("Q_OBJECT") != -1 :
                self.FileList.append( path )

    def BeginDirectory( self, package, path ) :
        self.FileList = []
        return True

    def EndDirectory( self, path ) :
        if len( self.FileList ) == 0 :
            return 
        
        mocOutputDir = os.path.abspath( path + "/Moc" );
        # Clear Moc directory if necessary
        if os.path.exists( mocOutputDir ) == True : 
            shutil.rmtree( mocOutputDir )

        LibUtils.SafeMakeDir( mocOutputDir )
                
        for f in self.FileList :
            fileRawname = os.path.split( os.path.splitext( f )[0] )[1]
            mocInput = os.path.abspath( f );
            mocOutput = os.path.abspath( path+"/Moc/"+fileRawname+".cpp" );
            cmd = os.environ["__qt__"] + "/bin/moc.exe -o "+mocOutput+" "+mocInput
            pid = subprocess.Popen( cmd, shell=True )
            pid.wait()


"""
Generator class used to create build file 
"""
class CGeneratorBuildFile( CGenerator ) :

    FileList = []
    BuildFileDir = ""
    
    def PrintDesc( self ) :
        print "Generating build files for: " + self.Workspace.Name

    def ProcessFile( self, path ) :
        if os.path.splitext( path )[1] == ".cpp" or os.path.splitext( path )[1] == ".c":
            self.FileList.append( path )
            
    def Initialize( self ) :   
        shutil.rmtree( self.Workspace.GetBuildFileDir(), True )        
        LibUtils.SafeMakeDir( self.Workspace.GetBuildFileDir() )
        
    def BeginCodePackage( self, package ) :
        
        # If this package is agregated, then prepare a fresh new directory to store the build file
        if package.GetIsAgregated() == True :
            packageFileDir = os.path.dirname( package.GetBuildTargetList()[0].GetPath() )
            if os.path.exists( packageFileDir ) == False :
                os.makedirs( packageFileDir )
                
        self.FileList = []
        
    def EndCodePackage( self, package ) :
    
        # If this package is agregated, then prepare a fresh new directory to store the build file
        if package.GetIsAgregated() == True :
            buildFileName = package.GetBuildTargetList()[0].GetPath()
            
            if os.path.exists( buildFileName ) == True :
                os.remove( buildFileName )
                
            headerFileName = os.path.abspath( os.path.join( package.Path, "BuildFileHeader.h" ) )
                
            file = open( buildFileName, "w+t" ) 

            if os.path.exists( headerFileName ) == True :
                file.write( u"#include \"" + headerFileName + "\"\n" )

            file.write( u"\n" )
            for f in self.FileList :
                file.write( u"#include \"" + f + "\"\n" )
            file.write( u"\n" )
            file.close() 

    def BeginDirectory( self, package, path ) :
    
        # no need to go further for any non agregated package
        if package.GetIsAgregated() == False:
            return False
            
        for excludedDir in package.GetExcludedDirList() :
            if path == excludedDir :
                return False
                
        # if this path is a Stub impl directory, included it
        # if this path is NOT a Stub impl directory, and is an impl directory for the current platform include it
        # otherwise do note include it
        if path.find( "\\Impl\\" ) != -1 :
            if path.find( "Stub" ) != -1 :
                return True
            else :
                for impl in package.GetBuildConfig().GetImplTypes() :
                    if path.find( impl ) != -1 :
                        return True
                return False
            
        return True
        
"""
Generate header
"""
def GenerateHeader( workspace ):
    for wp in workspace.GetDependentWorkspace() :
        g = CGeneratorHeader( wp )
        g.Generate()
           
    g = CGeneratorHeader( workspace )
    g.Generate()
    
"""
Generate build code
"""
def GenerateBuildFile( workspace ):
    for wp in workspace.GetDependentWorkspace() :
        g = CGeneratorBuildFile( wp )
        g.Generate()
           
    g = CGeneratorBuildFile( workspace )
    g.Generate()  
    
"""
Generate qt moc file
"""
def GenerateQtMocFile( workspace ):
    g = CGeneratorQtMocFile( workspace )
    g.Generate()    
    
    
def FullGenerate():
 
    list = Workspace.List()
    for w in list :
        GenerateHeader( w ) 
        GenerateBuildCode( w )
    