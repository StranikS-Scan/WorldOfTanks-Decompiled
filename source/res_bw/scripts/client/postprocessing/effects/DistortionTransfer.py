# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/DistortionTransfer.py
from PostProcessing.RenderTargets import *
from PostProcessing import Effect
from PostProcessing.Phases import *
from PostProcessing.FilterKernels import *
from PostProcessing import getEffect
from PostProcessing.Effects.Properties import *
from PostProcessing.Effects import implementEffectFactory
import Math
alpha = MaterialFloatProperty('Fisheye', -1, 'alpha', 1, primary=True)
scale = MaterialFloatProperty('Fisheye', -1, 'scale', 1)
tile = MaterialFloatProperty('Fisheye', -1, 'tile', 1)

@implementEffectFactory('Distortion transfer', 'Redraw the scene, using a normal map to distort the image.', 'system/maps/post_processing/hexagonal_norms.bmp')
def distortionTransfer(distortionTexture):
    """This method creates and returns a post-process effect that redraws
    the screen, using a normal map to distort the image.  Use this for
    a fish-eye effect, full-screen shimmer/distort etc.
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    c = buildBackBufferCopyPhase(backBufferCopy)
    r = buildPhase(backBufferCopy.texture, None, 'shaders/post_processing/legacy/transfer_distort.fx', straightTransfer4Tap, BW_BLEND_SRCALPHA, BW_BLEND_INVSRCALPHA)
    r.name = 'distort and transfer'
    r.material.distortionTexture = distortionTexture
    e = Effect()
    e.name = 'Distort and Transfer'
    e.phases = [c, r]
    return e


@implementEffectFactory('Fisheye', 'Distortion transfer that defaults to a fisheye lens effect.')
def fisheye():
    e = distortionTransfer('system/maps/post_processing/fisheye_norms.bmp')
    e.name = 'Fisheye'
    return e
