# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/deserter_meta.py
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.shared.events import ShowDialogEvent

class IngameDeserterDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, key, focusedID=None):
        super(IngameDeserterDialogMeta, self).__init__(key, focusedID=focusedID)
        self.__imagePath = '../maps/icons/battle/deserterLeaveBattle.png'
        self.__offsetY = 270

    def getEventType(self):
        return ShowDialogEvent.SHOW_DESERTER_DLG

    def getImagePath(self):
        return self.__imagePath

    def getOffsetY(self):
        return self.__offsetY
