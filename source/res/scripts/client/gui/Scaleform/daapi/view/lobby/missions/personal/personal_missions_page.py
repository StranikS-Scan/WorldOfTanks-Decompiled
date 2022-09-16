# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/personal_missions_page.py
import logging
import operator
from collections import namedtuple
import BigWorld
from gui import SystemMessages
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions import missions_helper
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getHtmlAwardSheetIcon
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import getChainVehRequirements
from gui.Scaleform.daapi.view.meta.PersonalMissionsPageMeta import PersonalMissionsPageMeta
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.PERSONAL_MISSIONS_ALIASES import PERSONAL_MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.event_items import PersonalMission
from gui.server_events.events_dispatcher import showPersonalMissionDetails, hidePersonalMissionDetails, showPersonalMissionAwards
from gui.server_events.events_helpers import AwardSheetPresenter
from gui.server_events.personal_missions_navigation import PersonalMissionsNavigation
from gui.server_events.pm_constants import SOUNDS, PERSONAL_MISSIONS_SOUND_SPACE, PM_TUTOR_FIELDS as _PTF
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import PersonalMissionsEvent, LoadViewEvent
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Vehicle import getTypeShortUserName
from gui.shared.gui_items.processors import quests
from gui.shared.utils import decorators
from helpers import dependency
from helpers.i18n import makeString as _ms
from personal_missions import PM_BRANCH, PM_BRANCH_TO_FINAL_PAWN_COST
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)
_ChainState = namedtuple('_ChainState', ['hasUnlocked',
 'hasVehicle',
 'isCompleted',
 'isFullCompleted',
 'questInProgress'])
_UI_CHAINS_LEN = {PM_BRANCH.REGULAR: 5,
 PM_BRANCH.PERSONAL_MISSION_2: 4}

