import sys
import os
import ConfigParser
import _winreg
import os, sys
import optparse


#This method return the root directory of sable install
def GetInstallDirectory() :
    path = os.path.abspath( os.path.dirname(sys.argv[0]) + u'/../../..' )
    path = os.path.normpath( path )
    return path
	
#This method return the root directory of sable install
def GetScriptDirectory() :
    path = os.path.abspath( os.path.dirname(sys.argv[0] ) )
    path = os.path.normpath( path+u"/../Lib" )
    return path
	
def SetEnvVar( name, value ) :
    if len( name ) == 0 :
        print ( u'Error, variable' + name + " does not exist in configuration file")
    elif len( value ) == 0 :
        print ( "Error, variable " + name + " does not have a right value")
    else :
        path = ur'Environment'
        reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
        key = _winreg.OpenKey(reg, path, 0, _winreg.KEY_ALL_ACCESS)

        try:
            _winreg.DeleteValue( key, name )
            _winreg.FlushKey( key )
            _winreg.CloseKey( key )
        except WindowsError:
            key = _winreg.CreateKey(reg, path )

            
        reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
        key = _winreg.OpenKey(reg, path, 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(key, name, 0, _winreg.REG_EXPAND_SZ, value)
        _winreg.FlushKey( key )
        _winreg.CloseKey( key )
            
                
def MountDrive() :
    installDir = GetInstallDirectory()
    # Mount S drive
    if os.path.exists( "s:/" ) :
        os.system( "subst S: /D" )
        
    os.system( "subst S: "+installDir )
    
def SetEnvVars() :
    # setup persistent environent variable
    SetEnvVar( "PYTHONPATH", GetScriptDirectory() )
    #Parse config system
    configPath = os.path.normpath( GetScriptDirectory()+u"/../SetupEnvironment/EnvironmentSettings.conf" )
    #Setup environment variables
    if os.path.exists( configPath ) :
        
        config = ConfigParser.RawConfigParser()
        config.read( configPath )
        
        # Sdk path
        options = config.items( "SDKPathPC" )
        for option in options:
            envVarName = "__" + str( option[0] ) + "__"
            if os.path.exists(  option[1] ) == False :
                print("Error: Invalid path: "+ option[1] )
                
            SetEnvVar( envVarName, str( option[1] ) )

        # Tools path 
        options = config.items( "ToolsPath" )
        for option in options:
            envVarName = "__" + str( option[0] ) + "__"
            SetEnvVar( envVarName, str( option[1] ) )
            
        # MSVC related 
        options = config.items( "MSVC" )
        for option in options:
        
            envVarName = "__" + str( option[0] ) + "__"
            SetEnvVar( envVarName, str( option[1] ) )
            
            #Automaticly set __msvcyear__ according to MSVC Version
            if option[0] == "msvcversion" :

                if option[1] == "10" :
                    SetEnvVar( "__msvcyear__", "2010" )                
                elif option[1] == "9" :
                    SetEnvVar( "__msvcyear__", "2008" )
                elif option[1] == "8" :
                    SetEnvVar( "__msvcyear__", "2005" )
                else :
                    print( "Error: Invalid MSVCVersion" )
                    
            
    else:
        
        print ( configPath+" not present" )
        
"""
This will process all the necessary setup operation in order to compile projects.

option: 
    -v Set only environment variables, do not mount virtual drive.

"""    
def Main( argv ) :	

    if len( argv ) == 1 :
        MountDrive()
        SetEnvVars()
    else :
        usage = "usage: %prog [options] "
        parser = optparse.OptionParser(usage=usage)
        parser.add_option(u"-v", u"--variable", help="Only set the environment variables", action="store_true",  dest="onlyVar")
        (options, args) = parser.parse_args()
        if options.onlyVar == True :
            SetEnvVars()
        else :
            MountDrive()
            SetEnvVars()
    

Main( sys.argv )
