import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
import pickle

import LibWorkspace
import LibUtils
import LibLog
from LibBuildCodeBase import CBuilderBase

class CBuilderGCC( CBuilderBase ) :

    def __init__( self, buildConfig ):
        CBuilderBase.__init__( self, buildConfig )
        
    def GetBinFileList( self ) :
        binFileList = []
                  
        binFileList.append( self.GetExeName() )
            
        return binFileList
        
    # Build a given target using a given config
    def GetCompiledTargetPath( self, target ) :
        compiledTargetPath =  target.GetCompiledObjectPath( "o" )
        return compiledTargetPath
                
    def GetExeName( self ) : 
        config = self.GetBuildConfig() 
        return config.GetProject().GetName()
        
    def GetExePath( self ) : 
        exePath = os.path.normpath( self.GetBuildConfig().GetBuildDir()+"/"+self.GetExeName() )
        return exePath
                    
    def LinkConfig( self ) :
        CBuilderBase.LinkConfig( self )
        
        config = self.GetBuildConfig()

        cmdLine = ""
        for flag in config.GetLinkerFlags( ) :
            cmdLine += flag+" "        

        cmdLine += "-o "+self.GetExePath()+" "
        
        for libPath in config.GetLibPath( ) :
            cmdLine += "-L"+libPath+" "
            
        for lib in config.GetLibs( ) :
            cmdLine += "-l"+lib+" "
            
        for compiledTarget in self.GetCompiledTargetPathList( config ) :
            cmdLine += compiledTarget+" "
        
        # run linker
        compilerPath = "gcc"
        if config.GetToolChain() == "NaCl" :
            compilerPath = LibUtils.GetNaclBinPath()
            if compilerPath == None :
                print "Compiling NaCl config, but __NACLSDK__ is not set... failed to compile"
                return False
            else:
                compilerPath = os.path.normpath( compilerPath + "/clang" )
                    
        cmdLine = compilerPath+" "+cmdLine
        
        pid = subprocess.Popen( cmdLine, shell=True )
        returnCode = pid.wait()
                
        # in case of successfull link
        if returnCode == 0 :
            return True
            
        return False
        
    # Build a given target using a given config
    def CompileTarget( self, config, target ) :
        CBuilderBase.CompileTarget( self, config, target )
        
        compilerPath = "gcc"
        if config.GetToolChain() == "NaCl" :
            compilerPath = LibUtils.GetNaclBinPath()
            if compilerPath == None :
                print "Compiling NaCl config, but __NACLSDK__ is not set... failed to compile"
                return False
            else:
                compilerPath = os.path.normpath( compilerPath + "/clang" )
           
        # Build command line
        cmdLine = compilerPath
        cmdLine += " -o"+self.GetCompiledTargetPath( target )+" "
        cmdLine += " -c "+target.GetPath()+" "
        
        # Append Compiler flags
        for flag in config.GetCompilerFlags( ) :
            cmdLine += flag+" "
            
        # Append PreProcessorDefines
        for preprocessorDefine in config.GetPreporcessorDefines( ) :
            cmdLine += "-D"+preprocessorDefine+" "
            
        # append include path
        for includePath in config.GetIncludePath( ) :
            cmdLine += "\"-I"+includePath+"\" "

        #LibLog.Info( cmdLine )

        # run compiler

        pid = subprocess.Popen( cmdLine, shell=True )
        returnCode = pid.wait()
        
        # in case of successfull link
        if returnCode == 0:
            return True
            
        return False 
       
        
