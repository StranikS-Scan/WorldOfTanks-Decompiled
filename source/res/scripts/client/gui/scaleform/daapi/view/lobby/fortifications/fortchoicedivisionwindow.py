# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortChoiceDivisionWindow.py
from UnitBase import SORTIE_DIVISION
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.fortifications.components.sorties_dps import makeDivisionData
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.daapi.view.meta.FortChoiceDivisionWindowMeta import FortChoiceDivisionWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as I18N_FORTIFICATIONS
from gui.Scaleform.framework import AppRef
from gui.prb_control.items.unit_items import SupportedRosterSettings
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import FortEvent
from helpers import i18n

class FortChoiceDivisionWindow(AbstractWindowView, View, FortChoiceDivisionWindowMeta, AppRef):

    def __init__(self):
        super(FortChoiceDivisionWindow, self).__init__()

    def _populate(self):
        super(FortChoiceDivisionWindow, self)._populate()
        self.playersRange = []
        for roster in SupportedRosterSettings.list(PREBATTLE_TYPE.SORTIE):
            self.playersRange.append((roster.getMinSlots(), roster.getMaxSlots()))

        self.__makeData()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        self.playersRange = None
        super(FortChoiceDivisionWindow, self)._dispose()
        return

    def selectedDivision(self, divisionID):
        self.app.fireEvent(FortEvent(FortEvent.CHOICE_DIVISION, ctx={'data': divisionID}), EVENT_BUS_SCOPE.LOBBY)

    def __makeData(self):
        data = {}
        data['windowTitle'] = I18N_FORTIFICATIONS.CHOICEDIVISION_WINDOWTITLE
        data['description'] = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(I18N_FORTIFICATIONS.CHOICEDIVISION_DESCRIPTION))
        data['applyBtnLbl'] = I18N_FORTIFICATIONS.CHOICEDIVISION_APPLYBTNLBL
        data['cancelBtnLbl'] = I18N_FORTIFICATIONS.CHOICEDIVISION_CANCELBTNLBL
        list = makeDivisionData(I18N_FORTIFICATIONS.sortie_division_name)
        autoSelectDivision = None
        for item in list:
            if item['level'] == SORTIE_DIVISION.MIDDLE:
                autoSelectDivision = item['level']

        data['autoSelect'] = autoSelectDivision
        divisionSelector = self.__makeDivisionsData(list)
        data['selectorsData'] = divisionSelector
        self.as_setDataS(data)
        return

    def __getPlayerLimits(self, divisionType):
        if divisionType == SORTIE_DIVISION.MIDDLE:
            return self.playersRange[0]
        elif divisionType == SORTIE_DIVISION.CHAMPION:
            return self.playersRange[1]
        elif divisionType == SORTIE_DIVISION.ABSOLUTE:
            return self.playersRange[2]
        else:
            return None

    def __makePlayerCount(self, minPlayerCount, maxPlayerCount):
        separator = '-'
        result = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, str(minPlayerCount) + separator + str(maxPlayerCount))
        return result

    def __makeDivisionsData(self, list):
        result = []
        for item in list:
            divisionType = {}
            title = i18n.makeString(item['label'])
            profit = fort_formatters.getDefRes(item['profit'])
            minLevel = 1
            maxLevel = item['level']
            divisionType['divisionName'] = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(I18N_FORTIFICATIONS.CHOICEDIVISION_DIVISIONFULLNAME, divisionType=title))
            divisionType['divisionProfit'] = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(I18N_FORTIFICATIONS.CHOICEDIVISION_DIVISIONPROFIT, defResCount=profit))
            minLevelStr = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, fort_formatters.getTextLevel(minLevel))
            maxLevelStr = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, fort_formatters.getTextLevel(maxLevel))
            divisionType['vehicleLevel'] = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, i18n.makeString(I18N_FORTIFICATIONS.CHOICEDIVISION_VEHICLELEVEL, minLevel=minLevelStr, maxLevel=maxLevelStr))
            divisionType['divisionID'] = maxLevel
            minCount, maxCount = self.__getPlayerLimits(maxLevel)
            divisionType['playerRange'] = self.__makePlayerCount(minCount, maxCount)
            result.append(divisionType)

        return result
