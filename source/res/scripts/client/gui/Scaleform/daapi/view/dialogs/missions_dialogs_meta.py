# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/missions_dialogs_meta.py
from gui.Scaleform.daapi.view.dialogs import IDialogMeta
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import events
from helpers.i18n import makeString as _ms
from shared_utils import first

class UseAwardSheetDialogMeta(IDialogMeta):

    def __init__(self, quest, freeSheets):
        self.__quest = quest
        self.__freeSheets = freeSheets
        self.__title = PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_TITLE
        self.__submitLabel = PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_SUBMITBTN
        self.__cancelLabel = PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_CANCELBTN

    def getQuest(self):
        return self.__quest

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_USE_AWARD_SHEET_DIALOG

    def getTitle(self):
        return _ms(self.__title)

    def getSubmitButtonLabel(self):
        return _ms(self.__submitLabel)

    def getCancelButtonLabel(self):
        return _ms(self.__cancelLabel)

    def getViewScopeType(self):
        return ScopeTemplates.DEFAULT_SCOPE

    def getDescrText(self):
        return _ms(PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_DESCR)

    def getFooterText(self):
        return _ms(PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_SHEETSTOTAL, count=str(self.__freeSheets))

    def getCounterText(self):
        return _ms(PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_NEEDAMOUNT, count=str(self.__quest.getPawnCost()))

    def getIcon(self):
        return RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_FREE_SHEET_MID

    def isAvailable(self):
        return self.__quest.isUnlocked() and self.__quest.hasRequiredVehicles()

    def getInfoText(self):
        return _ms(PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_INFO)

    def getWarningText(self):
        if not self.__quest.hasRequiredVehicles():
            vehClass = first(self.__quest.getVehicleClasses())
            return _ms(PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_NOVEHICLE, vehicleClass=_ms('#menu:classes/short/' + vehClass))
        return _ms(PERSONAL_MISSIONS.USEAWARDSHEETWINDOW_LOCKED) if not self.__quest.isUnlocked() else ''
