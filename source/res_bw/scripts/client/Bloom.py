# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Bloom.py
"""
This Module implements some utility functions to help manipulate and 
debug the Bloom filter in-game.
There are three methods, please see the help for those methods for more
detailed information:
- selectPreset
- loadStyle
"""
import BigWorld
import ResMgr
import PostProcessing
import Math
from functools import partial
preloadedXML = ResMgr.openSection('scripts/data/bloom.xml', True)

def _getBloomEffect():
    """
    This function finds the bloom effect in the post-processing chain
    """
    chain = PostProcessing.chain()
    for e in chain:
        if e.name in ('Bloom', 'bloom'):
            return e

    return None


def _getBloomEffects():
    """
    This function finds all bloom effects in the post-processing chain
    """
    blooms = []
    chain = PostProcessing.chain()
    for e in chain:
        if e.name in ('Bloom', 'bloom'):
            blooms.append(e)

    return blooms


def removeEffect(effect):
    ch = list(PostProcessing.chain())
    try:
        ch.remove(effect)
        PostProcessing.chain(ch)
    except ValueError:
        pass


def loadStyle(ds, fadeSpeed = 1.0):
    """
    This function loads a bloom style from the given data section.  It smoothly
    changes from the current bloom settings to the new settings over
    "fadeSpeed" seconds.
    """
    newBloom = None
    if ds != None:
        enable = ds.readBool('enable', True)
        filterMode = ds.readInt('filterMode', 1)
        bloomBlur = ds.readBool('bloomAndBlur', True)
        attenuation = ds.readVector4('attenuation', (1, 1, 1, 1))
        attenuation *= attenuation.w
        attenuation.w = 1.0
        numPasses = ds.readInt('numPasses', 2)
        power = ds.readFloat('power', 8)
        width = ds.readFloat('width', 1.0)
        if bloomBlur:
            newBloom = PostProcessing.Effects.Bloom.bloom(filterMode, attenuation, numPasses, width, power)
        else:
            newBloom = PostProcessing.Effects.Bloom.blur(filterMode, attenuation, numPasses, width)
    else:
        print 'Bloom.loadStyle : No DataSection was provided'
        return
    ch = list(PostProcessing.chain())
    oldBloomList = _getBloomEffects()
    for oldBloom in oldBloomList:
        v4mDn = Math.Vector4Morph((1, 1, 1, 1))
        v4mDn.duration = fadeSpeed
        v4mDn.target = (0, 0, 0, 0)
        oldBloom.phases[-1].material.alpha = v4mDn
        oldBloom.bypass = v4mDn
        BigWorld.callback(fadeSpeed, partial(removeEffect, oldBloom))

    ch.append(newBloom)
    v4mUp = Math.Vector4Morph((0, 0, 0, 0))
    v4mUp.duration = fadeSpeed
    v4mUp.target = (1, 1, 1, 1)
    newBloom.phases[-1].material.alpha = v4mUp
    newBloom.bypass = v4mUp
    PostProcessing.chain(ch)
    return


def selectPreset(name, fadeSpeed = 1.0):
    """
    This function loads the named bloom settings from the bloom.xml
    data section that is referenced at the top of this file.  It loads settings
    formerly saved via the saveBloomPreset command.  It smoothly changes from
    the current bloom settings to the new settings over "fadeSpeed" seconds.
    """
    ds = preloadedXML[name]
    loadStyle(ds, fadeSpeed)
