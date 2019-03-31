# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/EdgeDetect.py
# Compiled at: 2010-05-25 20:46:16
import BigWorld
from PostProcessing.RenderTargets import *
from PostProcessing import Effect
from PostProcessing.Phases import *
from PostProcessing.FilterKernels import *
from PostProcessing.Effects import implementEffectFactory

@implementEffectFactory('Edge detect', 'Detect and draw the edges in the scene.')
def edgeDetect():
    """This method creates and returns a post-process effect that performs
    edge detection and dilation of the resultant edges."""
    backBufferCopy = rt('backBufferCopy')
    c = buildBackBufferCopyPhase(backBufferCopy)
    s = build9TapFilterPhase(backBufferCopy.texture, None, edgeDetectFilter)
    d = buildEdgeDilationPhase(backBufferCopy.texture, None)
    e = Effect()
    e.name = 'Edge Detect'
    e.phases = [c,
     s,
     c,
     d]
    return e
