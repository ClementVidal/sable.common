import sys
import optparse

import LibWorkspace
import LibBuildCode
import LibGenerateCode

def StartInteractive(  ) :
    workspaceName = raw_input( "Enter workspace name: " )
    
    #Select workspace
    workspace = LibWorkspace.GetWorkspace( workspaceName )
    if workspace == None :
        print( "Error: Invalid Workspace name")
        exit()
        
    # select project
    print( "Select Project: " )
    i = 1
    for project in workspace.GetProjectList() :
        print( "\t"+str(i)+" - "+project.GetName() )
        i += 1
    
    projectId = raw_input( "\tProject: " )
    project = workspace.GetProjectList()[ int(projectId)-1]
    if project == None :
        print( "Error: Invalid project")
        exit()
        
    # select build config   
    print( "Select Build Config: " )
    i = 1
    print( "\t0 - All" )
    for buildConfig in project.GetBuildConfigList() :
        print( "\t"+str(i)+" - "+buildConfig.GetName() )
        i += 1
    
    buildConfigId = raw_input( "\tBuildConfig: " )
    buildConfigList = []
    if buildConfigId == "0":
        buildConfigList = project.GetBuildConfigList()
    else :
        buildConfigList.append( project.GetBuildConfigList()[ int(buildConfigId)-1] )
    
    #select action
    print( "Select action: " )
    print( "\t1 - Clean" )
    print( "\t2 - Build" )
    print( "\t3 - Rebuild" )
    print( "\t4 - Generate Build Code" )
    actionTypeId = raw_input( "\tAction : " )
    
    # Build config
    for buildConfig in buildConfigList :
        builder = LibBuildCode.CreateBuilder( buildConfig )
        if builder == None :
            print( "Error: Failled to create builder")
            exit()
            
        if actionTypeId == "1" :
            builder.Clean()
        elif actionTypeId == "2" :
            builder.Build()
        elif actionTypeId == "3" :
            builder.ReBuild()  
        elif actionTypeId == "4" :
            LibGenerateCode.GenerateHeader( workspace )
            LibGenerateCode.GenerateBuildFile( workspace )
        else:
            print( "Error: Invalid action type")
            exit()

def StartFromCommandLine( argv ) :	
    usage = "usage: %prog [options] workspaceName projectName buildConfigName buildConfigType"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(u"-c", u"--clean", help="Clean Project", action="store_true",  dest="Clean")
    parser.add_option(u"-r", u"--rebuild", help="Rebuild Project", action="store_true",  dest="Rebuild")
    parser.add_option(u"-g", u"--generate", help="Generate Build code", action="store_true",  dest="Generate")
    parser.add_option(u"-v", u"--verbose1", help="Verbose output level 1", action="store_true",  dest="Verbose1")
    parser.add_option(u"", u"--verbose2", help="Verbose output level 2", action="store_true",  dest="Verbose2")
    (options, args) = parser.parse_args()
    
    if len( args ) != 3 :
        print("Error: invalid argument count")
        exit()
          
    workspace = LibWorkspace.GetWorkspace( args[0] )
    if workspace == None :
        print( "Error: Invalid workspace name" )
        exit()
        
    project = workspace.GetProject( args[1] )
    if project == None :
        print( "Error: Invalid project name" )
        exit()
        
    buildConfig = project.GetBuildConfig( args[2] )
    if buildConfig == None :
        print( "Error: Invalid build config name" )
        exit()
     
    builder = LibBuildCode.CreateBuilder( buildConfig )
    if builder == None :
        print( "Error: Failled to create builder")
        exit()
        
    if options.Clean == True :
        builder.Clean()
    elif options.Rebuild == True :
        builder.ReBuild()
    elif options.Generate == True:
        LibGenerateCode.GenerateHeader( workspace )
        LibGenerateCode.GenerateBuildFile( workspace )        
    else :
        builder.Build()    
    
"""
Build a project config for a given platform

option: 
    -c Clean build file for that config
    -r Rebuild file for that config
    
arguments:
    

"""     
def Main( argv ) :	

    try:
        if len( argv ) == 1 :
            StartInteractive()
        else:
            StartFromCommandLine( argv )
    except (KeyboardInterrupt):
        exit()
    
Main( sys.argv )
