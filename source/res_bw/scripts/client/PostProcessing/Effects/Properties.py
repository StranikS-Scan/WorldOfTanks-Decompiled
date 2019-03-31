# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/Effects/Properties.py
# Compiled at: 2010-08-12 17:04:20
from PostProcessing import chain
import Math

def getEffect(effectName):
    """Helper function - get an effect by name"""
    ch = chain()
    for e in ch:
        if e.name == effectName:
            return e

    raise NameError(effectName)


def linkMaterialAndBypass(effect, material, attributeName):
    """This method takes a material and attribute and
    wraps it in a Vector4Provider.  Then the Vector4Provider
    is set as the bypass of the effect, meaning when the
    material attribute (alpha thereof) goes to zero, the effect
    automatically switches off."""
    val = getattr(material, attributeName)
    try:
        v4Morph = Math.Vector4Morph((val,
         val,
         val,
         val))
    except TypeError:
        val = val.target[3]
        v4Morph = Math.Vector4Morph((val,
         val,
         val,
         val))

    setattr(material, attributeName, v4Morph)
    v4Morph.duration = 0.01
    effect.bypass = v4Morph


class BypassProperty:

    def __init__(self, effectName, primary=False):
        self.effectName = effectName
        if primary:
            from PostProcessing import chainListeners
            chainListeners.append(self.onSetChain)

    def set(self, amt, speed=0.01):
        e = getEffect(self.effectName)
        try:
            e.bypass.target = (amt,
             amt,
             amt,
             amt)
            e.bypass.duration = speed
        except:
            e.bypass = Math.Vector4(amt, amt, amt, amt)

    def get(self):
        e = getEffect(self.effectName)
        return e.bypass.value[3]

    def format(self, val):
        return '%s' % ('Off', 'On')[self.get() > 0.0]

    def onSetChain(self):
        try:
            e = getEffect(self.effectName)
        except NameError:
            return

        if e.bypass != None:
            try:
                val = e.bypass.value[3]
                e.bypass = Math.Vector4Morph((val,
                 val,
                 val,
                 val))
            except TypeError:
                val = e.bypass.target[3]
                e.bypass = Math.Vector4Morph((val,
                 val,
                 val,
                 val))

        return


class MaterialProperty:

    def __init__(self, effectName, phaseIdx, materialAttribute, primary=False):
        self.effectName = effectName
        self.phaseIdx = phaseIdx
        self.materialAttribute = materialAttribute
        if primary:
            from PostProcessing import chainListeners
            chainListeners.append(self.onSetChain)

    def getMaterial(self):
        e = getEffect(self.effectName)
        p = e.phases[self.phaseIdx]
        return p.material

    def onSetChain(self):
        try:
            e = getEffect(self.effectName)
        except NameError:
            return

        p = e.phases[self.phaseIdx]


class MaterialFloatProperty(MaterialProperty):

    def __init__(self, effectName, phaseIdx, materialAttribute, precis=2, primary=False):
        MaterialProperty.__init__(self, effectName, phaseIdx, materialAttribute, primary)
        self.fmtString = '%%0.%df' % (precis,)

    def set(self, amt, speed=0.01, makeVec4Prov=False):
        material = self.getMaterial()
        try:
            v4p = getattr(material, self.materialAttribute)
            v4p.target = (amt,
             amt,
             amt,
             amt)
            v4p.duration = speed
        except:
            if makeVec4Prov is False:
                setattr(material, self.materialAttribute, amt)
            else:
                attrib = getattr(material, self.materialAttribute)
                v4Morph = Math.Vector4Morph((attrib,
                 attrib,
                 attrib,
                 attrib))
                setattr(material, self.materialAttribute, v4Morph)

    def get(self):
        material = self.getMaterial()
        try:
            v4p = getattr(material, self.materialAttribute)
            return v4p.target[3]
        except:
            return getattr(material, self.materialAttribute)

    def format(self, val):
        return self.fmtString % (self.get(),)


class MaterialTextureProperty(MaterialProperty):

    def __init__(self, effectName, phaseIdx, materialAttribute, textureList):
        MaterialProperty.__init__(self, effectName, phaseIdx, materialAttribute)
        self.textureList = textureList
        self.idx = 0

    def idxFromVal(self, val):
        import math
        i = int(round(val * len(self.textureList)))
        i %= len(self.textureList)
        return i

    def set(self, amt, speed=0.01):
        self.idx = amt
        material = self.getMaterial()
        idx = self.idxFromVal(amt)
        filename = self.textureList[idx]
        setattr(material, self.materialAttribute, filename)

    def get(self):
        return self.idx

    def format(self, val):
        idx = self.idxFromVal(val)
        filename = self.textureList[idx]
        filename = filename[filename.rindex('/') + 1:]
        return filename
