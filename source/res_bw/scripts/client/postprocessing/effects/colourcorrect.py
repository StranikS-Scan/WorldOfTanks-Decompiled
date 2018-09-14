# Embedded file name: scripts/client/PostProcessing/Effects/ColourCorrect.py
from PostProcessing.RenderTargets import *
from PostProcessing.Phases import *
from PostProcessing import Effect
from PostProcessing import chain
from PostProcessing.Effects.Properties import *
from PostProcessing.Effects import implementEffectFactory
import Math
_colourCorrectEffectName = 'Colour Correct'
_hsvColourCorrectEffectName = 'HSV Colour Correct'
amount = MaterialFloatProperty(_colourCorrectEffectName, -1, 'alpha', primary=True)
saturation = MaterialFloatProperty('HSV Colour Correct', -1, 'saturation', primary=True)
brightness = MaterialFloatProperty('HSV Colour Correct', -1, 'brightness')
types = ['system/maps/post_processing/colour_correct.bmp',
 'system/maps/post_processing/s_curve/s_curve.bmp',
 'system/maps/post_processing/blood_rage/blood_rage.bmp',
 'system/maps/post_processing/heat/heat.bmp',
 'system/maps/post_processing/night_vision/night_vision.bmp',
 'system/maps/post_processing/old_film/old_film.bmp',
 'system/maps/post_processing/quantise01/quantise02.bmp',
 'system/maps/post_processing/spectrum/spectrum.bmp']
toneMap = MaterialTextureProperty(_colourCorrectEffectName, -1, 'lookupTexture', types)

@implementEffectFactory('Colour correct', 'Apply a tone-map to the colours in the scene using a lookup texture.')
def colourCorrect(texName = 'system/maps/post_processing/colour_correct.dds'):
    """This method creates and returns a post-process effect that performs
    colour correction, or tone mapping, based on the colour_correct.fx effect.
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    e = Effect()
    e.name = _colourCorrectEffectName
    c = buildBackBufferCopyPhase(backBufferCopy)
    p = buildColourCorrectionPhase(backBufferCopy.texture, texName, None)
    e.phases = [c, p]
    return e


@implementEffectFactory('Colour correct HSV', 'Adjust the hue, saturation and value(brightness) of the scene.')
def colourCorrectHSV():
    """This method creates and returns a post-process effect that performs
    hsv colour correction, or tone mapping, based on the colour_correct_hsv.fx effect.
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    e = Effect()
    e.name = _hsvColourCorrectEffectName
    c = buildBackBufferCopyPhase(backBufferCopy)
    p = buildHSVColourCorrectionPhase(backBufferCopy.texture, None)
    e.phases = [c, p]
    return e
