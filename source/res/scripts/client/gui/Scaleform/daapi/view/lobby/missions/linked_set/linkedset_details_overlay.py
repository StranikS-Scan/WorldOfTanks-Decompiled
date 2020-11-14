# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/linked_set/linkedset_details_overlay.py
import BigWorld
from gui.Scaleform.daapi.view.meta.LinkedSetDetailsOverlayMeta import LinkedSetDetailsOverlayMeta
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatErrorTextWithIcon, formatOkTextWithIcon
from gui.Scaleform.locale.LINKEDSET import LINKEDSET
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from helpers.i18n import makeString as _ms
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from adisp import process
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getLinkedSetBonuses
from gui.server_events.awards_formatters import getDefaultAwardFormatter
from gui.server_events.bonuses import mergeBonuses
from gui.server_events import settings as quest_settings
from helpers import dependency
from skeletons.gui.linkedset import ILinkedSetController
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.server_events.events_helpers import hasAtLeastOneAvailableQuest, isAllQuestsCompleted
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.STORAGE import STORAGE
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui import makeHtmlString
from shared_utils import CONST_CONTAINER
from gui.server_events.events_helpers import getLocalizedQuestNameForLinkedSetQuest, getLocalizedQuestDescForLinkedSetQuest, getLinkedSetMissionIDFromQuest
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.server_events import IEventsCache
from gui.server_events.conditions import getProgressFromQuestWithSingleAccumulative
_QUESTS_MOVIE_ROUTES = {(2, 1): 'X2',
 (2, 2): 'Module',
 (2, 3): 'Bullets',
 (2, 4): 'Store',
 (2, 5): 'Consumables',
 (2, 6): 'Exterior',
 (2, 7): 'Equipment',
 (2, 8): 'Reserves'}
_QUEST_MOVIE_GEN_PATH = '../flash/linkedSetVideo{}.swf'

class LinkedSetPagePaginatorColor(CONST_CONTAINER):
    COMPLETED = 'done'
    AVAILABLE = 'available'
    NOT_AVAILABLE = 'notAvailable'


