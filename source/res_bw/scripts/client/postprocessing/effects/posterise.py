# Embedded file name: scripts/client/PostProcessing/Effects/Posterise.py
from PostProcessing.RenderTargets import *
from PostProcessing import Effect
from PostProcessing.Phases import *
from PostProcessing.FilterKernels import *
from PostProcessing.D3DEnums import *
from PostProcessing import chain
from PostProcessing.Effects.Properties import *
from PostProcessing.Effects import implementEffectFactory
import Math
amount = BypassProperty('Posterise and Edge', primary=True)
edgeDilation = MaterialFloatProperty('Posterise and Edge', -2, 'threshold')

@implementPhaseFactory('Kuwahara mean-variance', 'Apply a Kuwahara mean-variance filter and store the intermediate results.', None, None)
def buildMeanVariancePhase(input, output):
    p = buildPhase(input, output, 'shaders/post_processing/legacy/kuwahara_mean_variance.fx', straightTransfer4Tap, BW_BLEND_ONE, BW_BLEND_ZERO)
    p.name = 'kuwahara mean-variance'
    taps = mean9Tap()
    p.material.tap1 = (taps[0][0],
     taps[0][1],
     taps[0][2],
     0)
    p.material.tap2 = (taps[1][0],
     taps[1][1],
     taps[1][2],
     0)
    p.material.tap3 = (taps[2][0],
     taps[2][1],
     taps[2][2],
     0)
    p.material.tap4 = (taps[3][0],
     taps[3][1],
     taps[3][2],
     0)
    p.material.tap5 = (taps[4][0],
     taps[4][1],
     taps[4][2],
     0)
    p.material.tap6 = (taps[5][0],
     taps[5][1],
     taps[5][2],
     0)
    p.material.tap7 = (taps[6][0],
     taps[6][1],
     taps[6][2],
     0)
    p.material.tap8 = (taps[7][0],
     taps[7][1],
     taps[7][2],
     0)
    p.material.tap9 = (taps[8][0],
     taps[8][1],
     taps[8][2],
     0)
    return p


@implementPhaseFactory('Kuwahara mean-variance select', 'Look up the mean-variance filter results and select the colour with the mean variance.', None, None)
def buildVarianceSelectPhase(input, output):
    p = buildPhase(input, output, 'shaders/post_processing/legacy/kuwahara_variance_select.fx', straightTransfer4Tap, BW_BLEND_ONE, BW_BLEND_ZERO)
    p.name = 'kuwahara mean-variance select'
    p.material.tap1 = (-1, 1, 1, 0)
    p.material.tap2 = (-1, -1, 1, 0)
    p.material.tap3 = (1, 1, 1, 0)
    p.material.tap4 = (1, -1, 1, 0)
    return p


@implementEffectFactory('Posterise', 'Posterise the scene colours using a noise-reducing, edge-preserving filter.')
def posterise():
    """This method creates and returns a post-process effect that posterises
    the back buffer.  It does this by using a Kuwahara filter, which is a
    noise-reduction filter that preserves edges."""
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    downSample1 = rt('PostProcessing/downSample1')
    downSample1B = rt('PostProcessing/downSample1B')
    c = buildBackBufferCopyPhase(backBufferCopy)
    d0 = buildDownSamplePhase(backBufferCopy.texture, downSample1)
    computeMeanVariance = buildMeanVariancePhase(downSample1.texture, downSample1B)
    selectVariance = buildVarianceSelectPhase(downSample1B.texture, None)
    e = Effect()
    e.name = 'Posterise'
    e.phases = [c,
     d0,
     computeMeanVariance,
     selectVariance]
    return e


@implementEffectFactory('Posterise and edge', 'Posterise the scene colours, then detect and draw edges.')
def posteriseAndEdge():
    """This method creates and returns a post-process effect that posterises
    the back buffer and draws black edges.  It does this by using a Kuwahara
    filter, which is a noise-reduction filter that preserves edges. It then
    performs edge detection and dilation and blends the results back over the
    posterised back buffer."""
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    backBufferCopyB = rt('PostProcessing/backBufferCopyB')
    downSample1 = rt('PostProcessing/downSample1')
    downSample1B = rt('PostProcessing/downSample1B')
    c = buildBackBufferCopyPhase(backBufferCopy)
    c2 = buildBackBufferCopyPhase(backBufferCopyB)
    d0 = buildDownSamplePhase(backBufferCopy.texture, downSample1)
    computeMeanVariance = buildMeanVariancePhase(downSample1.texture, downSample1B)
    selectVariance = buildVarianceSelectPhase(downSample1B.texture, None)
    s = build9TapFilterPhase(backBufferCopyB.texture, backBufferCopy, edgeDetectFilter)
    d = buildEdgeDilationPhase(backBufferCopy.texture, backBufferCopyB)
    t = buildTransferPhase(backBufferCopyB.texture, BW_BLEND_ZERO, BW_BLEND_SRCCOLOR)
    e = Effect()
    e.name = 'Posterise and Edge'
    e.phases = [c,
     c2,
     d0,
     computeMeanVariance,
     selectVariance,
     s,
     d,
     t]
    return e
