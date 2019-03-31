# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/post_processing/__init__.py
# Compiled at: 2011-06-20 15:40:14
import BigWorld, Math, ResMgr, weakref
import PostProcessing
import Settings
from PostProcessing.Effects import *
from functools import partial
from debug_utils import *

class _Effect:
    __FILE_EXT = '.ppchain'
    name = property(lambda self: self.__name + _Effect.__FILE_EXT)

    def __init__(self, fileName, ctrlName, optional, isAdvanced, isMapDepended, qualityRange):
        self.__name = fileName
        self.__ctrlName = ctrlName
        self.__isAdvanced = isAdvanced
        self.__isMapDepended = isMapDepended
        self.__qualityRange = qualityRange
        self.__optional = optional
        self.__mapName = ''
        self.__chain = None
        self.__ctrl = None
        self.__curQuality = None
        return

    def prerequisites(self):
        if self.__isMapDepended:
            return []
        return PostProcessing.prerequisites(self.__name + _Effect.__FILE_EXT)

    def create(self):
        if self.__isMapDepended:
            return
        self.__create(self.__name + _Effect.__FILE_EXT)

    def destroy(self):
        if self.__ctrl is not None:
            self.__ctrl.destroy()
            self.__ctrl = None
        self.__chain = None
        self.__curQuality = None
        return

    def enable(self, settings):
        if not self.__isSupported(settings):
            return []
        else:
            if self.__isMapDepended:
                try:
                    mapName = BigWorld.player().arena.typeDescriptor.typeName
                except:
                    LOG_CODEPOINT_WARNING()
                    return []

                if self.__mapName != mapName:
                    self.__mapName = mapName
                    self.__create(self.__name + '_' + self.__mapName + _Effect.__FILE_EXT)
            if self.__ctrl is not None:
                self.__ctrl.enable()
            return self.__chain

    def disable(self):
        if self.__ctrl is not None:
            self.__ctrl.disable()
        return

    def changeQuality(self, quality):
        self.__curQuality = quality

    def __isSupported(self, settings):
        isEnabled = True if self.__optional == '' else settings[self.__optional]
        if BigWorld.getGraphicsSetting('MRT_DEPTH') == 0:
            mrtEnabled = not BigWorld.graphicsSettingsNeedRestart()
            return self.__curQuality in self.__qualityRange and isEnabled and self.__isAdvanced and self.__isAdvanced and mrtEnabled
        return True

    def __create(self, fileName):
        self.__chain = PostProcessing.load(fileName)
        if self.__chain is None:
            self.__chain = []
            self.__ctrl = None
            LOG_WARNING('Post effect <%s> was not loaded.' % fileName)
        elif self.__ctrlName is not None:
            self.__ctrl = getattr(post_effect_controllers, self.__ctrlName)()
            self.__ctrl.create()
        return


