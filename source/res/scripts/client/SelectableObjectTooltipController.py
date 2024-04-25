# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SelectableObjectTooltipController.py
import GUI
import math_utils
from HangarInteractiveObject import HangarInteractiveObject
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class SelectableObjectTooltipController(object):
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

    def showTooltipOnEntity(self, tooltipMgr, tooltipType, entity):
        itemId = entity.selectionId
        if not itemId:
            return
        if isinstance(entity, HangarInteractiveObject) and entity.isShowTooltip:
            tooltipMgr.onCreateWulfTooltip(tooltipType, [itemId], *self.mouseScreenPosition)

    def hideTooltipOnEntity(self, tooltipMgr, tooltipType, entity):
        if tooltipMgr is None:
            return
        else:
            if isinstance(entity, HangarInteractiveObject):
                tooltipMgr.onHideTooltip(tooltipType)
            return

    def _readInterfaceScale(self, scale=None):
        if scale is None:
            scale = self._settingsCore.interfaceScale.get()
        self.__interfaceScale = math_utils.clamp(1.0, 2.0, round(scale, 1))
        return
