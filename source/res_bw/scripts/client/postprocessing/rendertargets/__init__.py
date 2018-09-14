# Embedded file name: scripts/client/PostProcessing/RenderTargets/__init__.py
"""RenderTargets python module
This module manages the render targets used by the post-processing chain.
"""
import BigWorld
import traceback
__all__ = ['calcMemoryUsage',
 'reportMemoryUsage',
 'clearRenderTargets',
 'getRenderTargets',
 'createStubs',
 'rt']
rts = {}
rtData = {'PostProcessing/backBufferCopy': (0, 0),
 'PostProcessing/backBufferCopyB': (0, 0, True),
 'PostProcessing/skyBoxCopy': (0, 0, True),
 'PostProcessing/downSample1': (-1, -1),
 'PostProcessing/downSample1B': (-1, -1),
 'PostProcessing/downSample1HDR': (-1,
                                   -1,
                                   False,
                                   'A16B16G16R16F'),
 'PostProcessing/downSample1BHDR': (-1,
                                    -1,
                                    False,
                                    'A16B16G16R16F'),
 'PostProcessing/downSample1CHDR': (-1,
                                    -1,
                                    False,
                                    'A16B16G16R16F'),
 'PostProcessing/downSample1DHDR': (-1,
                                    -1,
                                    False,
                                    'A16B16G16R16F'),
 'PostProcessing/downSample1EHDR': (-1,
                                    -1,
                                    False,
                                    'A16B16G16R16F'),
 'PostProcessing/downSampleBlur1': (-1, -1),
 'PostProcessing/bkDownSample1': (-1, -1),
 'PostProcessing/bkDownSampleN1': (-1, -1),
 'PostProcessing/bkBlur1': (-1,
                            -1,
                            False,
                            'A16B16G16R16F'),
 'PostProcessing/bkBlurN1': (-1,
                             -1,
                             False,
                             'A16B16G16R16F'),
 'PostProcessing/downSample2': (-2, -2),
 'PostProcessing/downSample2B': (-2, -2),
 'PostProcessing/downSampleBlur2': (-2, -2),
 'PostProcessing/bkDownSample2': (-2, -2),
 'PostProcessing/bkDownSampleN2': (-2, -2),
 'PostProcessing/bkBlur2': (-2,
                            -2,
                            False,
                            'A16B16G16R16F'),
 'PostProcessing/bkBlurN2': (-2,
                             -2,
                             False,
                             'A16B16G16R16F'),
 'PostProcessing/downSample3': (-3, -3),
 'PostProcessing/downSample3B': (-3, -3),
 'PostProcessing/downSampleBlur3': (-3, -3),
 'PostProcessing/bkDownSample3': (-3, -3),
 'PostProcessing/bkDownSampleN3': (-3, -3),
 'PostProcessing/bkBlur3': (-3,
                            -3,
                            False,
                            'A16B16G16R16F'),
 'PostProcessing/bkBlurN3': (-3,
                             -3,
                             False,
                             'A16B16G16R16F'),
 'PostProcessing/computeBuffer1': (-3, -3),
 'PostProcessing/computeBuffer2': (-3, -3),
 'PostProcessing/fpComputeBuffer1': (0,
                                     0,
                                     False,
                                     'G16R16F'),
 'PostProcessing/fpComputeBufferHalf': (-1,
                                        -1,
                                        True,
                                        'G16R16F'),
 'PostProcessing/fpComputeBuffer2': (0,
                                     0,
                                     False,
                                     'G16R16F'),
 'PostProcessing/bkComputeBuffer': (0,
                                    0,
                                    False,
                                    'A32B32G32R32F')}

def _create(name, width, height, reuseZ = False, format = 'A8R8G8B8'):
    global rts
    rt = BigWorld.RenderTarget(name, int(width), int(height), reuseZ, format)
    rts[name] = rt
    return rt


def calcMemoryUsage(silent):
    total = 0.0
    for name, rt in rts.items():
        total += float(rt.textureMemoryUsed)
        if rt.textureMemoryUsed > 0 and not silent:
            print 'PostProcessing: %s (%d x %d)' % (rt.name, rt.width, rt.height)

    total /= 1048576.0
    if not silent:
        pass
    return total


def reportMemoryUsage():
    calcMemoryUsage(False)


def rt(rtName):
    """Return a render target by name, or raise a KeyError exception"""
    if not rts.has_key(rtName):
        rts[rtName] = _create(rtName, *rtData[rtName])
    return rts[rtName]


def getRenderTargets():
    return rts.values()


def clearRenderTargets():
    for name, rt in rts.items():
        rt.release()


def createStubs():
    for name, data in rtData.items():
        _create(name, *data)


def fini():
    clearRenderTargets()
    rts = {}
