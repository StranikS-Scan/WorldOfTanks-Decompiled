# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/deserter_meta.py
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.shared.events import ShowDialogEvent
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class IngameDeserterDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, key, additionalInfo='', focusedID=None, imagePath=RES_ICONS.MAPS_ICONS_BATTLE_DESERTERLEAVEBATTLE):
        super(IngameDeserterDialogMeta, self).__init__(key, messageCtx={'additionalInfo': additionalInfo}, focusedID=focusedID)
        self.__imagePath = imagePath
        self.__offsetY = 270

    def getEventType(self):
        return ShowDialogEvent.SHOW_DESERTER_DLG

    def getImagePath(self):
        return self.__imagePath

    def getOffsetY(self):
        return self.__offsetY
