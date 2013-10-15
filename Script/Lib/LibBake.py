import os
import sys
import subprocess

import Utils

BakeCmdPath = "S:/Dune/Bin/Msw/Command/Bake.exe"

"""
Bake a given dprj
"""
def BakeDprj( dprj ) :
    BakeFromPath( dprj.Path, dprj.Output )
    
"""
Bake all the dprj of a given platform
"""
def BakePlatform( platform ) :
    for p in platform.Dprjs:
        BakeDprj( p )

"""
Bake all the dprj of a given project
"""        
def BakeProject( project ) :
    for p in project.Platforms:
        BakePlatform( p )

"""
Bake all the dprj of a given workspace
"""  
def BakeWorkspace( workspace ) :
    for p in workspace.Projects:
        BakeProject( p )
        
"""
Bake a given project
projectPath: *.dprj file path
outputPath: optional outputpath, if not given, the outputpath of the projects is used
"""
def BakeFromPath( projectPath, outputPath ) :
    cmd = ""
    if outputPath == None:
        cmd = BakeCmdPath+" "+projectPath
    else:
        cmd = BakeCmdPath+" "+projectPath+" -o "+outputPath
        
    pid = subprocess.Popen( cmd, shell=True )
    returnCode = pid.wait()
    