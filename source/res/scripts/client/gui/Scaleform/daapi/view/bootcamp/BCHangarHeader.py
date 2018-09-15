# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHangarHeader.py
from bootcamp.BootcampConstants import getBootcampInternalHideElementName
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared import events, EVENT_BUS_SCOPE
from bootcamp.BootcampGarage import g_bootcampGarage
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.MENU import MENU
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

class BCHangarHeader(HangarHeader):
    bootcampCtrl = dependency.descriptor(IBootcampController)

    def __init__(self, _=None):
        super(BCHangarHeader, self).__init__()
        self.__componentKey = 'HangarQuestControl'

    def updateVisibleComponents(self, _):
        self.update()

    def showQuestsWindow(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_QUESTS_VIEW), scope=EVENT_BUS_SCOPE.LOBBY)
        if g_bootcampGarage.getPrevHint() == 'highlightButton_Quests_LessonV':
            g_bootcampGarage.hidePrevShowNextHint()

    def showPersonalQuests(self):
        self.showQuestsWindow()

    def showCommonQuests(self):
        self.showQuestsWindow()

    def getFakeQuestData(self):
        return {'commonQuestsLabel': '',
         'commonQuestsIcon': RES_ICONS.questsStateIconOutline('available'),
         'commonQuestsTooltip': '',
         'commonQuestsEnable': True}

    def update(self, *args):
        self._personalQuestID = None
        key = getBootcampInternalHideElementName(self.__componentKey)
        visibleSettings = self.bootcampCtrl.getLobbySettings()
        headerVisible = key in visibleSettings and not visibleSettings[key]
        if headerVisible and self._currentVehicle.isPresent():
            vehicle = self._currentVehicle.item
            headerVO = {'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
             'tankInfo': text_styles.concatStylesToMultiLine(text_styles.promoSubTitle(vehicle.shortUserName), text_styles.stats(MENU.levels_roman(vehicle.level))),
             'isPremIGR': vehicle.isPremiumIGR,
             'isVisible': headerVisible}
            headerVO.update(self.getFakeQuestData())
            headerVO.update(self.getFakeQuestData())
        else:
            headerVO = {'isVisible': False}
        self.as_setDataS(headerVO)
        return

    def _populate(self):
        super(BCHangarHeader, self)._populate()
        g_bootcampEvents.onComponentAppear += self._onComponentAppear

    def _dispose(self):
        g_bootcampEvents.onComponentAppear -= self._onComponentAppear
        super(BCHangarHeader, self)._dispose()

    def _onComponentAppear(self, componentId):
        if componentId == self.__componentKey:
            self.update()
