import os
import sys
import string
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError

import LibUtils



# A Code Package represent a directory of source code file.
# a code package can be agregated meaining that a separated BuildFile will be created
#by default a Code Package is agregated
class CCodePackage(object) :
    Path = ""
    ExcludedDirList = []
    BuildConfig = None
    IsAgregated = True
    
    def __init__(self, buildConfig, xmlNode):
        self.ExcludeList = []
        self.Path = ""
        self.BuildConfig = buildConfig
        self.Load( xmlNode )
        
    def Load( self, xmlObj ) :
        self.Path = os.path.normpath( xmlObj.get("Path") )
        
        self.IsAgregated = True
        agregateString = xmlObj.get("IsAgregated", "True") ;
        if agregateString == "False" :
            self.IsAgregated = False
            
        # find all excluded dir
        # path MUST be normalized in order to transform / to \ and to get consistent file naming
        excludedDirList = xmlObj.findall( "ExcludedDir" )
        for excludedDir in excludedDirList :
            self.ExcludedDirList.append( os.path.abspath( excludedDir.get( "Path" ) ) )           
            
        return True
        
    def GetIsAgregated( self ) :
        return self.IsAgregated
        
    # return a list of all the target file (i.e: cpp fil that needs to be compiled)
    def GetBuildTargetList( self ) :
        buildTargetList = []
        
        # if the package is agregated then only ONE target file is produced: the build file generated by the code builder
        if self.IsAgregated :  
            buildFilePath = self.BuildConfig.GetProject().GetWorkspace().GetBuildFileDir()
            buildFileName = self.GetBuildFileName()
            buildConfigName = self.BuildConfig.GetName()
            path = os.path.abspath( buildFilePath+"/"+buildConfigName+"/"+buildFileName )
            buildTargetList.append( CBuildTarget( path, self ) )
        # otherwise every file in the package are considered as individual target
        else :
            for sourcePath in self.GetSourceFileList() :
                buildTargetList.append( CBuildTarget( sourcePath, self ) )
                
        return buildTargetList
            
    def GetExcludedDirList( self ) :
        return self.ExcludedDirList
        
    # return MyPackageBuildFile.cpp
    def GetBuildFileName( self ) :
        return self.GetName() +"BuildFile.cpp"     
        
    def GetFileListRecursive( self, dir, ext ) :
        fileList = []
        
        for subName in os.listdir( dir ) :
            subName = os.path.abspath( dir+"/"+subName )
            if os.path.isfile( subName ) == True :
                fileExt = os.path.splitext(subName)[1]
                # Si le fichier dispose d'une extension valide
                if fileExt in ext :
                    fileList.append( subName )
            #Attention a bien prendre en compte la liste des repertoires a exclure
            else :
                if not subName in self.GetExcludedDirList() :
                    fileList += self.GetFileListRecursive( subName, ext )
        
        return fileList
        
    # return a list of file whoses extension match the one given in extList
    def GetFileList( self, extList ) :
        return self.GetFileListRecursive( self.Path, extList )
        
    # return a list of every source file (.h) stored in this package
    def GetHeaderFileList( self ) :
        return self.GetFileList( [".h"] )
        
    # return a list of every source file (.cpp and .c ) stored in this package
    def GetSourceFileList( self ) :
        return self.GetFileList( [".cpp", ".c"] );
        
    def GetBuildConfig( self ) :
        return  self.BuildConfig 
        
    def GetName( self ) :
        name = os.path.normpath( self.Path ).partition( "Source" )[2]
        if name == "" :
            print("Error: invalid code package path: "+self.Path )
            exit()
        
        name = name.strip( "\\/" )
        name = name.replace( "/", "_" )
        name = name.replace( "\\", "_" )
        
        return name
        
    def GetWorkspace( self ) :
        return self.GetBuildConfig().GetWorkspace()
        
#
#
#
class CBuildTarget(object) :
    Path = ""
    Package = None
    
    def __init__(self, path, package ): 
        self.Path = path
        self.Package = package
        
    def GetPackage( self ) :
        return self.Package
        
    def GetPath( self ) :
        return self.Path
        
    def GetWorkspace( self ) :
        return self.GetPackage().GetWorkspace()
        
    def GetBuildConfig( self ) :
        return self.GetPackage().GetBuildConfig()
        
