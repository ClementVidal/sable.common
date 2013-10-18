#include <Sable/Core/Common/DataTypes.h>
#include <Sable/Core/Common/Manager.h>

#include <wx/cmdline.h>
#include <wx/filename.h>
#include <wx/dir.h>

using namespace Dune;
using namespace Sable;

Int32 Process( const wxCmdLineParser& cmdLine )
{
	return 1;
}

wxCmdLineEntryDesc cmdLineDesc[] =
{
	{ wxCMD_LINE_SWITCH,  WT("h"), WT("help"), WT("Show help") },
	// Add commands params here

	{ wxCMD_LINE_NONE }
};

/**
Main function,
Normaly this function should not be altered, 
insetad use Process() to write your own code
*/
Int32 main( Int32 argc, Char** argv )
{
	CDuneCommandOutput output;
	wxMessageOutput::Set( &output );

	wxCmdLineParser cmdLine( argc, argv );
	cmdLine.SetSwitchChars( WT("-") );
	cmdLine.SetDesc( cmdLineDesc );
	if( cmdLine.Parse( false ) != 0  )
	{
		cmdLine.Usage();
		return -1;
	}

	CCoreManager coreManager;

	return Process( cmdLine );
}

