import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
import pickle

import LibWorkspace
import LibUtils


# base class for any builder
class CBuilderBase(object) :

    BuildConfig = None
    HashDataBase = {}
        
    def __init__( self, buildConfig ):
        self.BuildConfig = buildConfig
        
        # Create Build dir
        for childBuildConfig in buildConfig.GetDependencyRecursive() :
            if not os.path.exists( childBuildConfig.GetBuildDir() ) :
                os.makedirs( childBuildConfig.GetBuildDir() )
            
        if not os.path.exists( buildConfig.GetBuildDir() ) :
            os.makedirs( buildConfig.GetBuildDir() )
        
        # Create Bin dir
        for childBuildConfig in buildConfig.GetDependencyRecursive() :
            if not os.path.exists( childBuildConfig.GetBinDir() ) :
                os.makedirs( childBuildConfig.GetBinDir() )
            
        if not os.path.exists( buildConfig.GetBinDir() ) :
            os.makedirs( buildConfig.GetBinDir() )
            
        # restore hash database from file
        filePath = self.GetHashDataBaseFilePath()
        if os.path.exists( filePath ):
            file = open( filePath,'r'  )
            self.HashDataBase = pickle.load( file )
            if self.HashDataBase == None :
                self.HashDataBase = {}
        
    def __del__( self ):
       
        # Clear hash table and refill it with fresh md5
        self.HashDataBase = {}
        for package in self.BuildConfig.GetCodePackageListRecursive() :
            for filePath in package.GetFileList( [".cpp", ".c", ".h",".hpp"] ) :
                self.HashDataBase[filePath] = self.ComputeFileHashValue( filePath )   
        
        #Dump HashDataBase to file
        filePath = self.GetHashDataBaseFilePath() 
        file = open( filePath,'w' )
        pickle.dump( self.HashDataBase, file )
        
 
    # hash the content of a file and return it's checksum
    def ComputeFileHashValue( self, filePath ):
        if os.path.exists( filePath ) == False :
            return 0
            
        file = open( filePath, "r" )
        m = hashlib.md5()
        m.update( file.read() )
        file.close()
        return m.digest()
     
    # return the path to the hash database file
    def GetHashDataBaseFilePath( self ) :
        return os.path.abspath( self.GetBuildConfig().GetBuildDir()+"/"+self.GetBuildConfig().GetProject().GetName()+".hashdb" )
        
    # return the path of the compiled file representing this target
    def GetCompiledTargetPath( self, target ) :
        return None
                
    def LinkConfig( self ) :
        return True 
        
    def GetBinFileList( self ) :
        return []
        
    # This will copy every files returned by GetBinFileList into the BinDir of the current buildConfig
    def DeployBinFiles( self ) :
        binFileList = self.GetBinFileList()
        for binFile in binFileList :
            srcFilePath = os.path.abspath( self.GetBuildConfig().GetBuildDir() +"/" + binFile)
            if os.path.exists( srcFilePath ): 
                shutil.copy( srcFilePath, self.GetBuildConfig().GetBinDir() )
        return True
        
    def CleanBinFiles( self ) :
        # Remove exe, pdb and stuff from bin dir
        binFileList = self.GetBinFileList()
        for binFile in binFileList :
            filePath = os.path.abspath( self.GetBuildConfig().GetBinDir() +"/" + binFile )
            if os.path.exists( filePath ) :
                os.remove( filePath )
        return True
        
    def CleanHashDataBaseFile( self ) :
        if os.path.exists( self.GetHashDataBaseFilePath() ) == True:
            os.remove( self.GetHashDataBaseFilePath() )
            
    # Build a given target using a given config
    def CompileTarget( self, config, target ) :
        return False 
        
    # check if a package is up to date:
    #   1- Check If each targets file exists or not    
    #   2- Check the md5 sum of each fils against the ones stored in the database
    def IsPackageUpToDate( self, package ) :
       
        for buildTarget in package.GetBuildTargetList() :
            if os.path.exists( self.GetCompiledTargetPath( buildTarget ) ) == False :
                return False
                
        for filePath in package.GetFileList( [".cpp", ".c", ".h",".hpp"] ) :
            if filePath in self.HashDataBase :
                if self.HashDataBase[filePath] != self.ComputeFileHashValue( filePath ) :
                    return False
            else:
                return False
   
        return True
        
    # return a list of all the compiled file representing this target
    def GetCompiledTargetPathList( self, config ) :
        list = []

        for package in self.BuildConfig.GetCodePackageListRecursive() :
            for buildTarget in package.GetBuildTargetList() :
                list.append( self.GetCompiledTargetPath( buildTarget ) )
         
        return list
        
    def GetBuildConfig( self ) :
        return self.BuildConfig
               
    # Build each package in the config
    def CompileConfig( self, config ) :
        compileOk = True
        for package in config.GetCodePackageList() :
            if self.IsPackageUpToDate( package ) == False :
                if self.CompilePackage( package ) == False :
                    compileOk = False
        
        return compileOk
        
    # Build each target in the package
    def CompilePackage( self, package ) :
        compileOk = True
        for target in package.GetBuildTargetList() :
            if self.CompileTarget( package.GetBuildConfig(), target ) == False :
                compileOk = False
                
        return compileOk 
        
    #recurcivly build all the dependency of a given project   
    def CompileDependency(  self, config ) :
        compileOk = True
        for childConfig in config.GetDependencyList() :
            if self.CompileConfig( childConfig ) == False :
                compileOk = False
            
            if self.CompileDependency( childConfig ) == False :
                compileOk = False
                
        return compileOk        

    def CleanConfig( self, config ) :
    
        #Remove all targets
        for target in config.GetBuildTargetList():
            compiledtargetPath = self.GetCompiledTargetPath( target )
            if os.path.exists( compiledtargetPath ) :
                os.remove( compiledtargetPath )
                
        # Remove exe, pdb and stuff from build dir
        binFileList = self.GetBinFileList()
        for binFile in binFileList :
            filePath = os.path.abspath( self.GetBuildConfig().GetBuildDir() +"/" + binFile )
            if os.path.exists( filePath ) :
                os.remove( filePath )
            
    def CleanConfigRecursive( self, config ) :
        self.CleanConfig( config )
        
        for childConfig in config.GetDependencyList() :
            self.CleanConfigRecursive( childConfig )
    
    # main entry point to build and link a specific config
    def Build( self ):
        compileOk = True
        
        print( "Info: Compiling "+self.GetBuildConfig().GetName() )
        if self.CompileDependency( self.GetBuildConfig() ) == False :
            compileOk = False
        if self.CompileConfig( self.GetBuildConfig() ) == False :
            compileOk = False     

        if compileOk == True :
            print( "Info: Linking "+self.GetBuildConfig().GetName() )
            if self.LinkConfig( ) == True :
                print( "Info: Deploying "+self.GetBuildConfig().GetName() )
                self.DeployBinFiles( )
        
    def Clean( self ) :
        print( "Info: Cleaning "+self.GetBuildConfig().GetName() )
        self.CleanConfigRecursive( self.GetBuildConfig() )
        self.CleanBinFiles( )
        self.CleanHashDataBaseFile( )
        
    def ReBuild( self ) :
        self.Clean( )
        self.Build( )
        
    
