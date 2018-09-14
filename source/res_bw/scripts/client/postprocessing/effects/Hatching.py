# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/Hatching.py
from PostProcessing.RenderTargets import *
from PostProcessing.Phases import *
from PostProcessing import Effect
from PostProcessing import chain
from PostProcessing.Effects.Properties import *
from PostProcessing.Effects import implementEffectFactory
import Math
scale = MaterialFloatProperty('Hatching', -1, 'scale', primary=True)
power = MaterialFloatProperty('Hatching', -1, 'power')
tile = MaterialFloatProperty('Hatching', -1, 'tile')

@implementEffectFactory('Hatching', 'Simulated pencil cross-hatching.')
def hatching(texName = 'system/maps/post_processing/hatching.dds'):
    """This method creates and returns a post-process effect that performs
    hatching, or a pencil sketch effect.  It requires the back buffer,
    and a texture containing 3 individual channels of response to the
    different information created by processing the back buffer
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    c = buildBackBufferCopyPhase(backBufferCopy)
    p = buildPhase(backBufferCopy.texture, None, 'shaders/post_processing/legacy/hatching.fx', straightTransfer4Tap, BW_BLEND_SRCALPHA, BW_BLEND_INVSRCALPHA)
    p.name = 'hatching'
    p.material.hatchTexture = 'system/maps/post_processing/hatch.bmp'
    p.material.offsetTexture = 'system/maps/post_processing/hatch_offset.bmp'
    e = Effect()
    e.name = 'Hatching'
    e.phases = [c, p]
    return e