#
# Represent a given workspace.
# A workspace is a named object that contain a list of projects
#
class CWorkspace(object) :
    ProjectList = []
    BuildOptionsList = []
    Name = ""
    Path = ""
    Context = None

    def __init__(self, context):
        self.ProjectList = []
        self.Name = ""
        self.Path = ""
        self.Context = context
        self.BuildOptionsList = []
    
    def IsValid(self):
        if self.Name == "" :
            return 0
        return 1

    def GetDependentWorkspace( self ) :
        list = []
        for project in self.GetProjectList() :
            for buildConfig in project.GetBuildConfigList() :
                for childConfig in buildConfig.GetDependencyList() :
                    if childConfig.GetWorkspace() not in list :
                        list.append( childConfig.GetWorkspace() )
                        
        return list;
        
    # return s:/MyPrj/Source/
    def GetSourceFileDir( self ):
        return os.path.abspath( self.GetRootDir() + "/Source/")
        
    # return s:/MyPrj/Source/
    def GetBinDir( self ):
        return os.path.abspath( self.GetRootDir() + "/Bin/")
        
    # return s:/MyPrj/Source/MyPrj/BuildFile/
    def GetBuildFileDir( self ):   
        return  os.path.abspath( self.GetSourceFileDir() + "/" + self.Name + "/BuildFile/" )

    # return s:/MyPrj/Build/
    def GetBuildDir( self ) :
        return os.path.abspath( self.GetRootDir() + "/Build/" )
        
    # return s:/MyPrj/
    def GetRootDir( self ) :
        return os.path.abspath( os.path.dirname( self.Path ) )
        
    def Load( self ):   
        try :
            # parse project definition
            xmlTree = ElementTree()
            xmlTree.parse( self.Path )
            xmlRoot = xmlTree.getroot()

            self.Name = xmlRoot.get("Name")
               
            xmlBuildOptionsList = xmlRoot.findall( "BuildOptions" )
            for xmlBuildOptions in xmlBuildOptionsList :
                buildOptions = CBuildOptions( xmlBuildOptions )
                self.BuildOptionsList.append( buildOptions )
            
            xmlProjectList = xmlRoot.findall( "Project" )
            for xmlProject in xmlProjectList :
                project = CProject( self )
                project.Load( xmlProject )
                self.ProjectList.append( project )
            
            return True
                
        except Exception, err:
            print( "Error: Failed to parse xml file: "+self.Path+":\n"+str( err ) )
            exit()
        
    def GetBuildOptions( self, name ) :
        for buildOptions in self.BuildOptionsList :
            if buildOptions.GetName() == name :
                return buildOptions
        return None
        
    def GetProjectList( self ) :
        return self.ProjectList
        
    def GetProject( self, name ):
        for p in self.ProjectList :
            if p.Name == name :
                return p
        return None
        
    def GetName( self ) :
        return self.Name
    
        
#
# Represent a given dependency of a given project
#
class CDependecy(object) :
    Workspace = ""
    Project = ""
    BuildConfig = ""
    OwnerBuildConfig = None
    
    def __init__(self, ownerBuildConfig, xmlDomObj ):
        self.Workspace = ""
        self.Project = ""
        self.BuildConfig = ""
        self.OwnerBuildConfig = ownerBuildConfig
        self.Load( xmlDomObj )
        
    def GetWorkspace( self ) :
        return self.OwnerBuildConfig.GetWorkspace().Context.GetWorkspace( self.Workspace )
        
    def GetProject( self ) :
        workspace = self.OwnerBuildConfig.GetWorkspace().Context.GetWorkspace( self.Workspace )
        if workspace != None :
            return workspace.GetProject( self.Project )
        return None
            
    def GetBuildConfig( self ) :
        project = self.GetProject( )
        if project != None :
            return project.GetBuildConfig( self.BuildConfig )
                
        return None
        
    def Load( self, xmlDomObj ):
        self.Workspace = xmlDomObj.get("Workspace")
        self.Project = xmlDomObj.get("Project")    
        self.BuildConfig = xmlDomObj.get("BuildConfig")    
            
#            
# Project class representation
#
class CProject(object) :
    Name = ""
    Workspace = None
    BuildConfigList = []
    BuildType = ""
    
    def __init__( self, workspace ):
        self.Name = ""
        self.Workspace = workspace
        self.BuildConfigList = []
        self.BuildType = ""
            
    def GetBuildConfig( self, buildConfigName ) :
        for c in self.BuildConfigList :
            if c.GetName() == buildConfigName :
                return c

    # return the build type of this project.
    #This could be:
    #   Program
    #   Lib
    def GetBuildType( self ) :
        return self.BuildType
        
    def GetBuildConfigList( self ):
        return self.BuildConfigList
        
    def GetName( self ):
        return self.Name
        
    def GetWorkspace( self ):
        return self.Workspace
        
    def Load( self, xmlObj ) :
        self.Name = xmlObj.get("Name")
        self.BuildType = xmlObj.get("BuildType")

        xmlBuildConfigList = xmlObj.findall( "BuildConfig" )
        for xmlBuildConfig in xmlBuildConfigList :
            config = CBuildConfig( self, xmlBuildConfig )
            self.BuildConfigList.append( config )
            
        return True

