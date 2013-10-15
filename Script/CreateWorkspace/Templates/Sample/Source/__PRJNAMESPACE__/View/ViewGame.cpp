#include <__PRJNAMESPACE__\View\ViewGame.h>

#include <__PRJNAMESPACE__\Application\Renderer.h>

#include <Sable\Graphics\Camera\Perspective.h>
#include <Sable\Graphics\Scene\World.h>
#include <Sable\Graphics\Debug\RenderPass.h>
#include <Sable\Graphics\Common\Manager.h>

using namespace __PRJNAMESPACE__;

IMPLEMENT_MANAGED_CLASS1( __PRJNAMESPACE__, CViewGame, Sable::CView );

CViewGame::CViewGame()
{
}

CViewGame::CViewGame(CApplication& app) : 
    CView()
{
}

CViewGame::~CViewGame()
{
}

Void CViewGame::Initialize()
{
    Sable::CVector3f position;

    // Create Renderer
    CGameRenderer* renderer = NEWOBJ( CGameRenderer, ( GraphicsManager.GetRenderTargetBackBuffer() ) );
    SetRenderer(*renderer);

    // Create Camera
    Sable::CCameraPerspective* camera = NEWOBJ( Sable::CCameraPerspective, () );
    SetCamera(camera);

    // Create World
    Sable::CSceneWorld* world = NEWOBJ( Sable::CSceneWorld, ( *this ) );
    SetWorld( world );

    position.Set(20,20,20.0f);
    camera->SetParent( world->GetRootNode() );
    camera->SetCameraPosition(position);

    CView::Initialize();

    camera->SetAspect( (Float32) renderer->GetRenderTarget().GetHeight() / (Float32) renderer->GetRenderTarget().GetWidth() );
    camera->SetFOV( MathPi / 2.5f );

}

Void CViewGame::Update()
{
    CView::Update();
}

Void CViewGame::Render()
{
    Sable::CDebugRenderPass* debugRp = GetRenderer().GetDebugRenderPass();

    debugRp->PushViewProjMatrix();

    debugRp->BeginLineList();

        debugRp->DrawLine( Sable::CVector3f( 0.0f, 0.0f, 0.0f ), Sable::CVector3f( 0.0f, 1.0f, 0.0f )  );
        debugRp->DrawLine( Sable::CVector3f( 0.0f, 0.0f, 0.0f ), Sable::CVector3f( 0.0f, 0.0f, 1.0f )  );
        debugRp->DrawLine( Sable::CVector3f( 0.0f, 0.0f, 0.0f ), Sable::CVector3f( 1.0f, 0.0f, 0.0f )  );

    debugRp->EndLineList();

    debugRp->PopViewProjMatrix();

    CView::Render();
}