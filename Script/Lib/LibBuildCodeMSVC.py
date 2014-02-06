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
        CBuilderBase.LinkConfig( self )
        
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
       
        
