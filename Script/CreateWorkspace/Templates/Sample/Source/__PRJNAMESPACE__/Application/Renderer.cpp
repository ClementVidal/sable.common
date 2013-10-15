#include <__PRJNAMESPACE__\Application\Renderer.h>

#include <Sable\Graphics\RenderPass\Header.h>
#include <Sable\Graphics\Debug\RenderPass.h>
#include <Sable\Graphics\RenderTarget\Texture.h>
#include <Sable\Gui\Common\RenderPass.h>
#include <Sable\Graphics\Text\Font.h>

using namespace __PRJNAMESPACE__;
using namespace Sable;

class Sable::CRenderPass;

IMPLEMENT_MANAGED_CLASS1( __PRJNAMESPACE__, CGameRenderer, CRenderer );

CGameRenderer::CGameRenderer( const CRenderTarget& renderTarget ) :
    CRenderer( renderTarget )
{

}

CGameRenderer::~CGameRenderer()
{

}

Void CGameRenderer::Initialize( Sable::CView& view )
{
	CRef< CTextFont > font = NEWOBJ( CTextFont, () );
	font->SetFilePath( FileSystem.GetFilePath( "System", "Font/Default.dfnt" ) );
	font->Load();

    m_RendererPassDeth = NEWOBJ( CRenderPassDepth, ( *this ) );
    m_RendererPassDefault = NEWOBJ( CRenderPassLighting, ( *this ) );
	m_UIRendererPass = NEWOBJ( CGuiRenderPass, ( *this, *font ) );
    m_DebugRenderer = NEWOBJ( CDebugRenderPass, ( *this ) );

    CRenderer::Initialize( view );

	PushRenderPass( *m_RendererPassDeth );
	PushRenderPass( *m_RendererPassDefault );
	PushRenderPass( *m_DebugRenderer );
	PushRenderPass( *m_UIRendererPass );

    m_RendererPassDeth->Initialize(*this);
    m_RendererPassDefault->Initialize(*this );
    m_DebugRenderer->Initialize(*this );
    m_UIRendererPass->Initialize(*this );

}

Void CGameRenderer::UnInitialize()
{
	CRenderer::UnInitialize();
}

Void CGameRenderer::Render()
{
    m_UIRendererPass->Update();

    {
		DebugGraphicCommandGroup( "SampleRenderer" );
		CRenderer::Render();
	}
}
