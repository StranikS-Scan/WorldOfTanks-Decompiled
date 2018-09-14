# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsTileChainsView.py
import weakref
import operator
from collections import namedtuple
from adisp import async
from gui.server_events.EventsCache import g_eventsCache
from helpers import int2roman
from helpers.i18n import makeString as _ms
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages, makeHtmlString
from gui.server_events import formatters, caches, events_dispatcher as quests_events
from gui.shared import g_itemsCache, event_dispatcher as shared_events
from gui.shared.utils import decorators
from gui.shared.gui_items import Vehicle
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.QUEST_TASK_FILTERS_TYPES import QUEST_TASK_FILTERS_TYPES
from gui.Scaleform.daapi.view.meta.QuestsTileChainsViewMeta import QuestsTileChainsViewMeta
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.shared.formatters import text_styles, icons
from potapov_quests import PQ_BRANCH

class _QuestsFilter(object):
    VEH_TYPE_DEFAULT = -1
    _FILTER_BY_STATE = {QUEST_TASK_FILTERS_TYPES.COMPLETED: lambda q: not q.isFullCompleted() and q.isMainCompleted(isRewardReceived=True),
     QUEST_TASK_FILTERS_TYPES.IN_PROGRESS: lambda q: q.isAvailableToPerform(),
     QUEST_TASK_FILTERS_TYPES.NEED_RECEIVE_AWARD: lambda q: q.needToGetReward(),
     QUEST_TASK_FILTERS_TYPES.UNAVAILABLE: lambda q: not q.isUnlocked()}

    def __init__(self, vehType, questState):
        self.__filters = []
        if vehType != self.VEH_TYPE_DEFAULT:
            vehTypeName = Vehicle.VEHICLE_TYPES_ORDER[vehType]
            self.__filters.append(lambda q: bool({vehTypeName} & q.getVehicleClasses()))
        self.__filters.append(self._FILTER_BY_STATE.get(questState, lambda q: True))

    def __call__(self, quest):
        for f in self.__filters:
            if not f(quest):
                return False

        return True


DetailsBtnInfo = namedtuple('DetailsBtnInfo', ['isApplyBtnVisible',
 'isApplyBtnEnabled',
 'isCancelBtnVisible',
 'btnLabel',
 'btnToolTip',
 'taskDescriptionText'])

def _makeSelectBtn(label = '', tooltip = '', descr = '', enabled = True):
    return DetailsBtnInfo(True, enabled, False, label, tooltip, descr)


def _makeRefuseBtn(label = '', tooltip = '', descr = ''):
    return DetailsBtnInfo(False, False, True, label, tooltip, descr)


def _makeNoBtn(descr = ''):
    return DetailsBtnInfo(False, False, False, '', '', descr)


