# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/pve_common.py
from enum import IntEnum
import typing
from constants import IS_VS_EDITOR
from pve_battle_hud import getPveHudLogger
from visual_script import ASPECT
from visual_script.block import Block
from visual_script.misc import EDITOR_TYPE, errorVScript
from visual_script.pve_battle_hud_blocks import PVEBattleHUDMeta
from visual_script.slot_types import SLOT_TYPE
if not IS_VS_EDITOR:
    from skeletons.gui.battle_session import IBattleSessionProvider
    from helpers import dependency
_logger = getPveHudLogger()

class SettingType(IntEnum):
    GENERAL = 0
    ITEM = 1


class PropertySlotSpec(object):
    __slots__ = ('slotName', 'slotType', 'defaultValue', 'editorData', 'required')

    def __init__(self, slotName, slotType, defaultValue=None, editorData=None, required=False):
        self.slotName = slotName
        self.slotType = slotType
        self.defaultValue = defaultValue
        self.editorData = editorData
        self.required = required


class ClientBattleHUDWidgetSettings(Block, PVEBattleHUDMeta):
    _SETTINGS_MODEL = None
    _WIDGET_TYPE = None
    _SETTINGS_CONFIG = list()
    _SETTING_TYPE = None
    _ID_SLOT = PropertySlotSpec('id', SLOT_TYPE.STR, required=True)

    def __init__(self, *args, **kwargs):
        super(ClientBattleHUDWidgetSettings, self).__init__(*args, **kwargs)
        if self._SETTINGS_MODEL is None:
            errorVScript(self, 'Missing widget settings model for "{}" block.'.format(self.__name__))
        if self._WIDGET_TYPE is None:
            errorVScript(self, 'Missing widget type for "{}" block.'.format(self.__name__))
        if self._SETTING_TYPE is None:
            errorVScript(self, 'Missing setting type for "{}" block.'.format(self.__name__))
        self._inSlot = self._makeEventInputSlot('in', self._execute)
        self._outSlot = self._makeEventOutputSlot('out')
        self._slotSpecs = self._SETTINGS_CONFIG[:]
        if self._SETTING_TYPE == SettingType.ITEM:
            self._slotSpecs.insert(0, self._ID_SLOT)
        self._settingsSlots = [ self.__makeSettingsSlot(slotSpec) for slotSpec in self._slotSpecs ]
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def validate(self):
        for idx, slotSpec in enumerate(self._slotSpecs):
            slot = self._settingsSlots[idx]
            if slotSpec.required and not slot.hasValue():
                return '{slotName} value is required'.format(slotName=slotSpec.slotName)

    def _execute(self):
        settings = {slotSpec.slotName:self.__getSettingValue(self._settingsSlots[idx], slotSpec.slotType) for idx, slotSpec in enumerate(self._slotSpecs)}
        sessionProvider = dependency.instance(IBattleSessionProvider)
        settingsCtrl = sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl is not None:
            settingsModel = self._SETTINGS_MODEL(**settings)
            if self._SETTING_TYPE == SettingType.ITEM:
                itemID = settings[self._ID_SLOT.slotName]
                settingsCtrl.setItemSettings(self._WIDGET_TYPE, itemID, settingsModel)
            elif self._SETTING_TYPE == SettingType.GENERAL:
                settingsCtrl.setSettings(self._WIDGET_TYPE, settingsModel)
        self._outSlot.call()
        return

    def __makeSettingsSlot(self, slotSpec):
        editorType = EDITOR_TYPE.ENUM_SELECTOR if slotSpec.editorData is not None else -1
        slot = self._makeDataInputSlot(slotSpec.slotName, slotSpec.slotType, editorType=editorType)
        if slotSpec.defaultValue is not None:
            slot.setDefaultValue(slotSpec.defaultValue)
        if slotSpec.editorData is not None:
            slot.setEditorData(slotSpec.editorData)
        return slot

    @staticmethod
    def __getSettingValue(slot, slotType):
        if not slot.hasValue():
            if slotType == SLOT_TYPE.BOOL:
                resultValue = False
            elif 'Array' in slotType:
                resultValue = []
            else:
                resultValue = ''
        else:
            value = slot.getValue()
            if slotType == SLOT_TYPE.SOUND:
                resultValue = value.name
            else:
                resultValue = value
        return resultValue