class PersonalMissionsPage(LobbySubView, PersonalMissionsPageMeta, PersonalMissionsNavigation):
    _COMMON_SOUND_SPACE = PERSONAL_MISSIONS_SOUND_SPACE
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        super(PersonalMissionsPage, self).__init__(ctx)
        self.__mapView = None
        self.__eventID = None
        self.__lastTutorState = None
        self.__backAlias = None
        self.__callbackID = None
        self.__isPersonalMissionDetailsVisible = False
        self.__initialize(ctx)
        return

    def showAwards(self):
        showPersonalMissionAwards()

    def onBarClick(self, chainID, operationID):
        if chainID == -1 or operationID == -1:
            return
        if chainID != self.getChainID():
            self.soundManager.playInstantSound(SOUNDS.CHAIN_NAV_CLICK)
        if operationID != self.getOperationID():
            self.soundManager.playInstantSound(SOUNDS.OPERATION_NAV_CLICK_ANIMATION)
            self.soundManager.playInstantSound(SOUNDS.OPERATION_NAV_CLICK)
        self.__navigateTo(operationID, chainID)

    def onSkipTaskClick(self):
        chainState = self.__getChainState(self.getChain())
        if chainState.questInProgress is not None:
            self.__pawnMission(chainState.questInProgress)
        else:
            _logger.error('No quest in progress to pawn: %s', chainState)
        return

    def closeView(self):
        event = g_entitiesFactories.makeLoadEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR))
        self.fireEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def onTutorialAcceptBtnClicked(self):
        if self.__lastTutorState in (_PTF.ONE_FAL_SHOWN, _PTF.PM2_ONE_FAL_SHOWN):
            self.soundManager.playSound(SOUNDS.ONE_AWARD_LIST_RECEIVED_CONFIRM)
        self.__resetToIncomplete()
        if self.__lastTutorState in (_PTF.MULTIPLE_FAL_SHOWN, _PTF.PM2_MULTIPLE_FAL_SHOWN):
            if self.__PMCache.getFreeTokensCount(self.getBranch()) >= PM_BRANCH_TO_FINAL_PAWN_COST[self.getBranch()]:
                showPersonalMissionDetails(self.__getLastQuest().getID())
            else:
                self.as_showAwardsPopoverForTutorS()

    def onBackBtnClick(self):
        backAlias = self.__backAlias or PERSONAL_MISSIONS_ALIASES.PERSONAL_MISSIONS_OPERATIONS
        self.fireEvent(LoadViewEvent(SFViewLoadParams(backAlias)), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(PersonalMissionsPage, self)._populate()
        self._eventsCache.onSyncCompleted += self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated += self.__onQuestsUpdated
        self.addListener(PersonalMissionsEvent.ON_DETAILS_VIEW_CLOSE, self.__onDetailsViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(PersonalMissionsEvent.ON_DETAILS_VIEW_OPEN, self.__onDetailsViewOpen, EVENT_BUS_SCOPE.LOBBY)
        self.__tryOpenMissionDetails()
        self.as_initViewS(self.getBranch(), _UI_CHAINS_LEN[self.getBranch()])
        self.__updateComponents()
        self.soundManager.setRTPC(SOUNDS.RTCP_MISSIONS_ZOOM, SOUNDS.MIN_MISSIONS_ZOOM)
        self.soundManager.setRTPC(SOUNDS.RTCP_DEBRIS_CONTROL, SOUNDS.MIN_MISSIONS_ZOOM)
        if not self.__eventID:
            self.__checkTutorState()

    def _dispose(self):
        self.soundManager.stopSound(SOUNDS.ONE_AWARD_LIST_RECEIVED)
        self.soundManager.stopSound(SOUNDS.FOUR_AWARD_LISTS_RECEIVED)
        self.soundManager.stopSound(SOUNDS.ONE_AWARD_LIST_RECEIVED_CONFIRM)
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        self._eventsCache.onSyncCompleted -= self.__onQuestsUpdated
        self._eventsCache.onProgressUpdated -= self.__onQuestsUpdated
        self.removeListener(PersonalMissionsEvent.ON_DETAILS_VIEW_CLOSE, self.__onDetailsViewClose, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(PersonalMissionsEvent.ON_DETAILS_VIEW_OPEN, self.__onDetailsViewOpen, EVENT_BUS_SCOPE.LOBBY)
        super(PersonalMissionsPage, self)._dispose()
        return

    def _invalidate(self, ctx=None):
        super(PersonalMissionsPage, self)._invalidate(ctx)
        self.__initialize(ctx)
        self.as_reInitViewS(self.getBranch(), _UI_CHAINS_LEN[self.getBranch()])
        self.__tryOpenMissionDetails()
        self.__updateComponents()
        if self.__mapView:
            self.__updateMapData()

    def _onRegisterFlashComponent(self, viewPy, alias):
        self.__mapView = viewPy
        self.__updateMapData()

    def __collectSideBarData(self):
        currentOperation = self.getOperation()
        chains = []
        if self.getBranch() == PM_BRANCH.PERSONAL_MISSION_2:
            tooltip = TOOLTIPS_CONSTANTS.OPERATIONS_CHAIN_DETAILS
        else:
            tooltip = None
        for classifierAttr in currentOperation.getIterationChain():
            chainID, q = currentOperation.getChainByClassifierAttr(classifierAttr)
            chainState = self.__getChainState(q)
            progress = self.__getProgress(q)
            if chainState.isCompleted:
                currentProgress = text_styles.bonusAppliedText(progress['value'])
            else:
                currentProgress = text_styles.stats(progress['value'])
            if chainID == self.getChainID():
                label = text_styles.tutorial(currentOperation.getChainName(chainID))
            elif chainState.questInProgress is not None:
                label = text_styles.main(chainState.questInProgress.getShortUserName())
            elif chainState.isFullCompleted:
                label = text_styles.bonusAppliedText(PERSONAL_MISSIONS.SIDEBAR_FULLCOMPLETED)
            elif chainState.isCompleted:
                label = text_styles.bonusAppliedText(PERSONAL_MISSIONS.SIDEBAR_COMPLETED)
            else:
                label = text_styles.main(PERSONAL_MISSIONS.SIDEBAR_NOTSELECTED)
            progressText = text_styles.main(' / ').join((currentProgress, text_styles.main(progress['maxValue'])))
            chains.append({'chainID': chainID,
             'progressText': progressText,
             'label': label,
             'tankIcon': currentOperation.getChainIcon(chainID),
             'progress': progress,
             'tooltip': tooltip})

        return chains

    @property
    def __PMCache(self):
        return self._eventsCache.getPersonalMissions()

    def __onDetailsViewOpen(self, _):
        self.__isPersonalMissionDetailsVisible = True
        self.as_setContentVisibleS(False)

    def __onDetailsViewClose(self, _):
        self.__isPersonalMissionDetailsVisible = False
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
        self.__callbackID = BigWorld.callback(0.3, self.__checkTutorState)
        self.as_setContentVisibleS(True)
        return

    def __initialize(self, ctx=None):
        ctx = ctx or {}
        eventID = ctx.get('eventID')
        operationID = ctx.get('operationID')
        chainID = ctx.get('chainID')
        if operationID:
            branch = self._eventsCache.getPersonalMissions().getAllOperations().get(operationID).getBranch()
        else:
            branch = ctx.get('branch')
        if branch is not None:
            self.setBranch(branch)
        self.__backAlias = ctx.get('previewAlias')
        self.__eventID = int(eventID) if eventID is not None else eventID
        if eventID:
            quest = self.__PMCache.getAllQuests().get(self.__eventID)
            if quest:
                self.setBranch(quest.getQuestBranch())
                self.setOperationID(quest.getOperationID())
                self.setChainID(quest.getChainID())
        else:
            if operationID:
                self.setOperationID(operationID)
            if chainID:
                self.setChainID(chainID)
        return

    def __updateComponents(self):
        self.__updateHeader()
        self.__updateSideBar()
        self.__updateFooter()

    def __updateMapData(self):
        if self.__mapView:
            self.__mapView.refresh()

    def __getProgress(self, pmQuests):
        completed = filter(operator.methodcaller('isCompleted'), pmQuests.itervalues())
        return {'value': len(completed),
         'minValue': 0,
         'maxValue': len(pmQuests),
         'useAnim': False}

    def __updateHeader(self):
        self.as_setHeaderDataS({'operations': missions_helper.getOperations(self.getBranch(), self.getOperationID()),
         'operationTitle': self.__getOperationTitle(),
         'backBtnLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_LABEL,
         'backBtnDescrLabel': PERSONAL_MISSIONS.HEADER_BACKBTN_DESCRLABEL_CAMPAIGN})

    def __updateFooter(self):
        chainState = self.__getChainState(self.getChain())
        isQuestInProgress = False
        btnVisible = False
        btnEnabled = False
        btnLabel = ''
        descr = ''
        currentOperation = self.getOperation()
        chainClassifier = currentOperation.getChainClassifier(self.getChainID())
        vehicleClass = getTypeShortUserName(chainClassifier.classificationAttr)
        pm = self._eventsCache.getPersonalMissions()
        branch = self.getBranch()
        freeSheets = pm.getFreeTokensCount(branch)
        pawnedSheets = pm.getPawnedTokensCount(branch)
        if not chainState.hasUnlocked:
            status = text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(PERSONAL_MISSIONS.STATUSPANEL_STATUS_LOCKED))
        elif chainState.questInProgress is not None:
            quest = chainState.questInProgress
            if quest.isOnPause:
                status = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ONPAUSE, 16, 16, -3, 8), text_styles.playerOnline(quest.getUserName()))
            else:
                isQuestInProgress = True
                status = text_styles.concatStylesWithSpace(icons.inProgress(), text_styles.tutorial(quest.getUserName()))
            if quest.areTokensPawned():
                descr = text_styles.neutral(_ms(PERSONAL_MISSIONS.STATUSPANEL_STATUS_PAWNED, count=quest.getPawnCost(), icon=getHtmlAwardSheetIcon(quest.getQuestBranch())))
            elif quest.isMainCompleted():
                descr = text_styles.neutral(PERSONAL_MISSIONS.STATUSPANEL_STATUS_IMPROVE)
            elif quest.canBePawned() and not quest.isDisabled():
                btnVisible = True
                pawnCost = quest.getPawnCost()
                btnLabel = _ms(PERSONAL_MISSIONS.STATUSPANEL_FREESHEETBTN_LABEL, count=pawnCost, icon=getHtmlAwardSheetIcon(quest.getQuestBranch()))
                if pawnCost <= freeSheets:
                    btnEnabled = True
        elif chainState.isFullCompleted:
            status = text_styles.concatStylesWithSpace(icons.doubleCheckmark(1), text_styles.bonusAppliedText(_ms(PERSONAL_MISSIONS.STATUSPANEL_STATUS_ALLEXCELLENTDONE, vehicleClass=vehicleClass)))
        elif chainState.isCompleted:
            status = text_styles.concatStylesWithSpace(icons.checkmark(-2), text_styles.bonusAppliedText(_ms(PERSONAL_MISSIONS.STATUSPANEL_STATUS_ALLDONE, vehicleClass=vehicleClass)))
        elif not chainState.hasVehicle:
            if self.getBranch() == PM_BRANCH.PERSONAL_MISSION_2:
                template = PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_NOVEHICLE_PM2
            else:
                template = PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_NOVEHICLE_REGULAR
            vehData = getChainVehRequirements(currentOperation, self.getChainID(), useIcons=False)
            status = text_styles.concatStylesWithSpace(icons.markerBlocked(), text_styles.error(_ms(template, vehData=vehData)))
        else:
            status = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, 16, 16, -2), text_styles.neutral(PERSONAL_MISSIONS.STATUSPANEL_STATUS_SELECTTASK))
        tankwomanQuests = []
        for operation in pm.getAllOperations().itervalues():
            tankwomanQuests.extend(operation.getQuestsByFilter(PersonalMission.needToGetTankWoman).itervalues())

        counterText = ''
        tankwomanVisible = False
        if tankwomanQuests:
            counterText = text_styles.highlightText('x%s' % len(tankwomanQuests))
            tankwomanVisible = True
        self.as_setStatusDataS({'statusText': status,
         'descrText': descr,
         'btnVisible': btnVisible,
         'btnEnabled': btnEnabled,
         'btnLabel': btnLabel,
         'sheetsBlockData': {'freeSheetsIcon': AwardSheetPresenter.getIcon(AwardSheetPresenter.Size.MID),
                             'freeSheetsText': text_styles.main(_ms(PERSONAL_MISSIONS.STATUSPANEL_FREESHEETS, count=text_styles.highlightText(freeSheets))),
                             'pawnedSheetsText': text_styles.main(_ms(PERSONAL_MISSIONS.STATUSPANEL_PAWNEDSHEETS, count=text_styles.highlightText(pawnedSheets))),
                             'tooltipData': {'isSpecial': True,
                                             'specialAlias': TOOLTIPS_CONSTANTS.FREE_SHEET_RETURN if freeSheets or pawnedSheets else TOOLTIPS_CONSTANTS.FREE_SHEET,
                                             'specialArgs': [currentOperation.getCampaignID()]},
                             'popover': PERSONAL_MISSIONS_ALIASES.FREE_SHEET_POPOVER,
                             'popoverData': {'branch': branch}},
         'tankgirlsBlockData': {'counterText': counterText,
                                'visible': tankwomanVisible,
                                'tooltipData': {'isSpecial': True,
                                                'specialAlias': TOOLTIPS_CONSTANTS.PERSONAL_MISSIONS_TANKWOMAN,
                                                'specialArgs': []},
                                'popover': PERSONAL_MISSIONS_ALIASES.TANK_GIRLS_POPOVER},
         'tooltip': None,
         'isQuestInProgress': isQuestInProgress})
        return

    def __updateSideBar(self):
        chains = self.__collectSideBarData()
        self.as_updateSideBarDataS({'chains': chains})
        self.as_setSelectedBranchIndexS(self.getChainID())

    def __getOperationTitle(self):
        currentOperation = self.getOperation()
        chainState = self.__getChainState(self.getChain())
        state = PERSONAL_MISSIONS_ALIASES.OPERATION_UNLOCKED_STATE
        tooltip = {'tooltip': None,
         'isSpecial': False,
         'specialAlias': None,
         'specialArgs': None}
        if not currentOperation.isUnlocked():
            label = text_styles.stats(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_LOCKED)
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_LOCKED_STATE
        elif chainState.isFullCompleted:
            label = text_styles.bonusAppliedText(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_EXCELLENTDONE)
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_FULL_STATE
        elif chainState.isCompleted:
            infoIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIF_FILTERS_INFORMATION_16X16, 16, 16, -2)
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_COMPLETE_STATE
            currentCount = currentOperation.getFreeTokensCount()
            totalCount = currentOperation.getFreeTokensTotalCount()
            if currentCount < totalCount:
                icon = icons.makeImageTag(AwardSheetPresenter.getIcon(AwardSheetPresenter.Size.MID), 24, 24, -22)
                count = str(currentCount)
                total = str(totalCount)
                label = text_styles.stats(_ms(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_DONE, icon=icon, count=count, total=total, infoIcon=infoIcon))
                tooltip.update({'isSpecial': True,
                 'specialAlias': TOOLTIPS_CONSTANTS.FREE_SHEET,
                 'specialArgs': [currentOperation.getCampaignID()]})
            else:
                count = str(len(currentOperation.getFullCompletedQuests()))
                total = str(currentOperation.getQuestsCount())
                label = text_styles.stats(_ms(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_TOMASTER, count=count, total=total, infoIcon=infoIcon))
                tooltip['tooltip'] = TOOLTIPS.PERSONALMISSIONS_OPERATIONTITLE_COMPLETESTATE
        elif chainState.questInProgress:
            if self.getBranch() == PM_BRANCH.PERSONAL_MISSION_2:
                vehData = '  '
                template = PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_INPROGRESS_PM2
            else:
                vehData = ''
                template = PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_INPROGRESS_REGULAR
            vehData += getChainVehRequirements(currentOperation, self.getChainID(), useIcons=True)
            label = text_styles.stats(_ms(template, vehData=vehData))
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_CURRENT_STATE
        elif not chainState.hasVehicle:
            if self.getBranch() == PM_BRANCH.PERSONAL_MISSION_2:
                vehData = '  '
                template = PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_NOVEHICLE_PM2
            else:
                vehData = ''
                template = PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_NOVEHICLE_REGULAR
            vehData += getChainVehRequirements(currentOperation, self.getChainID(), useIcons=True)
            label = text_styles.stats(_ms(template, vehData=vehData))
            state = PERSONAL_MISSIONS_ALIASES.OPERATION_NO_VEHICLE_STATE
        else:
            if self.getBranch() == PM_BRANCH.PERSONAL_MISSION_2:
                vehData = '  '
                template = text_styles.stats(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_UNLOCKED_PM2)
            else:
                vehData = ''
                template = text_styles.stats(PERSONAL_MISSIONS.OPERATIONTITLE_LABEL_UNLOCKED_REGULAR)
            vehData += getChainVehRequirements(currentOperation, self.getChainID(), useIcons=True)
            label = text_styles.stats(_ms(template, vehData=vehData))
        return {'title': text_styles.promoTitle(_ms(PERSONAL_MISSIONS.OPERATIONTITLE_TITLE, title=_ms('#personal_missions:operations/title%d' % currentOperation.getID()))),
         'label': label,
         'state': state,
         'tooltip': tooltip}

    def __getChainState(self, pmQuests):
        hasUnlocked = False
        hasVehicle = False
        isCompleted = True
        isFullCompleted = True
        questInProgress = None
        for q in pmQuests.itervalues():
            if q.isUnlocked():
                hasUnlocked = True
            if q.hasRequiredVehicles():
                hasVehicle = True
            if not q.isCompleted():
                isCompleted = False
            if not q.isFullCompleted():
                isFullCompleted = False
            if q.isInProgress():
                questInProgress = q

        return _ChainState(hasUnlocked, hasVehicle, isCompleted, isFullCompleted, questInProgress)

    @decorators.adisp_process('updating')
    def __pawnMission(self, questInProgress):
        if not questInProgress.isDisabled():
            result = yield quests.PMPawn(questInProgress).request()
            if result and result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __onQuestsUpdated(self, *args):
        if not self.__isPersonalMissionDetailsVisible:
            self.__checkTutorState()
        self.__updateComponents()
        self.__updateMapData()

    def __tryOpenMissionDetails(self):
        if self.__eventID:
            showPersonalMissionDetails(self.__eventID)
        else:
            hidePersonalMissionDetails()

    def __getLastQuest(self):
        activeOperation = self.__PMCache.getIncompleteOperation(self.getBranch())
        completedQuests = activeOperation.getCompletedFinalQuests()
        return findFirst(lambda q: q.getID() not in completedQuests, activeOperation.getFinalQuests().values())

    def __getTutorMultipleState(self):
        return _PTF.MULTIPLE_FAL_SHOWN if self.getBranch() == PM_BRANCH.REGULAR else _PTF.PM2_MULTIPLE_FAL_SHOWN

    def __getTutorSingleState(self):
        return _PTF.ONE_FAL_SHOWN if self.getBranch() == PM_BRANCH.REGULAR else _PTF.PM2_ONE_FAL_SHOWN

    def __checkTutorState(self):
        if self.__callbackID is not None:
            self.__callbackID = None
        storageData = self.__settingsCore.serverSettings.getUIStorage()
        multipleState = self.__getTutorMultipleState()
        singleState = self.__getTutorSingleState()
        if not storageData.get(multipleState):
            activeOperation = self.__PMCache.getIncompleteOperation(self.getBranch())
            chainsCount = len(activeOperation.getQuests())
            falCount = self.__PMCache.getFreeTokensCount(self.getBranch())
            if self.getBranch() == PM_BRANCH.REGULAR:
                falGained = falCount - (storageData.get(_PTF.INITIAL_FAL_COUNT) or 0)
            else:
                falGained = falCount
            finalMissionPawnCost = PM_BRANCH_TO_FINAL_PAWN_COST[self.getBranch()]
            if len(activeOperation.getCompletedFinalQuests()) == chainsCount - 1:
                pawnedFalCount = self.__PMCache.getPawnedTokensCount(self.getBranch())
                if falCount >= finalMissionPawnCost:
                    self.__showTutor(multipleState)
                elif falCount + pawnedFalCount >= finalMissionPawnCost:
                    self.__showTutor(multipleState, showPawned=True)
            elif not storageData.get(singleState) and falGained > 0:
                self.__showTutor(singleState)
        return

    def __navigateTo(self, operationID=None, chainID=None):
        if operationID is not None:
            self.setOperationID(operationID)
        if chainID is not None:
            self.setChainID(chainID)
        self.__updateComponents()
        self.__updateMapData()
        return

    def __resetToIncomplete(self):
        self.__navigateTo(self.__PMCache.getIncompleteOperation(self.getBranch()).getID())

    def __showTutor(self, tutorState, showPawned=False):
        self.__resetToIncomplete()
        if tutorState in (_PTF.ONE_FAL_SHOWN, _PTF.PM2_ONE_FAL_SHOWN):
            self.soundManager.playSound(SOUNDS.ONE_AWARD_LIST_RECEIVED)
            self.as_showFirstAwardSheetObtainedPopupS(True, self._packFirstShowAwardTutorData())
        else:
            self.soundManager.playSound(SOUNDS.FOUR_AWARD_LISTS_RECEIVED)
            self.as_showFourAwardSheetsObtainedPopupS(True, self.__packUseFreeSheetsAwardTutorData(showPawned))
        self.__lastTutorState = tutorState
        self.__settingsCore.serverSettings.saveInUIStorage({self.__lastTutorState: True})

    def _packFirstShowAwardTutorData(self):
        if self.getBranch() == PM_BRANCH.REGULAR:
            res = {'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_AWARD_SHEETS_BRANCH_0_FREE_SHEET_BIG,
             'title': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_REGULAR_TITLE,
             'titleLeft': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_REGULAR_TITLELEFT,
             'descrLeft': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_REGULAR_DESCRLEFT,
             'titleRight': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_REGULAR_TITLERIGHT,
             'descrRight': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_REGULAR_DESCRRIGHT}
        else:
            res = {'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_AWARD_SHEETS_BRANCH_2_FREE_SHEET_BIG,
             'title': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_PM2_TITLE,
             'titleLeft': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_PM2_TITLELEFT,
             'descrLeft': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_PM2_DESCRLEFT,
             'titleRight': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_PM2_TITLERIGHT,
             'descrRight': PERSONAL_MISSIONS.FREESHEETOBTAINEDPOPUP_PM2_DESCRRIGHT}
        return res

    def __packUseFreeSheetsAwardTutorData(self, hasPawned):
        if self.getBranch() == PM_BRANCH.REGULAR:
            iconSource = RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_REGULAR_ORDER_BLANK
            freeSheetsDescr = PERSONAL_MISSIONS.FOURFREESHEETSOBTAINEDPOPUP_REGULAR_DESCR
            freeSheetsPawnedDescr = PERSONAL_MISSIONS.FOURFREESHEETSOBTAINEDPOPUP_REGULAR_PAWNEDDESCR
        else:
            iconSource = RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_PM2_ORDER_BLANK
            freeSheetsDescr = PERSONAL_MISSIONS.FOURFREESHEETSOBTAINEDPOPUP_PM2_DESCR
            freeSheetsPawnedDescr = PERSONAL_MISSIONS.FOURFREESHEETSOBTAINEDPOPUP_PM2_PAWNEDDESCR
        questName = self.__getLastQuest().getShortUserName()
        if hasPawned:
            description = _ms(freeSheetsPawnedDescr, pawnedCount=self.__PMCache.getPawnedTokensCount(self.getBranch()), questName=questName)
        else:
            description = _ms(freeSheetsDescr, questName=questName)
        return {'icon0': {'icon': AwardSheetPresenter.getIcon(AwardSheetPresenter.Size.BIG),
                   'label': 'x' + str(PM_BRANCH_TO_FINAL_PAWN_COST[self.getBranch()])},
         'icon1': {'icon': iconSource,
                   'label': questName},
         'icon2': {'icon': RES_ICONS.MAPS_ICONS_PERSONALMISSIONS_GEAR_BIG,
                   'label': 'x1'},
         'description': description,
         'header': PERSONAL_MISSIONS.FOURFREESHEETSOBTAINEDPOPUP_HEADER}