class LinkedSetDetailsOverlay(LinkedSetDetailsOverlayMeta):
    linkedSet = dependency.descriptor(ILinkedSetController)
    eventsCache = dependency.descriptor(IEventsCache)
    bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(LinkedSetDetailsOverlay, self).__init__()
        self._quests = None
        self.__opener = None
        self._missionID = None
        self._selectedQuestID = 0
        self._pageCount = 0
        self._isSetupedFlashAnimTexts = False
        self._formatter = getDefaultAwardFormatter()
        self.unSeenQuestsCount = 0
        return

    def setOpener(self, view):
        self.__opener = view
        self._missionID = int(self.__opener.ctx['eventID'])
        self._quests = self.linkedSet.getMissionByID(self._missionID)
        self._selectedQuestID = self.getFirstSelectedQuestIndex(self._quests, defaultIndex=0)
        self.unSeenQuestsCount = sum((1 for quest in self._quests if quest.isAvailable().isValid and quest_settings.isNewCommonEvent(quest)))
        self._updateView()

    def getFirstSelectedQuestIndex(self, quests, defaultIndex=None):
        questIndex = None
        for index, quest in enumerate(quests):
            if quest.isAvailable().isValid and not quest.isCompleted():
                if questIndex is None:
                    questIndex = index
                if quest_settings.isNewCommonEvent(quest):
                    return index

        return questIndex or defaultIndex

    def setPage(self, pageID):
        self._selectedQuestID = pageID
        self._updateView()

    def updatePageCount(self, pageCount):
        if self._pageCount != pageCount:
            self._pageCount = pageCount
            if self._pageCount:
                pages = [ self._getPaginatorPageData(index, quest) for index, quest in enumerate(self._quests[:self._pageCount]) ]
            else:
                pages = []
            self.as_setColorPagesS(pages)

    def markVisited(self, quest):
        if quest_settings.isNewCommonEvent(quest):
            quest_settings.visitEventGUI(quest, counters=(_getNewMissionCounter,))
            self.unSeenQuestsCount -= 1
            if self.unSeenQuestsCount == 0:
                self.fireEvent(events.MissionsEvent(events.MissionsEvent.ON_LINKEDSET_STATE_UPDATED), EVENT_BUS_SCOPE.LOBBY)

    def isPlayBootcampMission(self):
        return self.isPlayBootcampQuest(self._quests[self._selectedQuestID])

    def isPlayBootcampQuest(self, quest):
        return self.linkedSet.isBootcampQuest(quest)

    def getBlockerMissionIDFor(self, missionID):
        return self.linkedSet.getInitialMissionID() if missionID != self.linkedSet.getInitialMissionID() else -1

    def getAwardsFromQuests(self, quests, isCompleted):
        bonuses = [ bonus for bonuses in [ self.getBonusesFromQuest(quest) for quest in quests ] for bonus in bonuses ]
        return self.getAwards(bonuses, isCompleted)

    def getAwardsFromQuest(self, quest, alpha=1.0):
        return self.getAwards(self.getBonusesFromQuest(quest), quest.isCompleted(), alpha)

    def getBonusesFromQuest(self, quest):
        return self.linkedSet.getBonusForBootcampMission() if self.isPlayBootcampQuest(quest) else quest.getBonuses()

    def getAwards(self, bonuses, isCompleted, alpha=1.0):
        return [ {'icon': award['imgSource'],
         'value': award['label'],
         'isCompleted': isCompleted,
         'tooltip': award.get('tooltip', None),
         'specialAlias': award.get('specialAlias', None),
         'specialArgs': award.get('specialArgs', None),
         'alpha': alpha} for award in getLinkedSetBonuses(mergeBonuses(bonuses)) if award ]

    def startClick(self, eventID):
        if self.isPlayBootcampMission():
            self._goToBootcamp()

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def getMissionCompleteBackground(self, missionID):
        return RES_ICONS.getLinkedSetMissionCompleteBackground(missionID)

    def getMissionDisableBackground(self, missionID):
        return RES_ICONS.getLinkedSetMissionDisableBackground(missionID)

    def getQuestActiveBackground(self, missionID, questID):
        return RES_ICONS.getLinkedSetQuestActiveBackground(missionID, questID)

    def isQuestBackgroundIsMovie(self, quest):
        return getLinkedSetMissionIDFromQuest(quest) == 2

    def _populate(self):
        super(LinkedSetDetailsOverlay, self)._populate()
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._onSyncCompleted()

    def _dispose(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        super(LinkedSetDetailsOverlay, self)._dispose()

    def _onSyncCompleted(self):
        if self.__opener and self.linkedSet.isLinkedSetEnabled():
            self._quests = self.linkedSet.getMissionByID(self._missionID)
            if self._selectedQuestID >= len(self._quests):
                self._selectedQuestID = 0
            self._updateView()

    @process
    def _goToBootcamp(self):
        if self.isPlayBootcampMission() and self.prbDispatcher is not None and self.linkedSet.isLinkedSetEnabled():
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.BOOTCAMP))
        return

    def _updateView(self):
        if not self._quests:
            return
        pageCount = 0
        if isAllQuestsCompleted(self._quests):
            data = self._getViewDataForCompletedMission()
        elif hasAtLeastOneAvailableQuest(self._quests):
            data = self._getViewDataForAvailableMission()
            questsCount = len(self._quests)
            pageCount = questsCount if questsCount > 1 else 0
            if self._quests[self._selectedQuestID].isAvailable().isValid:
                self.markVisited(self._quests[self._selectedQuestID])
        else:
            data = self._getViewDataForNotAvailableMission()
        self.as_setDataS(data)
        self.updatePageCount(pageCount)
        if self._pageCount:
            self.as_setPageS(self._selectedQuestID)

    def _getPaginatorPageData(self, index, quest):
        if quest.isCompleted():
            status = LinkedSetPagePaginatorColor.COMPLETED
        elif quest.isAvailable().isValid:
            status = LinkedSetPagePaginatorColor.AVAILABLE
        else:
            status = LinkedSetPagePaginatorColor.NOT_AVAILABLE
        return {'buttonsGroup': 'linkedSetButtons',
         'status': status,
         'pageIndex': index,
         'label': str(index + 1)}

    def _getViewDataForCompletedMission(self):
        missionName = _ms(LINKEDSET.getMissionName(self._missionID))
        return self._getViewData(title=missionName, status=formatOkTextWithIcon(_ms(LINKEDSET.COMPLETED)), info=_ms(LINKEDSET.COMPLETED), task=_ms(LINKEDSET.REWARD_FOR_COMPLETED_MISSION, mission_name=missionName), isBackOverlay=True, isMovie=False, back=self.getMissionCompleteBackground(self._missionID), awards=self.getAwardsFromQuests(self._quests, True))

    def _getViewDataForNotAvailableMission(self):
        missionBlockerName = _ms(LINKEDSET.getMissionName(self.getBlockerMissionIDFor(self._missionID)))
        missionName = _ms(LINKEDSET.getMissionName(self._missionID))
        return self._getViewData(title=missionName, status=formatErrorTextWithIcon(_ms(LINKEDSET.NOT_AVAILABLE)), info=_ms(LINKEDSET.NOT_AVAILABLE), task=_ms(LINKEDSET.COMPLETE_MISSION_BEFORE, mission_name=missionBlockerName), description=_ms(LINKEDSET.REWARD_FOR_UNCOMPLETED_MISSION, quest_name=missionName), isBackOverlay=False, isMovie=False, back=self.getMissionDisableBackground(self._missionID), awards=self.getAwardsFromQuests(self._quests, False))

    def _getViewDataForAvailableMission(self):
        selectedQuest = self._quests[self._selectedQuestID]
        isCompleted = selectedQuest.isCompleted()
        isAvailable = isCompleted or selectedQuest.isAvailable().isValid
        if isCompleted:
            cardStatus = formatOkTextWithIcon(_ms(LINKEDSET.COMPLETED))
        elif isAvailable:
            cardStatus = _ms(LINKEDSET.AVAILABLE)
        else:
            cardStatus = formatErrorTextWithIcon(_ms(LINKEDSET.NOT_AVAILABLE))
        if len(self._quests) > 1:
            cardTitle = _ms(LINKEDSET.QUEST_CARD_TITLE, mission_name=_ms(LINKEDSET.getMissionName(self._missionID)), quest_name=getLocalizedQuestNameForLinkedSetQuest(selectedQuest))
        else:
            cardTitle = getLocalizedQuestNameForLinkedSetQuest(selectedQuest)
        if isCompleted:
            return self._getViewData(title=cardTitle, status=cardStatus, info=_ms(LINKEDSET.COMPLETED), task=_ms(LINKEDSET.REWARD_FOR_COMPLETED_QUEST, quest_name=cardTitle), isBackOverlay=isCompleted, isMovie=False, back=self.getMissionCompleteBackground(self._missionID), awards=self.getAwardsFromQuest(selectedQuest))
        elif isAvailable:
            isMovie = self.isQuestBackgroundIsMovie(selectedQuest)
            if isMovie:
                self._setupFlashAnimTexts()
                back = _getQuestItemActiveAnimBackground(self._missionID, self._selectedQuestID + 1)
            else:
                back = self.getQuestActiveBackground(self._missionID, self._selectedQuestID + 1)
            if self.isPlayBootcampMission():
                questName = getLocalizedQuestNameForLinkedSetQuest(selectedQuest)
                if self.bootcamp.runCount():
                    btnStartLabel = LINKEDSET.CONTINUE_QUEST_BTN
                else:
                    btnStartLabel = LINKEDSET.START_QUEST_BTN
                btnStartLabel = _ms(btnStartLabel, quest_name=questName)
            else:
                btnStartLabel = None
            progressValue = None
            curProgress, maxProgress = getProgressFromQuestWithSingleAccumulative(selectedQuest)
            if curProgress is not None and maxProgress:
                cardStatus = makeHtmlString('html_templates:lobby/quests/linkedSet', 'questProgressTemplate', {'curValue': backport.getIntegralFormat(curProgress),
                 'maxValue': backport.getIntegralFormat(maxProgress)})
                progressValue = curProgress * 100 // maxProgress
            return self._getViewData(title=cardTitle, status=cardStatus, description=getLocalizedQuestDescForLinkedSetQuest(selectedQuest), isBackOverlay=isCompleted, isMovie=isMovie, back=back, awards=self.getAwardsFromQuest(selectedQuest), btnStartLabel=btnStartLabel, progressValue=progressValue)
        else:
            questBeforeID = self._quests[self._selectedQuestID - 1]
            questBeforeName = _ms(LINKEDSET.QUEST_CARD_TITLE, mission_name=_ms(LINKEDSET.getMissionName(self._missionID)), quest_name=getLocalizedQuestNameForLinkedSetQuest(questBeforeID))
            return self._getViewData(title=cardTitle, status=cardStatus, info=_ms(LINKEDSET.NOT_AVAILABLE), task=_ms(LINKEDSET.COMPLETE_QUEST_BEFORE, quest_name=questBeforeName), isBackOverlay=isCompleted, isMovie=False, back=self.getMissionCompleteBackground(self._missionID), awards=self.getAwardsFromQuest(selectedQuest, alpha=0.5))
            return

    def _getViewData(self, title=None, status=None, info=None, task=None, description=None, isBackOverlay=None, isMovie=None, back=None, btnStartLabel=None, awards=None, progressValue=None):
        res = {'title': title,
         'status': status,
         'info': info,
         'task': task,
         'description': description,
         'isBackOverlay': isBackOverlay,
         'isMovie': isMovie,
         'back': back,
         'btnStartLabel': btnStartLabel,
         'awards': awards,
         'isProgressBar': progressValue is not None}
        if progressValue is not None:
            res['progressBarData'] = {'value': progressValue,
             'minValue': 0,
             'maxValue': 100}
        return res

    def _setupFlashAnimTexts(self):
        if not self._isSetupedFlashAnimTexts:
            self.as_setDataVideoS({'headerServiceText': MENU.HANGAR_AMMUNITIONPANEL_TECHNICALMAITENANCE_EQUIPMENT_LABEL,
             'headerDepotText': STORAGE.STORAGE_SECTIONTITLE,
             'headerConfirmSaleText': DIALOGS.SELLMODULECONFIRMATION_TITLE,
             'headerEquipmentText': MENU.OPTIONALDEVICEFITS_TITLE,
             'btnBattleText': MENU.HEADERBUTTONS_BATTLE,
             'btnAcceptText': MENU.HANGAR_AMMUNITIONPANEL_TECHNICALMAITENANCE_BUTTONS_APPLY,
             'btnResearchText': MENU.CONTEXTMENU_UNLOCK,
             'btnStoreText': MENU.HEADERBUTTONS_STORAGE,
             'btnSellText': DIALOGS.SELLMODULECONFIRMATION_SUBMIT,
             'btnCancelText': DIALOGS.SELLCONFIRMATION_CANCEL,
             'txtTotalText': MENU.AMMORELOAD_TOTALCOST,
             'headerPersonalReservesText': MENU.BOOSTERSWINDOW_TITLE,
             'btnActivateText': MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_ACTIVATEBTNLABEL,
             'txtMyProfileText': BigWorld.player().name,
             'headerExteriorText': MENU.HANGAR_AMMUNITIONPANEL_TUNINGBTN,
             'btnExteriorText': MENU.HANGAR_AMMUNITIONPANEL_TUNINGBTN,
             'btnServiceText': MENU.HANGAR_AMMUNITIONPANEL_MAITENANCEBTN,
             'btnPurchaseText': VEHICLE_CUSTOMIZATION.COMMIT_BUY})
            self._isSetupedFlashAnimTexts = True


def _getNewMissionCounter(eventsCache):
    return ('missions', len(quest_settings.getNewCommonEvents(eventsCache.getAdvisableQuests().itervalues())))


def _getQuestItemActiveAnimBackground(missionID, questID):
    return _QUEST_MOVIE_GEN_PATH.format(_QUESTS_MOVIE_ROUTES.get((missionID, questID)))
