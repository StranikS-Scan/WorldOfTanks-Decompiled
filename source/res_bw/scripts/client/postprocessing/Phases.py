# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Phases.py
from _PostProcessing import CopyBackBuffer
from _PostProcessing import FilterQuad
from _PostProcessing import TransferQuad
from _PostProcessing import Phase
from FilterKernels import *
from BigWorld import Material
from D3DEnums import *
from functools import partial
s_phaseFactories = {}

class implementPhaseFactory:

    def __init__(self, name, desc, *defaultArgs):
        self.name = name
        self.desc = desc
        self.defaultArgs = defaultArgs

    def __call__(self, f):

        def callFn(*args):
            if len(args) > 0:
                return f(*args)
            else:
                return f(*self.defaultArgs)

        fn = callFn
        s_phaseFactories[self.name] = [self.desc, fn]
        return fn


def getPhaseNames():
    """
            This method returns a list of phase (names,descriptions) used by the
            World Editor.
            Note that editor created phases take no arguments, therefore you
            must provide the default arguments to the underlying build fn in
            the decorator.
    """
    ret = []
    for key in sorted(s_phaseFactories.iterkeys()):
        desc = s_phaseFactories[key][0]
        ret.append((key, desc))

    return ret


def phaseFactory(name):
    """
            This method builds a phase, given the corresponding factory name.
    """
    return s_phaseFactories[name][1]()


backBufferCopyCache = {}

@implementPhaseFactory('<new empty phase>', 'Create a new, empty phase.')
def buildEmptyPhase():
    p = buildTransferPhase(None)
    p.name = 'unnamed phase'
    return p


@implementPhaseFactory('Back buffer copy', 'Resolve the backbuffer into a texture that is usable as an input to other phases.', None)
def buildBackBufferCopyPhase(renderTarget):
    global backBufferCopyCache
    if renderTarget == None:
        from RenderTargets import rt
        renderTarget = rt('PostProcessing/backBufferCopy')
    if backBufferCopyCache.has_key(renderTarget):
        return backBufferCopyCache[renderTarget]
    else:
        c = CopyBackBuffer()
        c.renderTarget = renderTarget
        backBufferCopyCache[renderTarget] = c
        return c


def buildPhase(input, output, fxFile, sampleProvider = straightTransfer4Tap, srcBlend = BW_BLEND_ONE, destBlend = BW_BLEND_ZERO):
    if input == None:
        from RenderTargets import rt
        input = rt('PostProcessing/backBufferCopy').texture
    if sampleProvider == straightTransfer4Tap:
        f = TransferQuad()
    else:
        f = FilterQuad()
        f.samples = sampleProvider()
    p = Phase()
    m = Material(fxFile)
    m.inputTexture = input
    p.filterQuad = f
    p.material = m
    p.material.srcBlend = srcBlend
    p.material.destBlend = destBlend
    p.renderTarget = output
    p.clearRenderTarget = False
    return p


