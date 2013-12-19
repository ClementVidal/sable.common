import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
import pickle

import LibWorkspace
import LibUtils
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
        targetname = os.path.splitext( os.path.basename( target.GetPath() ) )[0]
        compiledTargetPath = target.GetBuildConfig().GetBuildDir()+"/"+targetname+".o"
        compiledTargetPath = os.path.normpath( compiledTargetPath )
        return compiledTargetPath
                
    def GetExeName( self ) : 
        config = self.GetBuildConfig() 
        return config.GetProject().GetName()
        
    def GetExePath( self ) : 
        exePath = os.path.normpath( self.GetBuildConfig().GetBuildDir()+"/"+self.GetExeName() )
        return exePath
                    
    def LinkConfig( self ) :
    
        config = self.GetBuildConfig()

        return 

        cmdLine = ""
        for flag in config.GetLinkerFlags( ) :
            cmdLine += flag+" "        

        cmdLine += "/OUT:"+self.GetExePath()+" "
        
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

        compilerPath = "g++"
        if config.GetToolChain() == "NaCl" :
            if os.environ.has_key( "__NACLSDK__" ) :
                naclSDKPath = os.environ.get("__NACLSDK__")
            else :
                print "Compiling NaCl config, but __NACLSDK__ is not set... failed to compile"
                return False

            compilerPath = os.path.normpath( naclSDKPath + "/pepper_31/toolchain/linux_pnacl/host_x86_32/bin/clang++" )
           
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

        print cmdLine
        # run compiler

        pid = subprocess.Popen( cmdLine, shell=True )
        returnCode = pid.wait()
        
        # in case of successfull link
        if returnCode == 0:
            return True
            
        return False 
       
        