class WGPostProcessing:
    __CONFIG_FILE_NAME = 'scripts/post_effects.xml'

    def __init__(self):
        self.__curQuality = None
        self.__curEffects = list()
        self.__modes = dict()
        self.__settings = dict()
        self.__curMode = None
        return

    def prerequisites(self):
        ret = []
        return ret

    def init(self):
        self.__loadSettings()
        PostProcessing.g_graphicsSettingListeners.append(_FuncObj(self, 'onSelectQualityOption'))
        PostProcessing.init()
        PostProcessing.chain(None)
        section = ResMgr.openSection(WGPostProcessing.__CONFIG_FILE_NAME)
        self.__load(section)
        for mode in self.__modes.itervalues():
            for effect in mode:
                effect.create()

        return

    def fini(self):
        self.__curEffects = []
        for mode in self.__modes.itervalues():
            for effect in mode:
                effect.destroy()

        PostProcessing.fini()
        self.__saveSettings()

    def enable(self, mode):
        if self.__modes.get(mode, None) is None:
            LOG_WARNING('Effect mode with name %s was not found.' % mode)
            return
        else:
            self.__curMode = mode
            self.__gatherEffects('common')
            self.__gatherEffects(mode)
            chain = []
            for effect in self.__curEffects:
                chain += effect.enable(self.__settings)

            PostProcessing.chain(chain)
            return

    def disable(self):
        self.__curMode = None
        for effect in self.__curEffects:
            effect.disable()

        self.__curEffects = []
        PostProcessing.chain([])
        return

    def refresh(self):
        if self.__curMode is None:
            return
        else:
            curMode = self.__curMode
            self.disable()
            self.enable(curMode)
            return

    def setSetting(self, key, value):
        if self.__settings.get(key, None) is None:
            LOG_WARNING("Setting '%s' was not found." % key)
            return
        else:
            self.__settings[key] = value
            return

    def getSetting(self, key):
        return self.__settings.get(key, False)

    def onSelectQualityOption(self, quality):
        LOG_NOTE('The quality = %s was selected.' % quality)
        self.__curQuality = quality
        BigWorld.callback(0.1, partial(self.__onQualityChanged, self.__curQuality))

    def _printCurrentChain(self):
        chain = []
        for effect in self.__curEffects:
            chain.append(effect.name)

        print 'Current chain: %s' % chain

    def __onQualityChanged(self, quality):
        for mode in self.__modes.itervalues():
            for effect in mode:
                effect.changeQuality(quality)

        self.refresh()

    def __gatherEffects(self, mode):
        for effect in self.__modes[mode]:
            self.__curEffects.append(effect)

    def __load(self, section):
        for s in section.items():
            self.__modes[s[0]] = _loadMode(s[1])

    def __loadSettings(self):
        userPrefs = Settings.g_instance.userPrefs
        usePostMortemEffect = True
        if userPrefs.has_key(Settings.KEY_ENABLE_MORTEM_POST_EFFECT_OLD):
            usePostMortemEffect = userPrefs.readBool(Settings.KEY_ENABLE_MORTEM_POST_EFFECT_OLD, True)
            userPrefs.deleteSection(Settings.KEY_ENABLE_MORTEM_POST_EFFECT_OLD)
            userPrefs.writeBool(Settings.KEY_ENABLE_MORTEM_POST_EFFECT, usePostMortemEffect)
        else:
            usePostMortemEffect = userPrefs.readBool(Settings.KEY_ENABLE_MORTEM_POST_EFFECT, True)
        self.__settings['mortem_post_effect'] = usePostMortemEffect

    def __saveSettings(self):
        userPrefs = Settings.g_instance.userPrefs
        userPrefs.writeBool(Settings.KEY_ENABLE_MORTEM_POST_EFFECT, self.__settings['mortem_post_effect'])


g_postProcessing = WGPostProcessing()

def _fromMaskToQualityRange(mask):
    out = []
    if mask[0] == 1:
        out.append(0)
    if mask[1] == 1:
        out.append(1)
    if mask[2] == 1:
        out.append(2)
    return out


def _loadEffect(section):
    file = section.readString('file', '')
    qualityRange = _fromMaskToQualityRange(section.readVector3('qualityMask', (1, 1, 1)))
    ctrl = section.readString('controller', '')
    isMapDepended = section.has_key('mapDepended')
    isAdvanced = section.has_key('advanced')
    optional = section.readString('optional', '')
    return _Effect(file, None if ctrl == '' else ctrl, optional, isAdvanced, isMapDepended, qualityRange)


def _loadMode(section):
    effects = []
    for s in section.items():
        effects.append(_loadEffect(s[1]))

    return effects


class _FuncObj:

    def __init__(self, obj, funcName):
        self.__weakObj = weakref.ref(obj)
        self.__funcName = funcName

    def __call__(self, args):
        if self.__weakObj() is not None:
            getattr(self.__weakObj(), self.__funcName)(args)
        else:
            LOG_CODEPOINT_WARNING('weak object has been already destroyed.')
        return
