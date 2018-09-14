# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PostProcessing/__init__.py
"""The PostProcessing Module.  This imports all of the c++ _PostProcessing module
into the PostProcessing namespace.  It allows code to be written in script to
directly override c++ behaviour."""
from _PostProcessing import *
from _PostProcessing import debug as _debug
from _PostProcessing import chain as _chain
from _PostProcessing import save as _save
from _PostProcessing import load as _load
import RenderTargets
import Phases
import BigWorld
import ChainView
import ResMgr
import exceptions
from Phases import getPhaseNames
import Listener
preChainListeners = []
chainListeners = []
g_graphicsSettingListeners = []

def _dataSectionFromFilename(filename, createIfMissing=False):
    """
    This method returns a data section, given a data section
    or a filename
    """
    ds = None
    if isinstance(filename, ResMgr.DataSection):
        ds = filename
    else:
        ds = ResMgr.openSection(filename, createIfMissing)
        if ds == None:
            basePath = 'system/post_processing/chains/'
            ds = ResMgr.openSection(basePath + filename, createIfMissing)
    return ds


def _materialPrerequisites(materialSect):
    ret = []
    ret.append(materialSect.readString('fx'))
    for name, sect in materialSect.items():
        if name == 'property' and sect.has_key('Texture'):
            ret.append(sect.readString('Texture'))

    return ret


def prerequisites(filename):
    """
    This method returns a list of resources required for background loading.
    It assumes the data section has been preloaded, since this function needs
    to parse the xml file and must return synchronously.
    
    There are not many resources held by PP effects, mainly their materials.
    The only exceptions are VisualTransferMeshes.
    """
    ds = _dataSectionFromFilename(filename)
    ret = []
    if ds:
        for name, effectSect in ds.items():
            for name, phaseSect in effectSect.items():
                if phaseSect.has_key('material'):
                    ret += _materialPrerequisites(phaseSect['material'])
                if phaseSect.has_key('filterQuad'):
                    if phaseSect['filterQuad'].has_key('PyVisualTransferMesh'):
                        ret.append(phaseSect['filterQuad']['PyVisualTransferMesh'].readString('resourceID'))

    return ret


def chain(*kargs):
    """
    This method overloads the chain method in C++, and extends it
    to provide listener support
    """
    global chainListeners
    global preChainListeners
    if len(kargs) == 0:
        return _chain()
    for preListener in preChainListeners:
        if not preListener(*kargs):
            return

    _chain(*kargs)
    for listener in chainListeners:
        listener()


def save(dataSection):
    """
    This method overloads the underlying C++ function, and allows us to
    check if the dataSection is actually a filename instead.  Also added
    is the default folder name from WorldEditor
    """
    dataSection = _dataSectionFromFilename(dataSection, True)
    return _save(dataSection)


def load(dataSection):
    """
    This method overloads the underlying C++ function, and allows us to
    check if the dataSection is actually a filename instead.  Also added
    is the default folder name from WorldEditor
    """
    dataSection = _dataSectionFromFilename(dataSection)
    return _load(dataSection)


def merge(dataSection, addEffectIfMissing=False):
    """
    This method loads a chain from XML and merges it with the
    existing chain.  Effects with the same name as any of those
    loaded via XML will be replaced.
    """
    dataSection = _dataSectionFromFilename(dataSection)
    from Effects import Properties
    ds = ResMgr.openSection(dataSection)
    oldEffects = chain()
    newEffects = load(ds)
    ch = []
    for old in oldEffects:
        found = False
        for nw in newEffects:
            if old.name == nw.name:
                ch.append(nw)
                found = True
                break

        if not found:
            ch.append(old)

    if addEffectIfMissing == True:
        for nw in newEffects:
            found = False
            for old in ch:
                if old.name == nw.name:
                    found = True
                    break

            if not found:
                pass

    chain(*ch)


def isSupported(dataSection):
    """
    This method checks an dataSection to see if all the Effects contained
    therein are supported by the current graphics setting.
    
    Currently the only issue is that cases are depth-based effects are not
    available if the MRTDepth setting is not turned on.
    """
    optionIdx = BigWorld.getGraphicsSetting('MRT_DEPTH')
    if optionIdx == 0:
        return True
    else:
        ds = ResMgr.openSection(dataSection)
        if ds is None:
            raise exceptions.AttributeError(dataSection)
        effects = ds.readStrings('Effect')
        for name in effects:
            if name in ('Depth of Field (variable filter)', 'Depth of Field (bokeh control)', 'Depth of Field (multi-blur)', 'Rainbow', 'God Rays', 'Volume Light'):
                return False

        return True


def appendChain(effect):
    """
    This method appends an effect to the end of the post-processing chain
    """
    c = list(chain())
    c.append(effect)
    chain(*c)


def insertEffectAfter(previous, effect):
    """
    This method inserts an effect into the post-processing chain,
    after the effect specified by name.
    """
    c = list(chain())
    for i in xrange(0, len(c)):
        if c[i].name == previous:
            c.insert(i, effect)
            chain(*c)
            return True

    return False


def getEffect(name):
    """
    This function finds the appropriate effect in the post-processing chain
    """
    ch = chain()
    for e in ch:
        if e.name == name:
            return e

    raise exceptions.NameError(name)
    return None


def debug():
    """
    This method hides the debug method in C++, and extends it
    by automatically creating a render target for the debug object
    , and showing a GUI     component representing this texture
    """
    import GUI
    s = GUI.Simple('')
    GUI.addRoot(s)
    db = Debug()
    db.renderTarget = BigWorld.RenderTarget('debug post-processing', 1024, 1024)
    _debug(db)
    s.texture = db.renderTarget.texture
    s.materialFX = 'SOLID'
    return s


