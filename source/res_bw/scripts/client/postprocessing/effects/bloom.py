# Embedded file name: scripts/client/PostProcessing/Effects/Bloom.py
from PostProcessing.RenderTargets import *
from PostProcessing.Phases import *
from PostProcessing import Effect
from PostProcessing.Effects.Properties import *
from PostProcessing.Effects import implementEffectFactory
amount = MaterialFloatProperty('Bloom', -1, 'alpha', primary=True)

@implementEffectFactory('Bloom', 'Detect the highlights in the scene, blur them and add them back over the scene. Requires the downSample Effect.')
def bloom(filterMode = 0, attenuation = (1, 1, 1, 1), numPasses = 3, width = 1.0, power = 8):
    """This method creates and returns a bloom post-process effect.  It assumes
    the scene has been captured and downsampled into the downSample3 render target."""
    downSample3 = rt('PostProcessing/downSample3')
    computeBuffer1 = rt('PostProcessing/computeBuffer1')
    computeBuffer2 = rt('PostProcessing/computeBuffer2')
    c0 = buildColourScalePhase(downSample3.texture, computeBuffer2)
    c0.material.power = power
    phases = [c0]
    for n in xrange(0, numPasses):
        bh = buildBlurPhase(computeBuffer2.texture, computeBuffer1, True, filterMode, width)
        bh.material.attenuation = attenuation
        bv = buildBlurPhase(computeBuffer1.texture, computeBuffer2, False, filterMode, width)
        phases.append(bh)
        phases.append(bv)
        width *= 2.0

    t = buildTransferPhase(computeBuffer2.texture, BW_BLEND_SRCALPHA, BW_BLEND_ONE)
    phases.append(t)
    e = Effect()
    e.name = 'Bloom'
    e.phases = phases
    return e


@implementEffectFactory('Blur', 'Blur the scene. Requires the downSample Effect.')
def blur(filterMode = 0, attenuation = (1, 1, 1, 1), numPasses = 1, width = 1.0):
    """This method creates and returns a blur post-process effect.  It assumes
    the scene has been captured and downsampled into the downSample3 render target."""
    downSample3 = rt('PostProcessing/downSample3')
    computeBuffer1 = rt('PostProcessing/computeBuffer1')
    computeBuffer2 = rt('PostProcessing/computeBuffer2')
    phases = []
    if numPasses > 0:
        bh = buildBlurPhase(downSample3.texture, computeBuffer1, True, filterMode, width)
        bh.material.attenuation = attenuation
        bv = buildBlurPhase(computeBuffer1.texture, computeBuffer2, False, filterMode, width)
        phases.append(bh)
        phases.append(bv)
    if numPasses > 1:
        bh = buildBlurPhase(computeBuffer2.texture, computeBuffer1, True, filterMode, width)
        bh.material.attenuation = attenuation
        bv = buildBlurPhase(computeBuffer1.texture, computeBuffer2, False, filterMode, width)
        for n in xrange(1, numPasses):
            phases.append(bh)
            phases.append(bv)

    t = buildTransferPhase(computeBuffer2.texture, BW_BLEND_SRCALPHA, BW_BLEND_ZERO)
    phases.append(t)
    e = Effect()
    e.name = 'Blur'
    e.phases = phases
    return e


@implementEffectFactory('Streak', 'Variation on blooming, emphasising horizontal blurring of the highlights. Requires the downSample Effect.')
def streak():
    """This method creates and returns a variation on the standard bloom
    post-process effect.  It only performs horizontal blurs, thus producing
    more of a streak than a blur."""
    downSample3 = rt('PostProcessing/downSample3')
    computeBuffer1 = rt('PostProcessing/computeBuffer1')
    computeBuffer2 = rt('PostProcessing/computeBuffer2')
    c0 = buildColourScalePhase(downSample3.texture, computeBuffer2)
    phases = [c0]
    width = 1.0
    for i in xrange(0, 2):
        bh = buildBlurPhase(computeBuffer2.texture, computeBuffer1, True, 0, width)
        phases.append(bh)
        bh2 = buildBlurPhase(computeBuffer1.texture, computeBuffer2, True, 0, width * 2.0)
        phases.append(bh2)
        width *= 4.0

    t = buildTransferPhase(computeBuffer2.texture, BW_BLEND_SRCALPHA, BW_BLEND_ONE)
    phases.append(t)
    e = Effect()
    e.name = 'Bloom (Streak)'
    e.phases = phases
    return e
