# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/boosters/BoostersWindow.py
import BigWorld
import constants
from collections import defaultdict
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.boosters.BoostersPanelComponent import ADD_BOOSTER_ID
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.daapi.view.meta.BoostersWindowMeta import BoostersWindowMeta
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework import AppRef
from gui.goodies.Booster import MAX_ACTIVE_BOOSTERS_COUNT
from gui.goodies.GoodiesCache import g_goodiesCache
from gui.server_events import g_eventsCache, events_dispatcher as quests_events
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items.processors.goodies import BoosterActivator
from gui.shared.utils.decorators import process
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class BoostersWindow(View, BoostersWindowMeta, AbstractWindowView, AppRef):

    def __init__(self, ctx = None):
        super(BoostersWindow, self).__init__()
        self._availableBoosters = None
        self._boosterQuests = None
        self._activeBoosters = None
        self._isReceivedBoostersTab = ctx.get('slotID', None) != ADD_BOOSTER_ID
        self._boostersInQuestCount = 0
        return

    def onWindowClose(self):
        self.destroy()

    def requestBoostersArray(self, isReceivedBoostersTab):
        self._isReceivedBoostersTab = isReceivedBoostersTab
        self.as_setListDataS(self.__getBoostersVOs(self._isReceivedBoostersTab), False)
        self.__setCommonData()

    def onBoosterActionBtnClick(self, boosterID, questID):
        if self._isReceivedBoostersTab:
            booster = g_goodiesCache.getBooster(boosterID)
            self.__activateBoosterRequest(booster)
        else:
            quests_events.showEventsWindow(questID, constants.EVENT_TYPE.BATTLE_QUEST)

    def _populate(self):
        super(BoostersWindow, self)._populate()
        g_clientUpdateManager.addCallbacks({'goodies': self.__onUpdateGoodies})
        g_eventsCache.onSyncCompleted += self.__onUpdateGoodies
        self._availableBoosters = self.__getAvailableBoosters()
        self._boosterQuests = self.__getBoosterQuests()
        self._activeBoosters = self.__getActiveBooster()
        self._boostersInQuestCount = self.__getBoostersCountInQuests()
        self.as_setListDataS(self.__getBoostersVOs(self._isReceivedBoostersTab), True)
        self.__setCommonData()
        self.__setStaticData()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_eventsCache.onSyncCompleted -= self.__onUpdateGoodies
        self._availableBoosters = None
        self._boosterQuests = None
        self._activeBoosters = None
        self._isReceivedBoostersTab = None
        super(BoostersWindow, self)._dispose()
        return

    def __onUpdateGoodies(self, *args):
        self._activeBoosters = self.__getActiveBooster()
        self._availableBoosters = self.__getAvailableBoosters()
        self._boosterQuests = self.__getBoosterQuests()
        self._boostersInQuestCount = self.__getBoostersCountInQuests()
        self.__setCommonData()
        self.as_setListDataS(self.__getBoostersVOs(self._isReceivedBoostersTab), False)

    def __setStaticData(self):
        self.as_setStaticDataS({'noInfoText': text_styles.standard(MENU.BOOSTERSWINDOW_BOOSTERSTABLE_NOINFO),
         'windowTitle': _ms(MENU.BOOSTERSWINDOW_TITLE),
         'closeBtnLabel': _ms(MENU.BOOSTERSWINDOW_CLOSEBTN_LABEL),
         'noInfoBgSource': RES_ICONS.MAPS_ICONS_BOOSTERS_NOINFOBG})

    def __setCommonData(self):
        isHaveNotInfo = not self._boostersInQuestCount
        if self._isReceivedBoostersTab:
            isHaveNotInfo = not len(self._availableBoosters)
        self.as_setDataS({'isHaveNotInfo': isHaveNotInfo,
         'availableTabLabel': self.__getAvailableTabLabel(),
         'notAvailableTabLabel': self.__getNotAvailableTabLabel(),
         'activeText': self.__getActiveText(),
         'isReceivedBoostersTab': self._isReceivedBoostersTab})

    def __getBoostersCountInQuests(self):
        boostersCount = 0
        questsBoosters = self._boosterQuests.values()
        for boosters in questsBoosters:
            for _, count in boosters:
                boostersCount += count

        return boostersCount

    def __getAvailableTabLabel(self):
        boostersCount = sum((booster.count for booster in self._availableBoosters))
        return _ms(MENU.BOOSTERSWINDOW_TABS_AVAILABLELABEL, availableNo=boostersCount)

    def __getNotAvailableTabLabel(self):
        return _ms(MENU.BOOSTERSWINDOW_TABS_NOTAVAILABLELABEL, notAvailableNo=self._boostersInQuestCount)

    def __getActiveText(self):
        return text_styles.highTitle(_ms(MENU.BOOSTERSWINDOW_ACTIVEBOOSTERS, activeNo=len(self._activeBoosters), allNo=MAX_ACTIVE_BOOSTERS_COUNT))

    def __getBoostersVOs(self, isReceivedBoostersTab):
        boosterVOs = []
        isLimitExceeded = len(self._activeBoosters) >= MAX_ACTIVE_BOOSTERS_COUNT
        if isReceivedBoostersTab:
            for booster in self._availableBoosters:
                boosterVOs.append(self.__makeBoosterVO(booster, not isLimitExceeded))

        else:
            for (questID, qUserName), boosters in self._boosterQuests.iteritems():
                for booster, count in boosters:
                    boosterVOs.append(self.__makeBoosterVO(booster, questID is not None, questID, qUserName, count))

        return boosterVOs

    def __makeBoosterVO(self, booster, isBtnEnabled, questID = None, qUserName = None, qBoosterCount = None):
        headerText = _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_HEADER, boosterName=booster.userName, quality=booster.qualityStr)
        activateBtnLabel = MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_ACTIVATEBTNLABEL if questID is None else MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_GOTOQUESTBTNLABEL
        if self._isReceivedBoostersTab:
            actionBtnEnabled = booster.isReadyToActivate and isBtnEnabled
        else:
            actionBtnEnabled = isBtnEnabled
        return {'id': booster.boosterID,
         'questID': questID,
         'actionBtnEnabled': actionBtnEnabled,
         'actionBtnTooltip': self.__getQuestTooltip(qUserName),
         'headerText': text_styles.middleTitle(headerText),
         'descriptionText': text_styles.main(booster.description),
         'addDescriptionText': self.__getAdditionalDescription(booster, qUserName),
         'actionBtnLabel': _ms(activateBtnLabel),
         'boosterSlotVO': self.__makeBoosterSlotVO(booster, qBoosterCount)}

    def __makeBoosterSlotVO(self, booster, qBoosterCount):
        boosterCount = qBoosterCount or booster.count
        return {'icon': booster.icon,
         'countText': text_styles.counter(str(boosterCount)),
         'showCount': boosterCount > 1,
         'qualityIconSrc': booster.getQualityIcon(),
         'slotLinkage': BOOSTER_CONSTANTS.SLOT_UI,
         'showLeftTime': False}

    def __getQuestTooltip(self, qUserName):
        if qUserName is not None:
            return makeTooltip(None, _ms(TOOLTIPS.BOOSTER_QUESTLINKBTN_BODY, questName=qUserName))
        else:
            return ''

    def __getAdditionalDescription(self, booster, qUserName):
        text = ''
        if qUserName is not None:
            text = _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_QUESTFOROPEN, questName=qUserName)
        elif booster.expiryTime is not None:
            text = _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_TIME, tillTime=booster.getExpiryDate())
        return text_styles.standard(text)

    def __getAvailableBoosters(self):
        criteria = REQ_CRITERIA.BOOSTER.IN_ACCOUNT
        return g_goodiesCache.getBoosters(criteria=criteria).values()

    def __getActiveBooster(self):
        return g_goodiesCache.getBoosters(criteria=REQ_CRITERIA.BOOSTER.ACTIVE).values()

    def __getBoosterQuests(self):
        result = defaultdict(list)
        quests = g_eventsCache.getQuests(lambda q: not q.isCompleted())
        for q in quests.itervalues():
            bonuses = q.getBonuses('goodies')
            for b in bonuses:
                boosters = b.getBoosters()
                for booster, count in boosters.iteritems():
                    result[q.getID(), q.getUserName()].append((booster, count))

        return result

    @process('loadStats')
    def __activateBoosterRequest(self, booster):
        result = yield BoosterActivator(booster).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
