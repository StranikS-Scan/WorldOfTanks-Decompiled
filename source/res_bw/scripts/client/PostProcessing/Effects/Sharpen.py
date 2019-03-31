# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/Sharpen.py
# Compiled at: 2010-05-25 20:46:16
from PostProcessing.RenderTargets import *
from PostProcessing import Effect
from PostProcessing.Phases import build9TapFilterPhase
from PostProcessing.Phases import buildBackBufferCopyPhase
from PostProcessing.FilterKernels import *
from PostProcessing import chain
from PostProcessing.Effects.Properties import *
from PostProcessing.Effects import implementEffectFactory
import Math
amount = MaterialFloatProperty('Sharpen', -1, 'alpha', primary=True)

@implementEffectFactory('Sharpen', 'Sharpen the edges of the scene.')
def sharpen():
    """This method creates and returns a post-process effect that sharpens
    the back buffer.  It does this by using a generic sharpening filter kernel.
    """
    backBufferCopy = rt('backBufferCopy')
    c = buildBackBufferCopyPhase(backBufferCopy)
    s = build9TapFilterPhase(backBufferCopy.texture, None, sharpFilter)
    e = Effect()
    e.name = 'Sharpen'
    e.phases = [c, s]
    return e