# Represent a given build config for a given build project
class CBuildOptions(object) :
    IncludePath = []
    LibPath = []    
    Libs = []    
    CompilerFlags = []
    LinkerFlags = []
    Name = ""
    
    def __init__(self, xmlRoot):
        self.IncludePath = []
        self.LibPath = []
        self.Libs = []
        self.CompilerFlags = []
        self.DependencyList = []
        self.LinkerFlags = []
        self.Name = ""
        self.Load( xmlRoot )
            
    def LoadList( self, xmlNodeList ) :
        outputlist = []
        for xmlNode in xmlNodeList :
            # decoupe la chaine la ou il y a des espaces
            strList = xmlNode.text.split( )
            # Subtitue toute les variables d'environement
            for str in strList :
                outputlist.append( os.path.expandvars( str ) )
                
        return outputlist
        
    def GetName( self ) :
        return self.Name
        
    def GetIncludePath( self ) :
        return self.IncludePath

    def GetLibPath( self ) :
        return self.LibPath
        
    def GetLibs( self ) :
        return self.Libs

    def GetCompilerFlags( self ) :
        return self.CompilerFlags

    def GetLinkerFlags( self ) :
        return self.LinkerFlags
        
    def Load( self, xmlRoot ) :
        self.Name = xmlRoot.get("Name")
        # parse lib path
        self.LibPath = self.LoadList( xmlRoot.findall( "LibPath" ) )
                
        # parse include path
        self.IncludePath = self.LoadList( xmlRoot.findall( "IncludePath" ) )
            
        # parse libs
        self.Libs = self.LoadList( xmlRoot.findall( "Libs" ) )
            
        # parse linker flags
        self.LinkerFlags = self.LoadList( xmlRoot.findall( "LinkerFlags" ) )
            
        # parse compiler flags
        self.CompilerFlags = self.LoadList( xmlRoot.findall( "CompilerFlags" ) )
        