class CBuilderMSVC( CBuilderBase ) :

    def __init__( self, buildConfig ):
        CBuilderBase.__init__( self, buildConfig )

        self.SetupVCEnvironment()
        
    def GetBinFileList( self ) :
        binFileList = []
                  
        binFileList.append( self.GetExeName() )
        binFileList.append( self.GetPdbName() )
            
        return binFileList
        
    #code extracted from scons
    def SetupVCEnvironment( self ):

        interesting = set(("include", "lib", "libpath", "path"))
        result = {}

        arch = "x86"
        if self.GetBuildConfig().GetToolChain() == "Win32" :
            arch = "x86"
        elif self.GetBuildConfig().GetToolChain() == "Win64" :
            arch = "x86_amd64"
            
        popen = subprocess.Popen( os.path.normpath( LibUtils.GetVCDir() + "/vcvarsall.bat ")+arch+" & set" ,stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        
        try:
            stdout, stderr = popen.communicate()
            popen.wait()

            for line in stdout.split("\n"):
                if '=' not in line:
                    continue
                line = line.strip()
                key, value = line.split('=', 1)
                key = key.lower()
                if key in interesting:
                    if value.endswith(os.pathsep):
                        value = value[:-1]
                    result[key] = value

        finally:
            popen.stdout.close()
            popen.stderr.close()

        # update environment according to the result of vcvarsall.bat
        os.environ["path"] += os.pathsep+result['path']
        os.environ["include"] = result['include']
        os.environ["lib"] = result['lib']

    # Build a given target using a given config
    def GetCompiledTargetPath( self, target ) :
        targetname = os.path.splitext( os.path.basename( target.GetPath() ) )[0]
        compiledTargetPath = target.GetBuildConfig().GetBuildDir()+"\\"+targetname+".obj"
        compiledTargetPath = os.path.normpath( compiledTargetPath )
        return compiledTargetPath
        
    def GetPdbName( self ) : 
        config = self.GetBuildConfig() 
        return config.GetProject().GetName()+".pdb"
        
    def GetExeName( self ) : 
        config = self.GetBuildConfig() 
        return config.GetProject().GetName()+".exe"
        
    def GetExePath( self ) : 
        exePath = os.path.normpath( self.GetBuildConfig().GetBuildDir()+"/"+self.GetExeName() )
        return exePath
        
    def GetPdbPath( self ) : 
        exePath = os.path.normpath( self.GetBuildConfig().GetBuildDir()+"/"+self.GetPdbName() )
        return exePath
        
    def GetManifestPath( self ) : 
        config = self.GetBuildConfig()
        exePath = config.GetBuildDir()+"/"+config.GetProject().GetName()+".exe.manifest"
        return exePath
        
    def EmbedManifest( self ) :
        cmdLine = "mt.exe "
        cmdLine += "/nologo -manifest \""+self.GetManifestPath( )+"\" -outputresource:\""+self.GetExePath( )+"\";1"
        pid = subprocess.Popen( cmdLine )
        returnCode = pid.wait()
        
    def LinkConfig( self ) :
    
        config = self.GetBuildConfig()
            
        cmdLine = ""
        for flag in config.GetLinkerFlags( ) :
            cmdLine += flag+" "        

        cmdLine += "/OUT:"+self.GetExePath()+" "
        cmdLine += "/PDB:"+self.GetPdbPath()+" "
        
        for libPath in config.GetLibPath( ) :
            cmdLine += "\"/LIBPATH:"+libPath+"\" "
            
        for lib in config.GetLibs( ) :
            cmdLine += lib+" "
            
        for compiledTarget in self.GetCompiledTargetPathList( config ) :
            cmdLine += compiledTarget+" "
        
        # Create a temporary fil to store linker command        
        cmdFile = tempfile.NamedTemporaryFile( delete=False )
        cmdFile.write( cmdLine )
        cmdFile.close()
        
        # run linker
        cmdLine = "link.exe @"+cmdFile.name;
        pid = subprocess.Popen( cmdLine )
        returnCode = pid.wait()
                
        os.remove( cmdFile.name )
        
        # in case of successfull link
        if returnCode == 0:
            self.EmbedManifest( )
            return True
            
        return False
        
    # Build a given target using a given config
    def CompileTarget( self, config, target ) :
           
        # Build command line
        cmdLine = "cl.exe "
        cmdLine += "/Fo"+self.GetCompiledTargetPath( target )+" "
        cmdLine += "/c "+target.GetPath()+" "
        
        # Append Compiler flags
        for flag in config.GetCompilerFlags( ) :
            cmdLine += flag+" "
            
        # Append PreProcessorDefines
        for preprocessorDefine in config.GetPreporcessorDefines( ) :
            cmdLine += "/D"+preprocessorDefine+" "
            
        # append include path
        for includePath in config.GetIncludePath( ) :
            cmdLine += "\"/I"+includePath+"\" "

        # run compiler
        pid = subprocess.Popen( cmdLine )
        returnCode = pid.wait()
        
        # in case of successfull link
        if returnCode == 0:
            return True
            
        return False 
       
        
        

def CreateBuilder( buildConfig ) :
    if buildConfig.GetToolChain() == "Win32" or buildConfig.GetToolChain() == "Win64":
        return CBuilderMSVC( buildConfig )
        
    return None