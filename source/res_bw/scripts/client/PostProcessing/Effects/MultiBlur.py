# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/MultiBlur.py
# Compiled at: 2010-05-25 20:46:16
from PostProcessing.RenderTargets import *
from PostProcessing.Phases import *
from PostProcessing import Effect
from PostProcessing.Effects import implementEffectFactory

@implementEffectFactory('Multi blur', 'Store multiple levels of blur of the scene in intermediate textures.  This is required by the depthOfField3 Effect.')
def multiBlur(filterMode=0):
    """This method creates and returns an effect that down-samples and
    blurs the back-buffer.  *It relies on the down sample buffers already
    having been created*.  It fills the     downSampleBlur1/2/3 render targets."""
    downSample1 = rt('downSample1')
    downSample1B = rt('downSample1B')
    downSample2B = rt('downSample2B')
    downSample3B = rt('downSample3B')
    downSampleBlur1 = rt('downSampleBlur1')
    downSampleBlur2 = rt('downSampleBlur2')
    downSampleBlur3 = rt('downSampleBlur3')
    bh1 = buildBlurPhase(downSample1.texture, downSample1B, True, filterMode, 1.0)
    bv1 = buildBlurPhase(downSample1B.texture, downSampleBlur1, False, filterMode, 1.0)
    bh2 = buildBlurPhase(downSampleBlur1.texture, downSample2B, True, filterMode, 1.0)
    bv2 = buildBlurPhase(downSample2B.texture, downSampleBlur2, False, filterMode, 1.0)
    bh2a = buildBlurPhase(downSampleBlur2.texture, downSample2B, True, filterMode, 1.0)
    bv2a = buildBlurPhase(downSample2B.texture, downSampleBlur2, False, filterMode, 1.0)
    bh3 = buildBlurPhase(downSampleBlur2.texture, downSample3B, True, filterMode, 1.0)
    bv3 = buildBlurPhase(downSample3B.texture, downSampleBlur3, False, filterMode, 1.0)
    bh3a = buildBlurPhase(downSampleBlur3.texture, downSample3B, True, filterMode, 1.0)
    bv3a = buildBlurPhase(downSample3B.texture, downSampleBlur3, False, filterMode, 1.0)
    e = Effect()
    e.name = 'Multi Blur'
    phases = [bh1,
     bv1,
     bh2,
     bv2,
     bh3,
     bv3,
     bh3a,
     bv3a]
    e.phases = phases
    return e
