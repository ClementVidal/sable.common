import os
import sys
import shutil
import subprocess
import tempfile
import hashlib
import pickle

import LibWorkspace
import LibUtils
    
import LibBuildCodeMSVC
import LibBuildCodeGCC
        

def CreateBuilder( buildConfig ) :
    if buildConfig.GetToolChain() == "Win32" or buildConfig.GetToolChain() == "Win64":
        return LibBuildCodeMSVC.CBuilderMSVC( buildConfig )
    elif buildConfig.GetToolChain() == "GCC" or  buildConfig.GetToolChain() == "NaCl" :
        return LibBuildCodeGCC.CBuilderGCC( buildConfig )

    return None
