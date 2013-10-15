import LibWorkspace
import LibGenerateCode

w = LibWorkspace.GetWorkspace( "__PRJNAME__" )
LibGenerateCode.GenerateHeader( w )
LibGenerateCode.GenerateBuildFile( w )