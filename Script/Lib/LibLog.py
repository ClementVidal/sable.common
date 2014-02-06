
VerbosityLevel = 0

def SetVerbosity( level ) :
    VerbosityLevel = 0

def Error( msg ) :
    print ( "ERROR: "+msg )

def Info( msg ) :
    print ( "INFO: "+msg )
    
def InfoLvl1( msg ) :
    if VerbosityLevel >= 1 :
        print ( "INFO: "+msg )
    
def InfoLvl2( msg ) :
    if VerbosityLevel >= 2 :
        print ( "INFO: "+msg )
        
def Warning( msg ) :
    print ( "WARNING: "+msg )