# Represent a given build config for a given build project
class CBuildConfig(object) :

    CodePackageList = []
    DependencyList = []
    BuildOptionsList = []
    Project = None
    Name = ""
    ImplTypes = []
    ToolChain = ""
    
    def __init__(self, project, xmlRoot):
        self.Name = ""
        self.CodePackageList = []
        self.BuildOptionsList = []
        self.ImplTypes = ""
        self.Project = project
        self.ToolChain = ""
        self.DependencyList = []
        self.Load(xmlRoot)

    def GetIncludePath( self ) :
        list = []
        for childConfig in self.GetDependencyList() :
            list += childConfig.GetIncludePath( )        
            
        for buildOptions in self.GetBuildOptionsList() :
            list += buildOptions.GetIncludePath()
        return list

    def GetLibPath( self ) :
        list = []
        for childConfig in self.GetDependencyList() :
            list += childConfig.GetLibPath( )        
            
        for buildOptions in self.GetBuildOptionsList() :
            list += list + buildOptions.GetLibPath()
        return list
        
    def GetLibs( self ) :
        list = []
        for childConfig in self.GetDependencyList() :
            list += childConfig.GetLibs( )        
            
        for buildOptions in self.GetBuildOptionsList() :
            list += list + buildOptions.GetLibs()
        return list

    def GetCompilerFlags( self ) :
        list = []
        for childConfig in self.GetDependencyList() :
            list += childConfig.GetCompilerFlags( )        
            
        for buildOptions in self.GetBuildOptionsList() :
            list += list + buildOptions.GetCompilerFlags()
        return list

    def GetLinkerFlags( self ) :
        list = []
        for childConfig in self.GetDependencyList() :
            list += childConfig.GetLinkerFlags( )      
            
        for buildOptions in self.GetBuildOptionsList() :
            list += list + buildOptions.GetLinkerFlags()
        return list
        
    def GetPreporcessorDefines( self  ) :
        # Construction des defines pour chaque package
        definesList = []
        for cp in self.GetCodePackageListRecursive() :
            define = "SETUP_PACKAGE_" + cp.GetName()
            define = define.upper()
            definesList.append( define )
        
        # define additionel pour le type de platerforme 
        define = "SETUP_PLATFORM_" + self.GetName()
        define = define.upper()
        definesList.append( define )
            
        # define additionel pour chaque type d'implementation
        for impl in self.GetImplTypes() :
            define = "SETUP_IMPLTYPE_" + impl
            define = define.upper()
            definesList.append( define )
            
        # define du nom du projet
        define = "SETUP_PROJECT_" + self.GetProject().GetName()
        define = define.upper()
        definesList.append( define )  

        return definesList  
        
    # return a list of all the  build target necessary to build a given project   
    def GetBuildTargetList( self ) :
        buildTargetList = []
        
        for package in self.GetCodePackageList():
            for buildTarget in package.GetBuildTargetList() :
                buildTargetList.append( buildTarget )
                
        return buildTargetList

    # return a list of all the sourcefile used in this project config
    def GetSourceFileList( self ) :
        sourceFileList = []
        
        for package in self.GetCodePackageList():
            for sourceFile in package.GetSourceFileList() :
                sourceFileList.append( sourceFile )
                
        return sourceFile
        
    def GetBuildDir( self ) :
        return os.path.normpath( self.GetWorkspace().GetBuildDir() + "/" + self.GetName() )
        
    def GetBinDir( self ) :
        return os.path.normpath( self.GetWorkspace().GetBinDir() + "/" + self.GetName() )
        
    def GetToolChain( self ) :
        return self.ToolChain
        
    def GetProject( self ) :
        return self.Project
        
    def GetBuildOptionsList( self ) :
        return self.BuildOptionsList
        
    def GetWorkspace( self ) :
        return self.GetProject().GetWorkspace()
        
    def GetName( self ) :
        return self.Name
        
    def GetImplTypes( self ) :
        return self.ImplTypes
        
    def GetCodePackageList( self ):
        return self.CodePackageList
        
    def GetCodePackageListRecursive( self ):
        list = []
        for childConfig in self.GetDependencyList() :
            list = list + childConfig.GetCodePackageListRecursive( )          
        list = list + self.CodePackageList
        return list

    def GetDependencyRecursive( self ):
        list = self.GetDependencyList()
        for childConfig in self.GetDependencyList() :
            list += childConfig.GetDependencyRecursive( )
        return list
        
    def GetDependencyList( self ):
        list = []
        for dep in self.DependencyList :
            list.append( dep.GetBuildConfig() )
            
        return list
                    
    def Load( self, xmlRoot ) :
        self.Name = xmlRoot.get("Name")
        self.ImplTypes = xmlRoot.get("ImplTypes").split()
        self.ToolChain = xmlRoot.get("ToolChain")
        
        xmlBuildOptionsList = xmlRoot.findall( "BuildOptions" )
        for xmlBuildOptions in xmlBuildOptionsList :
            buildOptionsName = xmlBuildOptions.get( "Name" )
            buildOptions = self.GetWorkspace().GetBuildOptions( buildOptionsName )
            if buildOptions == None :
                print("Error: The specified build options does not exist: "+buildOptionsName)
                exit()
                
            self.BuildOptionsList.append( buildOptions )
            
        xmlCodePackageList = xmlRoot.findall( "CodePackage" )
        for xmlCodePackage in xmlCodePackageList :
            codePackage = CCodePackage( self, xmlCodePackage )
            self.CodePackageList.append( codePackage )        
        
        xmlDependencyList = xmlRoot.findall( "Dependency" )
        for xmlDependency in xmlDependencyList :
            dependency = CDependecy( self, xmlDependency )
            self.DependencyList.append( dependency )  
        

# Represent a list of all the workspace available in s:
# Only used internaly
class CContext(object) :
    WorkspaceList = []
    
    def __init__(self) :
        self.RecursiveLoadWorkspace( "S:/" )
        for  wp in self.WorkspaceList :
            wp.Load()   

    def RecursiveLoadWorkspace( self, dir ) :
        path = ""

        for f in os.listdir( dir ) :
            path = os.path.abspath( os.path.join( dir, f ) )
            if os.path.isfile( path ) :
                if f == "Workspace.xml" :
                    self.WorkspaceList.append( self.CreateWorkspace( path ) )
            else :
                if LibUtils.IsSvnDir( f ) == False and path != LibUtils.GetScriptDirectory():
                    self.RecursiveLoadWorkspace( path  )
        
    def GetWorkspace( self, name ) :
        for workspace in self.WorkspaceList :
            if workspace.Name == name :
                return workspace
        return None
        
    def GetWorkspaceList( self ) :
        return self.WorkspaceList
        
    # return a CWorkspace object represeting the parsed configFilePath
    def CreateWorkspace( self, configFilePath ) :
        workspace = CWorkspace( self )
        
        workspace.Path = configFilePath

        return workspace

globalContext = CContext()

def GetWorkspace( name ) :
    return globalContext.GetWorkspace( name )
    
def GetWorkspaceList( ) :
    return globalContext.GetWorkspaceList( )
            