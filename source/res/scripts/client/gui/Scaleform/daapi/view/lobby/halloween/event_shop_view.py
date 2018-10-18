# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/halloween/event_shop_view.py
import time
import GUI
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.EventShopViewMeta import EventShopViewMeta
from gui.Scaleform.locale.EVENT import EVENT
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.events import LobbyHeaderMenuEvent
from helpers import dependency, time_utils
from helpers.i18n import makeString as _ms
from skeletons.gui.halloween_controller import IHalloweenController
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
_SOULS_COUNT_IN_FORMULA = 100

class EventShopView(EventShopViewMeta):
    halloweenController = dependency.descriptor(IHalloweenController)
    __background_alpha__ = 0

    def __init__(self, _=None):
        super(EventShopView, self).__init__()
        self.__blur = GUI.WGUIBackgroundBlur()
        self._prevSouls = -1

    def closeView(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def onBuyItem(self, itemId):
        self.halloweenController.getProgress().buyItem(itemId)

    def _populate(self):
        super(EventShopView, self)._populate()
        self.halloweenController.getProgress().onItemsUpdated += self._onItemsUpdated
        self.__updateList()
        self.__blur.enable = True
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        if self.halloweenController.getProgress():
            self.halloweenController.getProgress().onItemsUpdated -= self._onItemsUpdated
        self.__blur.enable = False
        self.fireEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        super(EventShopView, self)._dispose()

    def _onItemsUpdated(self):
        self.__updateList()

    @staticmethod
    def _getDate(timeValue, fmtKey, fullMonthName=False):
        additionalArgs = None
        if fullMonthName:
            additionalArgs = {'month_s': _ms(MENU.datetime_months(time.localtime(timeValue).tm_mon))}
        return makeHtmlString('html_templates:lobby/quests/halloween', 'shopBannerDescDateTemplate', {'msg': time_utils.getTimeString(timeValue, fmtKey, additionalArgs)})

    def __updateList(self):
        halloweenProgress = self.halloweenController.getProgress()
        items = []
        maxProgressItem = halloweenProgress.getMaxProgressItem()
        self.as_setMaxBonusDataS(maxProgressItem.getGUIBonusData())
        isCompleted = halloweenProgress.isCompleted()
        maxLevelCost = str(halloweenProgress.getCurrentCostForLevel())
        dateInfo = ' '.join((self._getDate(halloweenProgress.getLastQuestStartTime(), EVENT.SHOP_SHORT_DATE), makeHtmlString('html_templates:lobby/quests/halloween', 'shopBannerDescTemplate', {'msg': _ms(EVENT.SHOP_DATE_INFO)}), self._getDate(halloweenProgress.getFinishTime(), EVENT.SHOP_SHORT_DATE)))
        timeLeft = _ms(EVENT.SHOP_COST_INFO_TIMELEFT, time=time_utils.getTillTimeString(halloweenProgress.getFinishTimeLeft(), MENU.TIME_TIMEVALUE))
        costText = ' '.join((makeHtmlString('html_templates:lobby/quests/halloween', 'shopBannerTittleTemplate', {'msg': _ms(EVENT.SHOP_COST_INFO)}), makeHtmlString('html_templates:lobby/quests/halloween', 'shopBannerTittleDateTemplate', {'msg': timeLeft})))
        dateHeader = makeHtmlString('html_templates:lobby/quests/halloween', 'shopBannerTittleTemplate', {'msg': _ms(EVENT.SHOP_BUY_DESCRIPTION)})
        startDate = makeHtmlString('html_templates:lobby/quests/halloween', 'shopBannerDescDateTemplate', {'msg': self._getDate(halloweenProgress.getStartTime(), EVENT.SHOP_FULL_DATE, True)})
        endDate = makeHtmlString('html_templates:lobby/quests/halloween', 'shopBannerDescDateTemplate', {'msg': self._getDate(halloweenProgress.getFinishTime(), EVENT.SHOP_FULL_DATE, True)})
        storyDateText = makeHtmlString('html_templates:lobby/quests/halloween', 'shopBannerDescTemplate', {'msg': _ms(EVENT.SHOP_DESCRIPTION, startDate=startDate, endDate=endDate)})
        bonusesForSoul = halloweenProgress.getBonusesForSoul()
        self.as_setShopDataS({'canBuy': not isCompleted,
         'cost': maxLevelCost,
         'dateHeader': dateHeader,
         'costText': costText,
         'dateInfo': dateInfo,
         'lastLevelReached': isCompleted,
         'lastLevelAvailable': maxProgressItem.isUnlocked(),
         'storyDateText': storyDateText,
         'costLabel': _ms(EVENT.SHOP_MAXLEVEL),
         'dateLabel': _ms(EVENT.SHOP_MAXLEVEL),
         'buyAvailable': halloweenProgress.isMaxLevelBuyEnabled(),
         'formulaSouls': _SOULS_COUNT_IN_FORMULA,
         'formulaExp1': int(_SOULS_COUNT_IN_FORMULA * bonusesForSoul['xpPerPoint']),
         'formulaExp2': int(_SOULS_COUNT_IN_FORMULA * bonusesForSoul['freeXpPerPoint'])})
        maxSouls = 0
        currentSouls = 0
        for item in self.halloweenController.getProgress().items:
            maxSouls += item.getMaxProgress()
            currentSouls += item.getCurrentProgress()
            level = item.getLevel()
            items.append({'index': level,
             'unlocked': isCompleted or item.isUnlocked() or item.isAvailable() or item.isCompleted(),
             'value': maxSouls,
             'specialAlias': TOOLTIPS_CONSTANTS.HALLOWEEN_PROGRESS_TOOLTIP,
             'specialArgs': (level,),
             'isSpecial': None,
             'bonus': item.getGUIBonusData().get('bonus'),
             'statusDescription': item.getStatusDescription()})

        if isCompleted:
            currentSouls = maxSouls
        self.as_setProgressDataS(items)
        self.as_setProgressValueS(currentSouls, self._prevSouls)
        self._prevSouls = currentSouls
        return
