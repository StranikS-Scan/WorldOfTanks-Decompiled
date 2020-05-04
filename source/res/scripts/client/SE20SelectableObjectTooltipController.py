# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SE20SelectableObjectTooltipController.py
import GUI
import math_utils
from SE20ClientSelectableObject import SE20ClientSelectableObject
from helpers import dependency
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from skeletons.account_helpers.settings_core import ISettingsCore

class SE20SelectableObjectTooltipController(object):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__interfaceScale = 1.0

    @property
    def mouseScreenPosition(self):
        width, height = GUI.screenResolution()[:2]
        cursorPosition = GUI.mcursor().position
        cursorPosition.x = (cursorPosition.x + 1.0) * 0.5 * width
        cursorPosition.y = (cursorPosition.y - 1.0) * -0.5 * height
        if self.__interfaceScale > 1.0:
            cursorPosition.x = round(cursorPosition.x / self.__interfaceScale)
            cursorPosition.y = round(cursorPosition.y / self.__interfaceScale)
        return cursorPosition

    def _onHighlight3DEntity(self, tooltipMgr, entity):
        itemId = entity.selectionId
        if not itemId:
            return
        if isinstance(entity, SE20ClientSelectableObject) and entity.isShowTooltip:
            tooltipMgr.onCreateWulfTooltip(TOOLTIPS_CONSTANTS.SECRET_EVENT_HANGAR_OBJECT, [itemId, True], *self.mouseScreenPosition)

    def _onFade3DEntity(self, tooltipMgr, entity):
        if tooltipMgr is None:
            return
        else:
            if isinstance(entity, SE20ClientSelectableObject):
                tooltipMgr.onHideTooltip(TOOLTIPS_CONSTANTS.SECRET_EVENT_HANGAR_OBJECT)
            return

    def _readInterfaceScale(self, scale=None):
        if scale is None:
            scale = self._settingsCore.interfaceScale.get()
        self.__interfaceScale = math_utils.clamp(1.0, 2.0, round(scale, 1))
        return
