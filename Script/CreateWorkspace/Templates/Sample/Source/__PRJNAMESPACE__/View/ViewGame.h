#ifndef ___PRJNAMESPACE___VIEW_VIEWGAME_
#define ___PRJNAMESPACE___VIEW_VIEWGAME_

#include <Sable/Core/Common/DataTypes.h>
#include <Sable/Core/ManagedObject/Ref.h>
#include <Sable/Graphics/Scene/View.h>

namespace __PRJNAMESPACE__ 
{

class CGameRenderer;
class CApplication;

class CViewGame : public Sable::CView
{

    DEFINE_MANAGED_CLASS( CViewGame );

public:

    /** @name Constructor/Destructor*/
    //@{
    CViewGame();
    CViewGame(CApplication& app);
    virtual ~CViewGame();
    //@}
    
    /** @name Operator*/
    //@{
    //@}
    
    /** @name Accessors*/
    //@{
    //@}
    
    /** @name Manipulator*/
    //@{
    Void            Initialize();
    virtual Void    Update() ;
    virtual Void    Render();
    //@}
    
private:

    // Methods

    //Attributes

};

}

#endif
