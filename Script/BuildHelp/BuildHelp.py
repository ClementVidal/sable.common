import LibWorkspace
import LibBuildHelp

list = LibWorkspace.GetWorkspaceList()
for w in list:
    LibBuildHelp.Build( w )