#ifndef ___PRJNAMESPACE___APPLICATION_RENDERER_
#define ___PRJNAMESPACE___APPLICATION_RENDERER_

#include <Sable/Core/Common/DataTypes.h>

#include <Sable/Graphics/Renderer/Header.h>

#define RENDERERPASS_DEPTH 0
#define RENDERERPASS_STATIC_LIGHTING 1

namespace Sable
{
    class CRenderPassDepth;
    class CRenderPassLighting;
    class CGuiRenderPass;
    class CDebugRenderPass;
}

namespace __PRJNAMESPACE__
{

/** 
\ingroup GraphicsRenderer
Represent the Main Renderer of the system.
\n It can be queried to create material using CMainRenderer::CreateMaterial
*/
class CGameRenderer : public Sable::CRenderer
{
	DEFINE_MANAGED_CLASS( CGameRenderer );

public:

	/** @name Operator*/
	//@{
	CGameRenderer( const Sable::CRenderTarget& renderTaget );
	~CGameRenderer();
	//@}

	/** @name Accessors*/
	//@{
    Sable::CDebugRenderPass&                 GetDebugRenderer() const;
	//@}

	/** @name Manipulator*/
	//@{
	virtual		Void	Initialize( Sable::CView& view );
	virtual		Void	UnInitialize();
	virtual		Void	Render();
	//@}

private:	

	// Types
	
	// Method

	// Attribute
	Sable::CRef<Sable::CRenderPassDepth>           m_RendererPassDeth ;
	Sable::CRef<Sable::CRenderPassLighting>         m_RendererPassDefault ;
    Sable::CRef<Sable::CGuiRenderPass>              m_UIRendererPass;
    Sable::CRef<Sable::CDebugRenderPass>           m_DebugRenderer;

	// Static Attributes

};

Inline
Sable::CDebugRenderPass& CGameRenderer::GetDebugRenderer() const
{
    return *m_DebugRenderer;
}

}

#endif