class _QuestsTileChainsView(QuestsTileChainsViewMeta):
    DEFAULT_FILTERS = {QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM: (-1, QUEST_TASK_FILTERS_TYPES.ALL),
     QUESTS_ALIASES.SEASON_VIEW_TAB_FALLOUT: (-1, QUEST_TASK_FILTERS_TYPES.ALL)}
    _HEADER_ICON_PATH = '../maps/icons/quests/headers/%s.png'

    def __init__(self):
        super(_QuestsTileChainsView, self).__init__()
        self._navInfo = caches.getNavInfo()
        self.__proxy = None
        self.__tile = events_helpers.getPotapovQuestsCache().getTiles()[self._navInfo.selectedPQ.tileID]
        self._tasksProgressLinkage = None
        self._tooltipType = None
        self._showVehicleFilter = True
        self._lockedMessageStrKey = None
        return

    def getTileData(self, vehType, questState):
        self.__updateTileData(vehType, questState)

    def getChainProgress(self):
        self._navInfo.selectPotapovQuest(self.__tile.getID(), -1)
        self.as_updateChainProgressS(self.__makeChainsProgressData())

    def getTaskDetails(self, questID):
        self.as_updateTaskDetailsS(self.__makeQuestDetailsInfo(questID))

    def gotoBack(self):
        try:
            self.__proxy._showSeasonsView(doResetNavInfo=True)
        except:
            LOG_WARNING('Error while getting event window for showing seasons view')
            LOG_CURRENT_EXCEPTION()

    @decorators.process('updating')
    def selectTask(self, questID):
        quest = events_helpers.getPotapovQuestsCache().getQuests()[questID]
        if quest.needToGetReward():
            result = yield self.__getAward(quest)
        else:
            result = yield events_helpers.getPotapovQuestsSelectProcessor()(quest, events_helpers.getPotapovQuestsCache()).request()
        if result and len(result.userMsg):
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def refuseTask(self, questID):
        result = yield events_helpers.getPotapovQuestsRefuseProcessor()(events_helpers.getPotapovQuestsCache().getQuests()[questID], events_helpers.getPotapovQuestsCache()).request()
        if len(result.userMsg):
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def showAwardVehicleInfo(self, vehTypeCompDescr):
        shared_events.showVehicleInfo(int(vehTypeCompDescr))

    def showAwardVehicleInHangar(self, vehTypeCompDescr):
        try:
            vehicle = g_itemsCache.items.getItemByCD(int(vehTypeCompDescr))
            g_currentVehicle.selectVehicle(vehicle.invID)
            shared_events.showHangar()
            self.__proxy.destroy()
        except:
            LOG_WARNING('Error while getting event window to close it')
            LOG_CURRENT_EXCEPTION()

    def _populate(self):
        super(_QuestsTileChainsView, self)._populate()
        g_eventsCache.onProgressUpdated += self._onProgressUpdated
        vehTypeFilter, qStateFilter = self.__getCurrentFilters()
        self.as_setHeaderDataS({'noTasksText': _ms(QUESTS.TILECHAINSVIEW_NOTASKSLABEL_TEXT),
         'header': {'tileID': self.__tile.getID(),
                    'titleText': text_styles.promoSubTitle(_ms(QUESTS.TILECHAINSVIEW_TITLE, name=self.__tile.getUserName() + ' ' + icons.info())),
                    'backBtnText': _ms(QUESTS.TILECHAINSVIEW_BUTTONBACK_TEXT),
                    'backBtnTooltip': TOOLTIPS.PRIVATEQUESTS_BACKBUTTON,
                    'backgroundImagePath': self._HEADER_ICON_PATH % self.__tile.getIconID(),
                    'tasksProgressLabel': text_styles.main(QUESTS.TILECHAINSVIEW_TASKSPROGRESS_TEXT),
                    'tasksProgressLinkage': self._tasksProgressLinkage,
                    'tooltipType': self._tooltipType},
         'filters': {'filtersLabel': _ms(QUESTS.TILECHAINSVIEW_FILTERSLABEL_TEXT),
                     'showVehicleTypeFilterData': self._showVehicleFilter,
                     'vehicleTypeFilterData': formatters._packVehicleTypesFilter(_QuestsFilter.VEH_TYPE_DEFAULT),
                     'taskTypeFilterData': self.__packQuestStatesFilter(),
                     'defVehicleType': vehTypeFilter,
                     'defTaskType': qStateFilter}})
        self._populateTileData()

    def _dispose(self):
        g_eventsCache.onProgressUpdated -= self._onProgressUpdated
        self.__proxy = None
        super(_QuestsTileChainsView, self)._dispose()
        return

    def _onProgressUpdated(self, pqType):
        targetTab = events_helpers.getTabAliasByQuestBranchName(pqType)
        if targetTab == self._navInfo.selectedPQType:
            self._populateTileData()

    def _populateTileData(self):
        itemID = self._navInfo.selectedPQ.questID or -1
        vehType, questState = self.__getCurrentFilters()
        self.__updateTileData(vehType, questState, itemID)

    def _setMainView(self, eventsWindow):
        self.__proxy = weakref.proxy(eventsWindow)

    def _formatChainsProgress(self, *args):
        return NotImplemented

    def _sortChains(self, questsByChains):
        return events_helpers.sortWithQuestType(questsByChains, key=operator.itemgetter(0))

    def __updateTileData(self, vehType, questState, selectItemID = -1):
        self._navInfo.changePQFilters(vehType, questState)
        questsByChains = self.__getQuestsByChains(vehType, questState)
        chains = []
        newSelectedItemID = -1
        for _, chainID, quests in questsByChains:
            completedQuestsCount = len(self.__tile.getQuestsInChainByFilter(chainID, lambda q: q.isCompleted()))
            chain = {'name': text_styles.highTitle(self.__getChainUserName(chainID)),
             'progressText': text_styles.main('%d/%d' % (completedQuestsCount, self.__tile.getChainSize())),
             'tasks': [],
             'enabled': True}
            for quest in sorted(quests, key=operator.methodcaller('getID')):
                stateName, stateIcon = self.__getQuestStatusData(quest)
                questID = quest.getID()
                chain['tasks'].append({'name': text_styles.main(quest.getUserName()),
                 'stateName': stateName,
                 'stateIconPath': stateIcon,
                 'arrowIconPath': RES_ICONS.MAPS_ICONS_LIBRARY_ARROWORANGERIGHTICON8X8,
                 'tooltip': TOOLTIPS.PRIVATEQUESTS_TASKLISTITEM_BODY,
                 'id': questID,
                 'enabled': True})
                if questID == selectItemID:
                    newSelectedItemID = questID

            chains.append(chain)

        self.as_updateTileDataS({'statistics': {'label': text_styles.main(_ms(QUESTS.TILECHAINSVIEW_STATISTICSLABEL_TEXT)),
                        'arrowIconPath': RES_ICONS.MAPS_ICONS_LIBRARY_ARROWORANGERIGHTICON8X8,
                        'tooltip': TOOLTIPS.PRIVATEQUESTS_TASKLISTITEM_BODY},
         'chains': chains})
        if selectItemID == -1:
            self.getChainProgress()
        else:
            self.as_updateChainProgressS(self.__makeChainsProgressData())
        self.as_setSelectedTaskS(newSelectedItemID)

    def __getQuestsByChains(self, vehType, questState):
        questsByChains = {}
        qFilter = _QuestsFilter(vehType, questState)
        for quest in self.__tile.getQuestsByFilter(qFilter).itervalues():
            questsByChains.setdefault(quest.getChainID(), []).append(quest)

        questsByChains = map(lambda (chID, qs): (self.__tile.getChainSortKey(chID), chID, qs), questsByChains.iteritems())
        return self._sortChains(questsByChains)

    @async
    @decorators.process('updating')
    def __getAward(self, quest, callback):
        yield lambda callback: callback(True)
        result = None
        tankman, isMainBonus = quest.getTankmanBonus()
        needToGetTankman = quest.needToGetAddReward() and not isMainBonus or quest.needToGetMainReward() and isMainBonus
        if needToGetTankman and tankman is not None:
            for tmanData in tankman.getTankmenData():
                quests_events.showTankwomanAward(quest.getID(), tmanData)
                break

        else:
            result = yield events_helpers.getPotapovQuestsRewardProcessor(quest).request()
        callback(result)
        return

    def __getCurrentFilters(self):
        return self._navInfo.selectedPQ.filters or self.__getDefaultFilters()

    def __getDefaultFilters(self):
        return self.DEFAULT_FILTERS[self._navInfo.selectedPQType]

    def __makeChainsProgressData(self):
        return {'progressItems': self.__makeChainsProgressItems()}

    def __makeChainsProgressItems(self):
        result = []
        for chainID, quests in self.__tile.getQuests().iteritems():
            totalCount = len(quests)
            completedCount = len(self.__tile.getQuestsInChainByFilter(chainID, lambda q: q.isCompleted()))
            if 0 < completedCount < totalCount:
                completedCountStr = text_styles.main(str(completedCount))
            else:
                completedCountStr = str(completedCount)
            result.append((self.__tile.getChainSortKey(chainID), {'chainID': chainID,
              'value': self._formatChainsProgress(completedCountStr, totalCount, chainID)}))

        return map(operator.itemgetter(1), self._sortChains(result))

    def __makeQuestDetailsInfo(self, questID):
        quest = events_helpers.getPotapovQuestsCache().getQuests()[questID]
        questInfoData = events_helpers.getEventInfoData(quest)
        self._navInfo.selectPotapovQuest(self.__tile.getID(), questID)
        vehMinLevel, vehClasses = quest.getVehMinLevel(), quest.getVehicleClasses()
        if vehMinLevel > 1:
            reqsHeader = text_styles.middleTitle(_ms(QUESTS.QUESTTASKDETAILSVIEW_REQUIREMENTS))
            if quest.getQuestBranch() == PQ_BRANCH.REGULAR:
                reqs = _ms(QUESTS.QUESTTASKDETAILSVIEW_REQUIREMENTS_TEXT, level=int2roman(vehMinLevel), vehType=', '.join([ Vehicle.getTypeShortUserName(vc) for vc in vehClasses ]))
            elif vehMinLevel < 10:
                reqs = _ms(QUESTS.QUESTTASKDETAILSVIEW_REQUIREMENTS_MORE8LVL)
            else:
                reqs = _ms(QUESTS.QUESTTASKDETAILSVIEW_REQUIREMENTS_ONLY10LVL)
        else:
            reqsHeader = reqs = ''
        condition = makeHtmlString('html_templates:lobby/quests/potapov', 'questDetails', ctx={'mainCondHeader': text_styles.middleTitle(_ms(QUESTS.QUESTTASKDETAILSVIEW_MAINCONDITIONS)),
         'mainCond': quest.getUserMainCondition(),
         'addCondHeader': text_styles.middleTitle(_ms(QUESTS.QUESTTASKDETAILSVIEW_ADDITIONALCONDITIONS)),
         'addCond': quest.getUserAddCondition(),
         'requirementsHeader': reqsHeader,
         'requirements': reqs,
         'adviseHeader': text_styles.middleTitle(_ms(QUESTS.QUESTTASKDETAILSVIEW_DESCRIPTION)),
         'advise': quest.getUserAdvice(),
         'descr': quest.getUserDescription()})
        if not quest.isUnlocked():
            btnInfo = _makeSelectBtn(QUESTS.QUESTTASKDETAILSVIEW_BTNLABEL_BEGIN, enabled=False, descr=text_styles.error(icons.notAvailableRed() + ' ' + _ms(self._lockedMessageStrKey)))
        elif quest.needToGetReward():
            btnInfo = _makeSelectBtn(QUESTS.QUESTTASKDETAILSVIEW_BTNLABEL_TAKEAWARD, TOOLTIPS.PRIVATEQUESTS_ACTIONPANNEL_RECEIVETHEAWARD, _ms(QUESTS.QUESTTASKDETAILSVIEW_TASKDESCRIPTION_TAKEAWARD))
        elif quest.isInProgress():
            btnInfo = _makeRefuseBtn(QUESTS.QUESTTASKDETAILSVIEW_BTNLABEL_CANCEL, TOOLTIPS.PRIVATEQUESTS_ACTIONPANNEL_ABORT, _ms(QUESTS.QUESTTASKDETAILSVIEW_TASKDESCRIPTION_INPROGRESS))
        elif quest.isFullCompleted():
            btnInfo = _makeNoBtn(text_styles.success(icons.checkmark() + _ms(QUESTS.QUESTTASKDETAILSVIEW_TASKDESCRIPTION_EXCELLENTDONE)))
        elif quest.isMainCompleted():
            btnInfo = _makeSelectBtn(QUESTS.QUESTTASKDETAILSVIEW_BTNLABEL_REPEAT, TOOLTIPS.PRIVATEQUESTS_ACTIONPANNEL_REPEAT, text_styles.success(icons.checkmark() + _ms(QUESTS.QUESTTASKDETAILSVIEW_TASKDESCRIPTION_DONE)))
        else:
            btnInfo = _makeSelectBtn(QUESTS.QUESTTASKDETAILSVIEW_BTNLABEL_BEGIN, TOOLTIPS.PRIVATEQUESTS_ACTIONPANNEL_PERFORM, _ms(QUESTS.QUESTTASKDETAILSVIEW_TASKDESCRIPTION_AVAILABLE))
        mainAwards, addAwards = questInfoData._getBonuses(events_helpers.getPotapovQuestsCache().getQuests().values())
        result = {'taskID': questID,
         'headerText': text_styles.highTitle(quest.getUserName()),
         'conditionsText': condition,
         'mainAwards': mainAwards,
         'addAwards': addAwards}
        result.update(btnInfo._asdict())
        return result

    def __getQuestStatusData(self, quest):
        if not quest.isUnlocked():
            return (text_styles.standard(_ms(QUESTS.TILECHAINSVIEW_TASKTYPE_UNAVAILABLE_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_NOTAVAILABLEICON)
        elif quest.needToGetReward():
            return (text_styles.alert(_ms(QUESTS.TILECHAINSVIEW_TASKTYPE_AWARDNOTRECEIVED_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON)
        elif quest.isInProgress():
            return (text_styles.neutral(_ms(QUESTS.TILECHAINSVIEW_TASKTYPE_INPROGRESS_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON)
        elif quest.isFullCompleted():
            return (text_styles.statInfo(_ms(QUESTS.TILECHAINSVIEW_TASKTYPE_FULLCOMPLETED_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_CHECKMARK)
        elif quest.isMainCompleted():
            return (text_styles.statInfo(_ms(QUESTS.TILECHAINSVIEW_TASKTYPE_COMPLETED_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_CHECKMARK)
        else:
            return (text_styles.main(''), None)

    def __packQuestStatesFilter(self):
        return [{'label': _ms(QUESTS.TILECHAINSVIEW_TASKTYPEFILTER_ITEMSINPROGRESS_TEXT),
          'data': QUEST_TASK_FILTERS_TYPES.IN_PROGRESS},
         {'label': _ms(QUESTS.TILECHAINSVIEW_TASKTYPEFILTER_COMPLETEDITEMS_TEXT),
          'data': QUEST_TASK_FILTERS_TYPES.COMPLETED},
         {'label': _ms(QUESTS.TILECHAINSVIEW_TASKTYPEFILTER_AWARDSNOTRECEIVEDITEMS_TEXT),
          'data': QUEST_TASK_FILTERS_TYPES.NEED_RECEIVE_AWARD},
         {'label': _ms(QUESTS.TILECHAINSVIEW_TASKTYPEFILTER_ALLITEMS_TEXT),
          'data': QUEST_TASK_FILTERS_TYPES.ALL}]

    def __getChainUserName(self, chainID):
        chainType = self.__tile.getChainMajorTag(chainID)
        if chainType is not None:
            return _ms('#quests:tileChainsView/chainName/%s' % chainType)
        else:
            return ''


class RandomQuestsTileChainsView(_QuestsTileChainsView):

    def __init__(self):
        super(RandomQuestsTileChainsView, self).__init__()
        self._tasksProgressLinkage = QUESTS_ALIASES.QUEST_TASKS_PROGRESS_RANDOM
        self._tooltipType = TOOLTIPS_CONSTANTS.PRIVATE_QUESTS_TILE
        self._lockedMessageStrKey = QUESTS.QUESTTASKDETAILSVIEW_TASKDESCRIPTION_DOPREVTASKS

    def _formatChainsProgress(self, completedCountStr, totalCount, _):
        return text_styles.standard(_ms(QUESTS.QUESTSCHAINPROGRESSVIEW_CHAINPROGRESSCOUNT, count=completedCountStr, total=str(totalCount)))


class FalloutQuestsTileChainsView(_QuestsTileChainsView):

    def __init__(self):
        super(FalloutQuestsTileChainsView, self).__init__()
        self._tasksProgressLinkage = QUESTS_ALIASES.QUEST_TASKS_PROGRESS_FALLOUT
        self._tooltipType = TOOLTIPS_CONSTANTS.PRIVATE_QUESTS_FALLOUT_TILE
        self._showVehicleFilter = False
        self._lockedMessageStrKey = QUESTS.QUESTTASKDETAILSVIEW_FALLOUT_TASKDESCRIPTION_DOPREVTASKS

    def _formatChainsProgress(self, completedCountStr, totalCount, chainID):
        return _ms(QUESTS.QUESTSCHAINPROGRESSVIEW_FALLOUTCHAINPROGRESSCOUNT, name=text_styles.neutral(_ms('#potapov_quests:chain_%s_fallout' % chainID)), count=text_styles.stats(completedCountStr), total=text_styles.standard(str(totalCount)))