@implementPhaseFactory('Transfer', 'Transfer a texture to the screen or an intermediate texture.', None)
def buildTransferPhase(input, srcBlend = BW_BLEND_ONE, destBlend = BW_BLEND_ZERO):
    p = buildPhase(input, None, 'shaders/post_processing/transfer.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'transfer'
    return p


@implementPhaseFactory('Greyscale', 'Apply a greyscale pixel shader.', None, None)
def buildGreyscalePhase(input, output, srcBlend = BW_BLEND_ONE, destBlend = BW_BLEND_ZERO):
    p = buildPhase(input, output, 'shaders/post_processing/greyscale.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'greyscale'
    return p


@implementPhaseFactory('Down sample', 'Apply a 4-tap downsample filter.', None, None)
def buildDownSamplePhase(input, output):
    p = buildPhase(input, output, 'shaders/post_processing/four-tap_filter.fx', mean9Tap, BW_BLEND_ONE, BW_BLEND_ONE)
    p.name = 'down sample'
    p.clearRenderTarget = True
    return p


@implementPhaseFactory('Colour scale', 'Apply a colour scaling shader, detecting highlights in the scene.', None, None)
def buildColourScalePhase(input, output, srcBlend = BW_BLEND_ONE, destBlend = BW_BLEND_ZERO):
    p = buildPhase(input, output, 'shaders/post_processing/colour_scale.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'colour scale'
    return p


def buildBlurPhase(input, output, horiz, filterMode = 0, width = 1.0):
    if filterMode == 0:
        sampleProv = partial(gaussianBlur4Tap, horiz, width)
    else:
        sampleProv = partial(gaussianBlur24Tap, horiz, width)
    p = buildPhase(input, output, 'shaders/post_processing/gaussian_blur.fx', sampleProv, BW_BLEND_ONE, BW_BLEND_ONE)
    prefix = ['vertical ', 'horizontal '][horiz]
    if filterMode == 0:
        p.name = prefix + '4-tap blur'
    else:
        p.name = prefix + '24-tap blur'
    p.clearRenderTarget = True
    return p


@implementPhaseFactory('Horizontal blur', 'Horiztonally blur the scene.')
def buildHorizontalBlurPhase():
    return buildBlurPhase(None, None, 1)


@implementPhaseFactory('Vertical blur', 'Vertically blur the scene.')
def buildVerticalBlurPhase():
    return buildBlurPhase(None, None, 0)


@implementPhaseFactory('Colour correction', 'Apply tone mapping using a lookup texture', None, 'system/maps/post_processing/colour_correct.dds', None)
def buildColourCorrectionPhase(input, lookupTexture, output, srcBlend = BW_BLEND_SRCALPHA, destBlend = BW_BLEND_INVSRCALPHA):
    p = buildPhase(input, output, 'shaders/post_processing/colour_correct.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.material.lookupTexture = lookupTexture
    p.name = 'colour correct'
    return p


@implementPhaseFactory('HSV colour correction', 'Adjust the hue, saturation or value (brightness) of the scene.', None, None)
def buildHSVColourCorrectionPhase(input, output, srcBlend = BW_BLEND_SRCALPHA, destBlend = BW_BLEND_INVSRCALPHA):
    p = buildPhase(input, output, 'shaders/post_processing/colour_correct_hsv.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'HSV colour correct'
    return p


@implementPhaseFactory('N-tap filter', 'Apply an arbitrary n-tap filter kernel.', None, None, mean9Tap)
def buildNTapFilterPhase(input, output, filter, srcBlend = BW_BLEND_ONE, destBlend = BW_BLEND_ZERO):
    p = buildPhase(input, output, 'shaders/post_processing/n-tap_filter.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'n-tap filter'
    taps = filter()
    idx = 0
    for u, v, weight in taps:
        setattr(p.material, 'tap%d' % (idx,), (u,
         v,
         weight,
         0))
        idx += 1

    return p


@implementPhaseFactory('9-tap filter', 'Apply a 9-tap filter kernel.', None, None, mean9Tap)
def build9TapFilterPhase(input, output, filter, srcBlend = BW_BLEND_SRCALPHA, destBlend = BW_BLEND_INVSRCALPHA):
    p = buildPhase(input, output, 'shaders/post_processing/nine-tap_filter.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = '9-tap filter'
    taps = filter()
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


@implementPhaseFactory('Edge dilation', 'Apply a dilation filter to the scene.', None, None)
def buildEdgeDilationPhase(input, output, srcBlend = BW_BLEND_ONE, destBlend = BW_BLEND_ZERO):
    p = buildPhase(input, output, 'shaders/post_processing/dilate.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'dilation'
    p.material.tap1 = (-1, 0, 1, 0)
    p.material.tap2 = (1, 0, 1, 0)
    p.material.tap3 = (0, 1, 1, 0)
    p.material.tap4 = (0, -1, 1, 0)
    p.material.tap5 = (0, 0, 1, 0)
    return p


@implementPhaseFactory('Vignette', 'Overlay a vignette texture on the screen.', 'system/maps/post_processing/film_grain/vignette.tga')
def buildVignettePhase(input):
    p = buildPhase(input, None, 'shaders/post_processing/transfer.fx', straightTransfer4Tap, BW_BLEND_SRCALPHA, BW_BLEND_INVSRCALPHA)
    p.material.alpha = 0.5
    p.name = 'vignette'
    return p


def finiPhases():
    global backBufferCopyCache
    print 'PostProcessing.Phases.fini()'
    backBufferCopyCache = {}