def debugGui():
    if _debug() == None:
        db = Debug()
        db.renderTarget = BigWorld.RenderTarget('debug post-processing', 1024, 1024)
        _debug(db)
        print 'created debug rT'
    import GUI
    w = GUI.Window('')
    GUI.addRoot(w)
    w.script = ChainView.ChainView(w)
    w.script.createChildren()
    w.size = (0.75, 3.0)
    return w


def defaultChain(optionIdx=-1):
    """
    Create the default BigWorld PostProcessing chain, for the given
    graphics setting level.  If no graphics setting level is passed in,
    the current Post Processing graphics setting is read from the
    graphics setting registry and used.
    """
    if optionIdx == -1:
        optionIdx = BigWorld.getGraphicsSetting('POST_PROCESSING_QUALITY')
    RenderTargets.clearRenderTargets()
    if optionIdx == 0:
        chain(load('High_Graphics_Setting.ppchain'))
    elif optionIdx == 1:
        chain(load('Medium_Graphics_Setting.ppchain'))
    elif optionIdx == 2:
        chain(load('Low_Graphics_Setting.ppchain'))
    elif optionIdx == 3:
        chain(None)
    return


def _onSelectQualityOption(key, optionIdx):
    """
    Callback from the graphics settings system when the user changes the desired
    post-processing quality.
    """
    global g_graphicsSettingListeners
    for l in g_graphicsSettingListeners:
        l(key, optionIdx)

    BigWorld.callback(0.1, RenderTargets.reportMemoryUsage)


_graphicsSetting = None

def _registerGraphicsSettings():
    """
    Create and register graphics settings for Post Processing
    """
    global _graphicsSetting
    gs = BigWorld.GraphicsSetting('POST_PROCESSING_QUALITY', 'Post Processing Quality', -1, False, False, partial(_onSelectQualityOption, 'POST_PROCESSING'))
    gs.addOption('MAX', 'Max', True, True)
    gs.addOption('HIGH', 'High', True, True)
    gs.addOption('MEDIUM', 'Medium', True, True)
    gs.addOption('LOW', 'Low', True, True)
    gs.addOption('OFF', 'Off', True, False)
    gs.registerSetting()
    _graphicsSetting = gs


def _deregisterGraphicsSettings():
    """
    Create and register graphics settings for Post Processing
    """
    global _graphicsSetting
    if _graphicsSetting is not None:
        _graphicsSetting.callback = None
        _graphicsSetting = None
    return


_graphicsSettingMotionBlur = None

def _registerMotionBlurGraphicsSettings():
    """
    Create and register graphics settings for Post Processing
    """
    global _graphicsSettingMotionBlur
    gs = BigWorld.GraphicsSetting('MOTION_BLUR_QUALITY', 'Motion Blur Quality', -1, False, False, partial(_onSelectQualityOption, 'MOTION_BLUR'))
    gs.addOption('HIGH', 'High', True, True)
    gs.addOption('MEDIUM', 'Medium', True, True)
    gs.addOption('LOW', 'Low', True, True)
    gs.addOption('OFF', 'Off', True, False)
    gs.registerSetting()
    _graphicsSettingMotionBlur = gs


def _deregisterMotionBlurGraphicsSettings():
    """
    Create and register graphics settings for Post Processing
    """
    global _graphicsSettingMotionBlur
    if _graphicsSettingMotionBlur is not None:
        _graphicsSettingMotionBlur.callback = None
        _graphicsSettingMotionBlur = None
    return


def init():
    RenderTargets.createStubs()
    _registerGraphicsSettings()
    _registerMotionBlurGraphicsSettings()


def fini():
    global g_motionBlurGraphicsSettingListeners
    global g_graphicsSettingListeners
    chain(None)
    _deregisterGraphicsSettings()
    _deregisterMotionBlurGraphicsSettings()
    RenderTargets.fini()
    Phases.finiPhases()
    g_graphicsSettingListeners = []
    g_motionBlurGraphicsSettingListeners = []
    return


def gatherPhases(effect, name):
    """This function returns a list of phases
    matching the search string.  Wildcard *
    can be used"""
    if name == '*':
        return effect.phases
    else:
        phases = []
        for phase in effect.phases:
            if name == phase.name:
                phases.append(phase)

        return phases


def gatherEffects(chain, name):
    """This function returns a list of effects
    matching the search string.  Wildcard *
    can be used"""
    if name == '*':
        return chain
    else:
        effects = []
        for effect in chain:
            if name == effect.name:
                effects.append(effect)

        return effects


def setMaterialProperty(chain, name, value):
    """
    This function sets a material property on a chain.
    
    The name of the variable can be specified in 1 up to
    3 parts, separated with a forward slash :
    
    material variable name
    phase name/material variable name
    effect name/phase name/material variable name
    
    Additionally, you can use a wild card on the effect or
    phase name :
    
    effect name/*/variable name
    
    If there is more than one phase that has the name that
    matches, the property will be set on multiple materials.
    """
    if chain == None:
        return
    elif len(chain) == 0:
        return
    else:
        searchFields = name.split('/')
        if len(searchFields) == 3:
            effects = gatherEffects(chain, searchFields[0])
            searchFields = searchFields[1:]
        else:
            effects = gatherEffects(chain, '*')
        phases = []
        if len(searchFields) == 2:
            for effect in effects:
                phases += gatherPhases(effect, searchFields[0])

            searchFields = searchFields[1:]
        else:
            for effect in effects:
                phases += gatherPhases(effect, '*')

        if len(searchFields) == 1:
            for phase in phases:
                try:
                    setattr(phase.material, searchFields[0], value)
                except AttributeError:
                    pass

        return


from FilterKernels import *
from Effects import *
