# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_button_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_sub_button_model import CustomizationSubButtonModel

class ButtonActionType(Enum):
    CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_PARTS = 'apply_all_parts'
    CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS = 'apply_all_seasons'
    CUSTOMIZATION_SHEET_ACTION_APPLY_TO_ALL_SEASONS_ALERT = 'apply_all_seasons_alert'
    CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_SEASONS = 'remove_all_seasons'
    CUSTOMIZATION_SHEET_ACTION_REMOVE_ONE = 'remove_one'
    CUSTOMIZATION_SHEET_ACTION_COLOR_CHANGE = 'color_change'
    CUSTOMIZATION_SHEET_ACTION_SCALE_CHANGE = 'scale_change'
    CUSTOMIZATION_SHEET_RENT_PROLONG = 'rent_prolong'
    CUSTOMIZATION_SHEET_RENT_NOT_PROLONG = 'rent_not_prolong'
    CUSTOMIZATION_SHEET_ACTION_REMOVE_FROM_ALL_PARTS = 'remove_from_all_parts'
    CUSTOMIZATION_SHEET_ACTION_CLOSE = 'action_close'
    CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR_RIGHT = 'horizontal_mirror_right'
    CUSTOMIZATION_SHEET_ACTION_HORIZONZONTAL_MIRROR_LEFT = 'horizontal_mirror_left'
    CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR_UP = 'vertical_mirror_up'
    CUSTOMIZATION_SHEET_ACTION_VERTICAL_MIRROR_DOWN = 'vertical_mirror_down'
    CUSTOMIZATION_SHEET_ACTION_MIRROR_LEFT_UP = 'mirror_left_up'
    CUSTOMIZATION_SHEET_ACTION_MIRROR_RIGHT_UP = 'mirror_right_up'
    CUSTOMIZATION_SHEET_ACTION_MIRROR_LEFT_DOWN = 'mirror_left_down'
    CUSTOMIZATION_SHEET_ACTION_MIRROR_RIGHT_DOWN = 'mirror_right_down'
    CUSTOMIZATION_SHEET_ACTION_MOVE = 'move'
    CUSTOMIZATION_SHEET_ACTION_EDIT = 'edit'
    CUSTOMIZATION_SHEET_ACTION_INFO = 'info'
    CUSTOMIZATION_SHEET_ACTION_GET_BACK = 'get_back'
    CUSTOMIZATION_SHEET_ACTION_SWITCH_PROGRESSION_LVL = 'switch_progression_lvl'
    CUSTOMIZATION_SHEET_ACTION_EDIT_STYLE = 'edit_style'


class CustomizationButtonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CustomizationButtonModel, self).__init__(properties=properties, commands=commands)

    def getActionBtnLabel(self):
        return self._getString(0)

    def setActionBtnLabel(self, value):
        self._setString(0, value)

    def getDisableTooltip(self):
        return self._getString(1)

    def setDisableTooltip(self, value):
        self._setString(1, value)

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def getActionType(self):
        return ButtonActionType(self._getString(3))

    def setActionType(self, value):
        self._setString(3, value.value)

    def getProgressionLevel(self):
        return self._getNumber(4)

    def setProgressionLevel(self, value):
        self._setNumber(4, value)

    def getSubButtons(self):
        return self._getArray(5)

    def setSubButtons(self, value):
        self._setArray(5, value)

    @staticmethod
    def getSubButtonsType():
        return CustomizationSubButtonModel

    def _initialize(self):
        super(CustomizationButtonModel, self)._initialize()
        self._addStringProperty('actionBtnLabel', '')
        self._addStringProperty('disableTooltip', '')
        self._addBoolProperty('isEnabled', False)
        self._addStringProperty('actionType')
        self._addNumberProperty('progressionLevel', 1)
        self._addArrayProperty('subButtons', Array())
