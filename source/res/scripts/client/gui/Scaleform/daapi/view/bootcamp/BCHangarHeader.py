# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCHangarHeader.py
from gui.Scaleform.daapi.view.meta.BCHangarHeaderMeta import BCHangarHeaderMeta
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP

class BCHangarHeader(BCHangarHeaderMeta):

    def __init__(self, ctx=None):
        LOG_DEBUG_DEV_BOOTCAMP('BCHangarHeader.__init__')
        super(BCHangarHeader, self).__init__()

    def showQuestsWindow(self):
        from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
        from gui.shared import events, EVENT_BUS_SCOPE
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_QUESTS_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)
        from bootcamp.BootcampGarage import g_bootcampGarage
        if g_bootcampGarage.getPrevHint() == 'highlightButton_Quests_LessonV':
            g_bootcampGarage.hidePrevShowNextHint()

    def showPersonalQuests(self):
        self.showQuestsWindow()

    def showCommonQuests(self):
        self.showQuestsWindow()

    def getFakeQuestData(self):
        from gui.Scaleform.locale.RES_ICONS import RES_ICONS
        return {'commonQuestsLabel': '',
         'commonQuestsIcon': RES_ICONS.questsStateIconOutline('available'),
         'commonQuestsTooltip': '',
         'commonQuestsEnable': True}

    def update(self, *args):
        self._personalQuestID = None
        if self._currentVehicle.isPresent():
            vehicle = self._currentVehicle.item
            from gui.shared.formatters import text_styles
            from gui.Scaleform.locale.MENU import MENU
            from bootcamp.Bootcamp import g_bootcamp
            headerVO = {'tankType': '{}_elite'.format(vehicle.type) if vehicle.isElite else vehicle.type,
             'tankInfo': text_styles.concatStylesToMultiLine(text_styles.promoSubTitle(vehicle.shortUserName), text_styles.stats(MENU.levels_roman(vehicle.level))),
             'isPremIGR': vehicle.isPremiumIGR,
             'isVisible': True}
            headerVO.update(self.getFakeQuestData())
            headerVO.update(self.getFakeQuestData())
        else:
            headerVO = {'isVisible': False}
        self.as_setDataS(headerVO)
        return
