import os
import shutil
import hashlib
import pickle

import LibWorkspace
import LibUtils
import LibLog

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
            hashFile = open( filePath,'r'  )
            self.HashDataBase = pickle.load( hashFile )
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
        hashFile = open( filePath,'w' )
        pickle.dump( self.HashDataBase, hashFile )
        
 
    # hash the content of a file and return it's checksum
    def ComputeFileHashValue( self, filePath ):
        if os.path.exists( filePath ) == False :
            return 0
            
        hashFile = open( filePath, "r" )
        m = hashlib.md5()
        m.update( hashFile.read() )
        hashFile.close()
        return m.digest()
     
    # return the path to the hash database file
    def GetHashDataBaseFilePath( self ) :
        return os.path.abspath( self.GetBuildConfig().GetBuildDir()+"/"+self.GetBuildConfig().GetProject().GetName()+".hashdb" )
        
    # return the path of the compiled file representing this target
    def GetCompiledTargetPath( self, target ) :
        return None
                
    def LinkConfig( self ) :
        LibLog.Info( "Linking: "+self.GetBuildConfig().GetName() )
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
                os.remove( srcFilePath )
                dstFilePath = os.path.abspath( self.GetBuildConfig().GetBinDir() +"/" + binFile)
                LibLog.Info( "Deploying: "+self.GetBuildConfig().GetName()+" to: "+dstFilePath)
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
        LibLog.Info( "Compiling: "+target.GetPath() )
        return False 
        
    # check if a package is up to date:
    #   1- Check If each targets file exists or not    
    #   2- Check the md5 sum of each fils against the ones stored in the database
    def IsPackageUpToDate( self, package ) :
       
        for buildTarget in package.GetBuildTargetList( self.BuildConfig ) :
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
        targetList = []

        for package in self.BuildConfig.GetCodePackageListRecursive() :
            for buildTarget in package.GetBuildTargetList( self.BuildConfig ) :
                targetList.append( self.GetCompiledTargetPath( buildTarget ) )
         
        return targetList
        
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
        for target in package.GetBuildTargetList( self.BuildConfig ) :
            if self.CompileTarget( self.BuildConfig, target ) == False :
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
        for target in config.GetBuildTargetList( ):
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
        if self.CompileDependency( self.GetBuildConfig() ) == False :
            compileOk = False
        if self.CompileConfig( self.GetBuildConfig() ) == False :
            compileOk = False     

        if compileOk == True :
            if self.LinkConfig( ) == True :
                self.DeployBinFiles( )
        
    def Clean( self ) :        
        LibLog.Info( "Cleaning: "+self.GetBuildConfig().GetName() )
        self.CleanConfigRecursive( self.GetBuildConfig() )
        self.CleanBinFiles( )
        self.CleanHashDataBaseFile( )
        
    def ReBuild( self ) :
        self.Clean( )
        self.Build( )
