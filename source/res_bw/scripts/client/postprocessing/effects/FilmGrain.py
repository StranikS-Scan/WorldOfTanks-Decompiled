# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/FilmGrain.py
from PostProcessing.RenderTargets import *
from PostProcessing import Effect
from PostProcessing.Phases import *
from PostProcessing.FilterKernels import *
from PostProcessing.Effects.Properties import *
from PostProcessing.Effects import implementEffectFactory
import Math
_effectName = 'Film Grain'
alpha = MaterialFloatProperty(_effectName, -2, 'alpha')
speed = MaterialFloatProperty(_effectName, -2, 'speed')
scale = MaterialFloatProperty(_effectName, -2, 'scale')
alpha2 = MaterialFloatProperty(_effectName, -1, 'alpha')
speed2 = MaterialFloatProperty(_effectName, -1, 'speed')
scale2 = MaterialFloatProperty(_effectName, -1, 'scale')

def buildFilmGrainPhase(inputTextures, punchcard, output, fxFile, sampleProvider = straightTransfer4Tap, srcBlend = BW_BLEND_ONE, destBlend = BW_BLEND_ZERO):
    p = Phase()
    m = Material(fxFile)
    m.punchcard = punchcard
    for i in xrange(0, 6):
        atr = 'inputTexture%d' % (i,)
        setattr(m, atr, inputTextures[i])

    p.filterQuad = TransferQuad()
    p.material = m
    p.material.srcBlend = srcBlend
    p.material.destBlend = destBlend
    p.renderTarget = output
    p.clearRenderTarget = False
    p.name = 'dust and scratches'
    return p


@implementEffectFactory('Film grain', 'Simulated Film Grain overlay.')
def filmGrain():
    """This method creates and returns a post-process effect that draws
    film grain, using 7 texture maps and a 'punch card' texture.  The
    'punch card' is a 7 * n bmp that describes the position on-screen
    of each of the 7 maps at any time..
    """
    textures = []
    base = 'system/maps/post_processing/film_grain/'
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    bbc = buildBackBufferCopyPhase(backBufferCopy)
    c = buildColourCorrectionPhase(backBufferCopy.texture, 'system/maps/post_processing/film_grain/colour_correct_oldfilm.bmp', None)
    for i in xrange(0, 2):
        textures.append('%sscratch_0%s.tga' % (base, str(i + 1)))

    for i in xrange(0, 4):
        textures.append('%sdirt_0%s.tga' % (base, str(i + 1)))

    punchcard = base + 'oldfilm_punchcard.bmp'
    fg = buildFilmGrainPhase(textures, punchcard, None, 'shaders/post_processing/legacy/film_grain.fx', straightTransfer4Tap, BW_BLEND_SRCALPHA, BW_BLEND_INVSRCALPHA)
    textures = []
    for i in xrange(2, 4):
        textures.append('%sscratch_0%s.tga' % (base, str(i + 1)))

    for i in xrange(4, 8):
        textures.append('%sdirt_0%s.tga' % (base, str(i + 1)))

    punchcard = base + 'oldfilm_punchcard.bmp'
    fg2 = buildFilmGrainPhase(textures, punchcard, None, 'shaders/post_processing/legacy/film_grain.fx', straightTransfer4Tap, BW_BLEND_SRCALPHA, BW_BLEND_INVSRCALPHA)
    fg2.material.punchcardOffset = 0.5
    v = buildVignettePhase()
    e = Effect()
    e.name = _effectName
    e.phases = [bbc,
     c,
     fg,
     fg2,
     v]
    fg.material.alpha = 0.3
    fg.material.speed = 0.3
    fg.material.scale = 50.0
    fg2.material.alpha = 0.12
    fg.material.speed = 0.01
    fg2.material.scale = 21.0
    return e
