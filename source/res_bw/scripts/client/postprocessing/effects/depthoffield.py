# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/DepthOfField.py
from PostProcessing.RenderTargets import *
from PostProcessing import Effect
from PostProcessing.Phases import *
from PostProcessing.FilterKernels import *
from PostProcessing import chain
from PostProcessing import PointSpriteTransferMesh
from PostProcessing import getEffect
from PostProcessing.Effects.Properties import *
from PostProcessing.Effects import implementEffectFactory
from PostProcessing.Phases import implementPhaseFactory
import Math
import math

def stochasticSample():
    w = 1.0 / 12.0
    taps = [(-0.326212, -0.40581, w),
     (-0.840144, -0.07358, w),
     (-0.695914, 0.457137, w),
     (-0.203345, 0.620716, w),
     (0.96234, -0.194983, w),
     (0.473434, -0.480026, w),
     (0.519456, 0.767022, w),
     (0.185461, -0.89124, w),
     (0.507431, 0.064425, w),
     (0.89642, 0.412458, w),
     (-0.32194, -0.932615, w),
     (-0.791559, -0.59771, w)]
    return taps


zFocus = MaterialFloatProperty('Thin Lens Simulation', -1, 'zFocus', 1)
bkzFocus = MaterialFloatProperty('Depth of Field (bokeh control)', 1, 'zFocus', 1)

class FocalLengthProperty(MaterialFloatProperty):

    def __init__(self, effectName, phaseIdx, materialAttribute, primary=False):
        MaterialFloatProperty.__init__(self, effectName, phaseIdx, materialAttribute, 2, primary)

    def format(self, val):
        v = self.get()
        return '%0.0fmm' % (v * 1000.0,)


focalLength = FocalLengthProperty('Thin Lens Simulation', -1, 'focalLen', True)
bkfocalLength = FocalLengthProperty('Depth of Field (bokeh control)', 1, 'focalLen', True)

class ApertureProperty(MaterialFloatProperty):

    def __init__(self, effectName, phaseIdx, materialAttribute):
        MaterialFloatProperty.__init__(self, effectName, phaseIdx, materialAttribute)

    def format(self, val):
        v = self.get()
        f = focalLength.get()
        return 'f/%0.1f' % (f / v,)


aperture = ApertureProperty('Thin Lens Simulation', -1, 'aperture')
bkaperture = ApertureProperty('Bokeh', 1, 'aperture')
falloff = MaterialFloatProperty('Explicit Lens Simulation', -1, 'falloff', primary=True)
zNear = MaterialFloatProperty('Explicit Lens Simulation', -1, 'zNear', 1)
zFar = MaterialFloatProperty('Explicit Lens Simulation', -1, 'zFar', 1)
bokehAmount = MaterialFloatProperty('Depth of Field (bokeh control)', -2, 'bokehAmount', primary=True)
maxCoC2 = MaterialFloatProperty('Depth of Field (bokeh control)', -2, 'maxCoC')
types = ['system/maps/col_white.dds',
 'system/maps/post_processing/bokeh.tga',
 'system/maps/post_processing/bokeh2.tga',
 'system/maps/post_processing/bokeh3.tga']
bokehType = MaterialTextureProperty('Depth of Field (bokeh control)', -2, 'bokehTexture', types)
dof3Alpha = MaterialFloatProperty('Depth of Field (multi-blur)', -1, 'alpha', primary=True)
dof3Overdrive = MaterialFloatProperty('Depth of Field (multi-blur)', -1, 'overdrive')

