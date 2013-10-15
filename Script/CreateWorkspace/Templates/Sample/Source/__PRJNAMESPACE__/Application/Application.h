#ifndef ___PRJNAMESPACE___APPLICATION_APPLICATION_
#define ___PRJNAMESPACE___APPLICATION_APPLICATION_

#include <Sable\Core\Common\DataTypes.h>
#include <Sable\Core\ManagedObject\Ref.h>
#include <Sable\Application\StandAlone.h>
#include <Sable\Core\Event\Header.h>
#include <Sable\Input\Keyboard\Event.h>
#include <Sable\Input\Common\CameraController.h>

#include <Sable\Physic\Common\Header.h>

using namespace Sable;

namespace __PRJNAMESPACE__
{

class CViewBase;

class CApplication : public CApplicationStandAlone
{

public:

	/** @name Constructor/Destructor*/
    //@{
	CApplication();
	virtual ~CApplication();
	//@}

	/** @name Operator*/
    //@{
    //@}

	/** @name Accessors*/
    //@{
    //@}

    /** @name Manipulator*/
    //@{
    Void        Run();
    Bool        Update();
    Void        Render();
    Void        Initialize();
    //@}

private:

	//Methods
    Void OnKeyboardEvent( EKeyboardEventType type, EKeyboardEventData data );

    //Attributes
    Sable::CCameraController           m_CameraController;
    Sable::CMouseInterface::Signal         m_SignalMouseEventCamCtrl;
    Sable::CKeyboardInterface::Signal      m_SignalKeyboardEventCamCtrl;

    Sable::CRef<Sable::CPhysicWorld>      m_PhysicWorld;
};

}

#endif
