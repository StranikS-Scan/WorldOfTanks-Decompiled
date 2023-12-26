# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/game_settings_blocks.py
from constants import IS_VS_EDITOR
from visual_script import ASPECT
from visual_script.block import Block, Meta, InitParam, buildStrKeysValue
from visual_script.misc import errorVScript, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.tunable_event_block import TunableEventBlock
if not IS_VS_EDITOR:
    import Windowing
    from gui import InputHandler
    from helpers import dependency
    from skeletons.account_helpers.settings_core import ISettingsCore
    from skeletons.gui.app_loader import IAppLoader

class GameSettingsMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class GetGameSetting(Block, GameSettingsMeta):
    settingsCore = dependency.descriptor(ISettingsCore) if not IS_VS_EDITOR else None
    _settingTypes = {'bool': SLOT_TYPE.BOOL,
     'int': SLOT_TYPE.INT,
     'str': SLOT_TYPE.STR}

    def __init__(self, *args, **kwargs):
        super(GetGameSetting, self).__init__(*args, **kwargs)
        self._name = self._makeDataInputSlot('settingName', SLOT_TYPE.STR)
        settingType = self._getInitParams()
        self._value = self._makeDataOutputSlot('value', self._settingTypes[settingType], self._getValue)

    @classmethod
    def initParams(cls):
        return [InitParam('Game Setting Type', SLOT_TYPE.STR, buildStrKeysValue(*cls._settingTypes.keys()), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def _getValue(self):
        value = self.settingsCore.getSetting(self._name.getValue())
        settingType = self._getInitParams()
        if value.__class__.__name__ == settingType:
            self._value.setValue(value)
        else:
            errorVScript(self, 'Incorrect type of the game setting value, {} expected '.format(value.__class__.__name__))


class OnGameSettingsChanged(TunableEventBlock, GameSettingsMeta):
    _EVENT_SLOT_NAMES = ['onChanged']
    settingsCore = dependency.descriptor(ISettingsCore) if not IS_VS_EDITOR else None

    def __init__(self, *args, **kwargs):
        super(OnGameSettingsChanged, self).__init__(*args, **kwargs)
        self._settings = self._makeDataOutputSlot('settings', arrayOf(SLOT_TYPE.STR), None)
        self._lastSettings = {}
        return

    def onStartScript(self):
        self.settingsCore.onSettingsChanged += self._onSettingsChanged

    def onFinishScript(self):
        self.settingsCore.onSettingsChanged -= self._onSettingsChanged

    def _onSettingsChanged(self, diff):
        res = [ name for name, value in diff.iteritems() if name not in self._lastSettings or value != self._lastSettings[name] ]
        self._lastSettings.update(diff)
        if res:
            self._callOutput(res)

    @TunableEventBlock.eventProcessor
    def _callOutput(self, res):
        self._settings.setValue(res)


class OnWindowAccessibilityChanged(Block, GameSettingsMeta):

    def __init__(self, *args, **kwargs):
        super(OnWindowAccessibilityChanged, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._isAccessible = self._makeDataOutputSlot('isAccessible', SLOT_TYPE.BOOL, None)
        return

    def onStartScript(self):
        Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)

    def onFinishScript(self):
        Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)

    def _onWindowAccessibilityChanged(self, isWindowAccessible):
        self._isAccessible.setValue(isWindowAccessible)
        self._out.call()


class HandleKeyEvent(Block, GameSettingsMeta):

    def __init__(self, *args, **kwargs):
        super(HandleKeyEvent, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('out')
        self._key = self._makeDataOutputSlot('key', SLOT_TYPE.INT, None)
        return

    def onStartScript(self):
        InputHandler.g_instance.onKeyDown += self._handleKeyEvent

    def onFinishScript(self):
        InputHandler.g_instance.onKeyDown -= self._handleKeyEvent

    def _handleKeyEvent(self, event):
        if event.isKeyDown():
            self._key.setValue(event.key)
            self._out.call()


class ShowSimpleTooltip(Block, GameSettingsMeta):
    __appLoader = dependency.descriptor(IAppLoader) if not IS_VS_EDITOR else None

    def __init__(self, *args, **kwargs):
        super(ShowSimpleTooltip, self).__init__(*args, **kwargs)
        self._show = self._makeEventInputSlot('show', self._onShowSimpleTooltip)
        self._hide = self._makeEventInputSlot('hide', self._onHideSimpleTooltip)
        self._tooltipHeader = self._makeDataInputSlot('header', SLOT_TYPE.STR)
        self._tooltipBody = self._makeDataInputSlot('body', SLOT_TYPE.STR)

    def _onShowSimpleTooltip(self):
        from gui.shared.utils.functions import makeTooltip
        self.__appLoader.getApp().getToolTipMgr().onCreateComplexTooltip(makeTooltip(header=self._tooltipHeader.getValue(), body=self._tooltipBody.getValue()), 'INFO')

    def _onHideSimpleTooltip(self):
        self.__appLoader.getApp().getToolTipMgr().as_hideS()
