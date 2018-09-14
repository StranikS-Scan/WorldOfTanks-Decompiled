# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/FXAA.py
from PostProcessing.RenderTargets import *
from PostProcessing import Effect
from PostProcessing.Phases import *
from PostProcessing.Effects import implementEffectFactory

@implementEffectFactory('FXAA', 'FXAA anti-aliasing.')
def FXAA():
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    c = buildBackBufferCopyPhase(backBufferCopy)
    lum = buildPhase(backBufferCopy.texture, None, 'shaders/anti_aliasing/fxaa_worldeditor_integration_luminance.fx', straightTransfer4Tap, BW_BLEND_ONE, BW_BLEND_ZERO)
    lum.name = 'luminance'
    lum.renderTarget = backBufferCopy
    r = buildPhase(backBufferCopy.texture, None, 'shaders/anti_aliasing/fxaa_worldeditor_integration.fx', straightTransfer4Tap, BW_BLEND_ONE, BW_BLEND_ZERO)
    r.name = 'transfer'
    e = Effect()
    e.name = 'FXAA'
    e.phases = [c, lum, r]
    return e