@implementPhaseFactory('Thin lens simulation', 'Mathematical thin lens simulation. Provides the intermediate data for depth of field phases.', None, None)
def buildThinLensSimulationPhase(input, output, srcBlend=BW_BLEND_ONE, destBlend=BW_BLEND_ZERO):
    p = buildPhase(input, output, 'shaders/post_processing/depth_blur_write.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'thin lens'
    return p


@implementPhaseFactory('Explicit lens simulation', 'Explicit control over lens parameters.  Provides the intermediate data for depth of field phases.', None, None)
def buildExplicitLensSimulationPhase(input, output, srcBlend=BW_BLEND_ONE, destBlend=BW_BLEND_ZERO):
    p = buildPhase(input, output, 'shaders/post_processing/depth_blur_write2.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'explicit lens'
    return p


@implementPhaseFactory('Depth of Field (variable filter)', 'Depth of field using a variable sized filter. Fast, but low quality. Requires intermediate data from a lens simulation.', None, None, None, stochasticSample)
def buildDOFVariableCoCPhase(input, depthBlurTexture, output, filter, srcBlend=BW_BLEND_ONE, destBlend=BW_BLEND_ZERO):
    """This depth-of-field output phase uses a variable-sized kernel to simulate
    the circle of confusion for depth-of-field."""
    p = buildPhase(input, output, 'shaders/post_processing/depth_of_field.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.name = 'depth of field (variable filter)'
    p.material.inputTexture = input
    p.material.depthBlurTexture = depthBlurTexture
    taps = filter()
    idx = 0
    for u, v, weight in taps:
        setattr(p.material, 'tap%d' % (idx,), (u,
         v,
         weight,
         0))
        idx += 1

    return p


@implementPhaseFactory('Depth of Field (bokeh control)', 'Depth of field using bokeh texture splatting. Slow, but high quality. Requires intermediate data from a lens simulation.', None, None, None)
def buildDOFBokehControlPhase(input, depthBlurTexture, output, srcBlend=BW_BLEND_SRCALPHA, destBlend=BW_BLEND_ONE):
    """This depth-of-field output phase uses variable-sized point sprites
    to simulate the circle of confusion for depth-of-field.  It accepts
    an arbitrary bokeh texture map, but uses large amounts of fill-rate."""
    p = buildPhase(input, output, 'shaders/post_processing/depth_of_field2.fx', straightTransfer4Tap, srcBlend, destBlend)
    oldFilterQuad = p.filterQuad
    p.filterQuad = PointSpriteTransferMesh()
    p.name = 'depth of field (bokeh control)'
    p.material.inputTexture = input
    p.material.depthBlurTexture = depthBlurTexture
    p.clearRenderTarget = True
    return p


@implementPhaseFactory('Depth of Field transfer (bokeh control)', 'Depth of field transfer phase specifically for use by depth-of-field (bokeh control).', None, None)
def buildDOFBokehControlTransferPhase(inputTexture, depthBlurTexture, srcBlend=BW_BLEND_SRCALPHA, destBlend=BW_BLEND_INVSRCALPHA):
    p = buildPhase(inputTexture, None, 'shaders/post_processing/depth_of_field2_transfer.fx', straightTransfer4Tap, srcBlend, destBlend)
    p.material.depthBlurTexture = depthBlurTexture
    p.name = 'depth of field transfer (bokeh control)'
    return p


@implementEffectFactory('Thin lens simulation', 'Thin-lens simulation for depth-of-field effects, offering control similar to an SLR camera lens.')
def lensSimulation():
    """This method creates and returns a post-process effect that performs
    lens simulation. It does this mathematically via the thin-lens formula,
    simulating focal length, aperture and zFocus.  It outputs to an
    intermediate buffer, designed for use by one of the depth-of-field
    simulations.
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    fpComputeBuffer1 = rt('PostProcessing/fpComputeBuffer1')
    c = buildBackBufferCopyPhase(backBufferCopy)
    w = buildThinLensSimulationPhase(backBufferCopy.texture, fpComputeBuffer1)
    e = Effect()
    e.name = 'Thin Lens Simulation'
    e.phases = [c, w]
    return e


@implementEffectFactory('Explicit lens simulation', 'Lens simulation for depth-of-field effects that offers direct control over the blur amount and falloff.')
def lensExplicit():
    """This method creates and returns a post-process effect that performs
    lens simulation. It allows direct control over the depth-of-field area
    and the falloff gradients.  It outputs to an intermediate buffer,
    designed for use by one of the depth-of-field simulations.
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    fpComputeBuffer1 = rt('PostProcessing/fpComputeBuffer1')
    c = buildBackBufferCopyPhase(backBufferCopy)
    w = buildExplicitLensSimulationPhase(backBufferCopy.texture, fpComputeBuffer1)
    e = Effect()
    e.name = 'Explicit Lens Simulation'
    e.phases = [c, w]
    return e


@implementEffectFactory('Depth of Field (variable filter)', 'Depth-of-field effect that uses a variable-sized filter kernel to produce the blur.  Fast, but with low quality bokeh.')
def depthOfFieldVariableCoC():
    """This method creates and returns a post-process effect that performs
    depth-of-field, using a variable-sized convolution kernel.
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    fpComputeBuffer1 = rt('PostProcessing/fpComputeBuffer1')
    c = buildBackBufferCopyPhase(backBufferCopy)
    t = buildDOFVariableCoCPhase(backBufferCopy.texture, fpComputeBuffer1.texture, None, stochasticSample)
    e = Effect()
    e.name = 'Depth of Field (variable filter)'
    e.phases = [c, t]
    return e


@implementEffectFactory('Depth of Field (bokeh control)', 'Depth-of-field effect that offers complete control over the bokeh shape.  Hi quality, slow and very fill-rate dependent.')
def depthOfFieldBokehControl():
    """Bokeh Control.  This method creates and returns a post-process
    effect that performs depth-of-field using variable-sized point
    sprites to draw artist-supplied bokeh.  It uses the alpha to
    accumulate into a buffer.
    It only draws far away blurs, to minimise the size of the render
    target, which is a major impact on performance for this technique.
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    fpComputeBuffer1 = rt('PostProcessing/fpComputeBuffer1')
    bkComputeBuffer = rt('PostProcessing/bkComputeBuffer')
    c = buildBackBufferCopyPhase(backBufferCopy)
    b = buildDOFBokehControlPhase(backBufferCopy.texture, fpComputeBuffer1.texture, bkComputeBuffer)
    t = buildDOFBokehControlTransferPhase(bkComputeBuffer.texture, fpComputeBuffer1.texture)
    e = Effect()
    e.name = 'Depth of Field (bokeh control)'
    e.phases = [c, b, t]
    m = b.material
    m.bokehTexture = 'system/maps/post_processing/bokeh2.tga'
    return e


@implementEffectFactory('Depth of Field (multi-blur)', 'Depth-of-field effect that blends together 3 previously created blurred images.  Requires the Multi-blur effect.')
def depthOfFieldMultiBlur():
    """This method creates and returns a post-process effect that performs
    depth-of-field, using 3 different sized blur textures, and blends them
    together.
    """
    backBufferCopy = rt('PostProcessing/backBufferCopy')
    fpComputeBuffer1 = rt('PostProcessing/fpComputeBuffer1')
    downSampleBlur1 = rt('PostProcessing/downSampleBlur1')
    downSampleBlur2 = rt('PostProcessing/downSampleBlur2')
    downSampleBlur3 = rt('PostProcessing/downSampleBlur3')
    c = buildBackBufferCopyPhase(backBufferCopy)
    b = buildPhase(backBufferCopy.texture, None, 'shaders/post_processing/depth_of_field3.fx', straightTransfer4Tap, BW_BLEND_SRCALPHA, BW_BLEND_INVSRCALPHA)
    b.name = 'depth of field (multi-blur)'
    m = b.material
    m.depthBlurTexture = fpComputeBuffer1.texture
    m.blurTexture1 = downSampleBlur1.texture
    m.blurTexture2 = downSampleBlur2.texture
    m.blurTexture3 = downSampleBlur3.texture
    e = Effect()
    e.name = 'Depth of Field (multi-blur)'
    e.phases = [c, b]
    return e
