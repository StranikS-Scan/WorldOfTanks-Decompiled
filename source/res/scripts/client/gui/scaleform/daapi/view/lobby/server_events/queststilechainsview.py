# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsTileChainsView.py
import weakref
import operator
from collections import namedtuple
from adisp import async
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from helpers import int2roman
from helpers.i18n import makeString as _ms
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages, makeHtmlString
from gui.server_events import g_eventsCache, formatters, caches, events_dispatcher as quests_events
from gui.shared import g_itemsCache, event_dispatcher as shared_events
from gui.shared.utils import decorators
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.processors import quests as quests_proc
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.QUEST_TASK_FILTERS_TYPES import QUEST_TASK_FILTERS_TYPES
from gui.Scaleform.framework import AppRef
from gui.Scaleform.daapi.view.meta.QuestsTileChainsViewMeta import QuestsTileChainsViewMeta
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.shared.formatters import text_styles, icons

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


class QuestsTileChainsView(QuestsTileChainsViewMeta, AppRef):
    _HEADER_ICON_PATH = '../maps/icons/quests/headers/%s.png'

    def __init__(self):
        super(QuestsTileChainsView, self).__init__()
        self._navInfo = caches.getNavInfo()
        self.__proxy = None
        self.__tile = g_eventsCache.potapov.getTiles()[self._navInfo.potapov.tileID]
        return

    def getTileData(self, vehType, questState):
        self.__updateTileData(vehType, questState)

    def __updateTileData(self, vehType, questState, selectItemID = -1):
        _getText = self.app.utilsManager.textManager.getText
        questsByChains = {}
        qFilter = _QuestsFilter(vehType, questState)
        self._navInfo.changePQFilters(vehType, questState)
        for quest in self.__tile.getQuestsByFilter(qFilter).itervalues():
            questsByChains.setdefault(quest.getChainID(), []).append(quest)

        questsByChains = map(lambda (chID, qs): (chID, self.__tile.getChainVehicleClass(chID), qs), questsByChains.iteritems())
        questsByChains = sorted(questsByChains, key=operator.itemgetter(1), cmp=Vehicle.compareByVehTypeName)
        chains = []
        for chainID, _, quests in questsByChains:
            completedQuestsCount = len(self.__tile.getQuestsInChainByFilter(chainID, lambda q: q.isCompleted()))
            chain = {'name': _getText(TEXT_MANAGER_STYLES.HIGH_TITLE, self.__getChainUserName(chainID)),
             'progressText': _getText(TEXT_MANAGER_STYLES.MAIN_TEXT, '%d/%d' % (completedQuestsCount, self.__tile.getChainSize())),
             'tasks': [],
             'enabled': True}
            for quest in sorted(quests, key=operator.methodcaller('getID')):
                stateName, stateIcon = self.__getQuestStatusData(quest)
                chain['tasks'].append({'name': _getText(TEXT_MANAGER_STYLES.MAIN_TEXT, quest.getUserName()),
                 'stateName': stateName,
                 'stateIconPath': stateIcon,
                 'arrowIconPath': RES_ICONS.MAPS_ICONS_LIBRARY_ARROWORANGERIGHTICON8X8,
                 'tooltip': TOOLTIPS.PRIVATEQUESTS_TASKLISTITEM_BODY,
                 'id': quest.getID(),
                 'enabled': True})

            chains.append(chain)

        self.as_updateTileDataS({'statistics': {'label': _getText(TEXT_MANAGER_STYLES.MAIN_TEXT, _ms(QUESTS.TILECHAINSVIEW_STATISTICSLABEL_TEXT)),
                        'arrowIconPath': RES_ICONS.MAPS_ICONS_LIBRARY_ARROWORANGERIGHTICON8X8,
                        'tooltip': TOOLTIPS.PRIVATEQUESTS_TASKLISTITEM_BODY},
         'chains': chains})
        if selectItemID == -1:
            self.getChainProgress()
        else:
            self.as_updateChainProgressS(self.__makeChainsProgressData())
        self.as_setSelectedTaskS(selectItemID)

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
        quest = g_eventsCache.potapov.getQuests()[questID]
        if quest.needToGetReward():
            result = yield self.__getAward(quest)
        else:
            result = yield quests_proc.PotapovQuestSelect(quest).request()
        if result and len(result.userMsg):
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    @decorators.process('updating')
    def refuseTask(self, questID):
        result = yield quests_proc.PotapovQuestRefuse(g_eventsCache.potapov.getQuests()[questID]).request()
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
            LOG_WARNING('Error while getting event window to slose it')
            LOG_CURRENT_EXCEPTION()

    def _populate(self):
        super(QuestsTileChainsView, self)._populate()
        g_eventsCache.potapov.onProgressUpdated += self._onProgressUpdated
        vehTypeFilter, qStateFilter = self.__getCurrentFilters()
        self.as_setHeaderDataS({'noTasksText': _ms(QUESTS.TILECHAINSVIEW_NOTASKSLABEL_TEXT),
         'header': {'tileID': self.__tile.getID(),
                    'titleText': self.app.utilsManager.textManager.getText(TEXT_MANAGER_STYLES.PROMO_SUB_TITLE, _ms(QUESTS.TILECHAINSVIEW_TITLE, name=self.__tile.getUserName() + ' ' + icons.info())),
                    'backBtnText': _ms(QUESTS.TILECHAINSVIEW_BUTTONBACK_TEXT),
                    'backBtnTooltip': TOOLTIPS.PRIVATEQUESTS_BACKBUTTON,
                    'backgroundImagePath': self._HEADER_ICON_PATH % self.__tile.getIconID()},
         'filters': {'filtersLabel': _ms(QUESTS.TILECHAINSVIEW_FILTERSLABEL_TEXT),
                     'vehicleTypeFilterData': formatters._packVehicleTypesFilter(_QuestsFilter.VEH_TYPE_DEFAULT),
                     'taskTypeFilterData': self.__packQuestStatesFilter(),
                     'defVehicleType': vehTypeFilter,
                     'defTaskType': qStateFilter}})
        self._populateTileData()

    def _dispose(self):
        g_eventsCache.potapov.onProgressUpdated -= self._onProgressUpdated
        self.__proxy = None
        super(QuestsTileChainsView, self)._dispose()
        return

    def _onProgressUpdated(self):
        self._populateTileData()

    def _populateTileData(self):
        if self._navInfo.potapov.questID:
            itemID = self._navInfo.potapov.questID
        else:
            itemID = -1
        vehType, questState = self.__getCurrentFilters()
        self.__updateTileData(vehType, questState, itemID)

    def _setMainView(self, eventsWindow):
        self.__proxy = weakref.proxy(eventsWindow)

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
            result = yield quests_proc.PotapovQuestsGetRegularReward(quest).request()
        callback(result)
        return

    def __getCurrentFilters(self):
        if self._navInfo.potapov.filters is not None:
            return self._navInfo.potapov.filters
        else:
            return (-1, QUEST_TASK_FILTERS_TYPES.ALL)

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
            result.append((self.__tile.getChainVehicleClass(chainID), {'chainID': chainID,
              'value': text_styles.standard(_ms(QUESTS.QUESTSCHAINPROGRESSVIEW_CHAINPROGRESSCOUNT, count=completedCountStr, total=str(totalCount)))}))

        return map(lambda (_, data): data, sorted(result, key=operator.itemgetter(0), cmp=Vehicle.compareByVehTypeName))

    def __makeQuestDetailsInfo(self, questID):
        _getText = self.app.utilsManager.textManager.getText
        quest = g_eventsCache.potapov.getQuests()[questID]
        questInfoData = events_helpers.getEventInfoData(quest)
        self._navInfo.selectPotapovQuest(self.__tile.getID(), questID)
        vehMinLevel, vehClasses = quest.getVehMinLevel(), quest.getVehicleClasses()
        if vehMinLevel > 1:
            reqsHeader = _getText(TEXT_MANAGER_STYLES.MIDDLE_TITLE, _ms(QUESTS.QUESTTASKDETAILSVIEW_REQUIREMENTS))
            reqs = _ms('#quests:QuestTaskDetailsView/requirements/text', level=int2roman(vehMinLevel), vehType=', '.join([ Vehicle.getTypeShortUserName(vc) for vc in vehClasses ]))
        else:
            reqsHeader = reqs = ''
        condition = makeHtmlString('html_templates:lobby/quests/potapov', 'questDetails', ctx={'mainCondHeader': _getText(TEXT_MANAGER_STYLES.MIDDLE_TITLE, _ms(QUESTS.QUESTTASKDETAILSVIEW_MAINCONDITIONS)),
         'mainCond': quest.getUserMainCondition(),
         'addCondHeader': _getText(TEXT_MANAGER_STYLES.MIDDLE_TITLE, _ms(QUESTS.QUESTTASKDETAILSVIEW_ADDITIONALCONDITIONS)),
         'addCond': quest.getUserAddCondition(),
         'requirementsHeader': reqsHeader,
         'requirements': reqs,
         'adviseHeader': _getText(TEXT_MANAGER_STYLES.MIDDLE_TITLE, _ms(QUESTS.QUESTTASKDETAILSVIEW_DESCRIPTION)),
         'advise': quest.getUserAdvice(),
         'descr': quest.getUserDescription()})
        if not quest.isUnlocked():
            btnInfo = _makeSelectBtn(QUESTS.QUESTTASKDETAILSVIEW_BTNLABEL_BEGIN, enabled=False, descr=text_styles.error(icons.notAvailableRed() + ' ' + _ms(QUESTS.QUESTTASKDETAILSVIEW_TASKDESCRIPTION_DOPREVTASKS)))
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
        mainAwards, addAwards = questInfoData._getBonuses(g_eventsCache.potapov.getQuests().values())
        result = {'taskID': questID,
         'headerText': _getText(TEXT_MANAGER_STYLES.HIGH_TITLE, quest.getUserName()),
         'conditionsText': condition,
         'mainAwards': mainAwards,
         'addAwards': addAwards}
        result.update(btnInfo._asdict())
        return result

    def __getQuestStatusData(self, quest):
        _getText = self.app.utilsManager.textManager.getText
        if not quest.isUnlocked():
            return (_getText(TEXT_MANAGER_STYLES.STANDARD_TEXT, _ms(QUESTS.TILECHAINSVIEW_TASKTYPE_UNAVAILABLE_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_NOTAVAILABLEICON)
        elif quest.needToGetReward():
            return (_getText(TEXT_MANAGER_STYLES.ALERT_TEXT, _ms(QUESTS.TILECHAINSVIEW_TASKTYPE_AWARDNOTRECEIVED_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON)
        elif quest.isInProgress():
            return (_getText(TEXT_MANAGER_STYLES.NEUTRAL_TEXT, _ms(QUESTS.TILECHAINSVIEW_TASKTYPE_INPROGRESS_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON)
        elif quest.isFullCompleted():
            return (_getText(TEXT_MANAGER_STYLES.STATUS_INFO_TEXT, _ms(QUESTS.TILECHAINSVIEW_TASKTYPE_FULLCOMPLETED_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_CHECKMARK)
        elif quest.isMainCompleted():
            return (_getText(TEXT_MANAGER_STYLES.STATUS_INFO_TEXT, _ms(QUESTS.TILECHAINSVIEW_TASKTYPE_COMPLETED_TEXT)), RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_CHECKMARK)
        else:
            return (_getText(TEXT_MANAGER_STYLES.MAIN_TEXT, ''), None)

    def __packQuestStatesFilter(self):
        return [{'label': _ms(QUESTS.TILECHAINSVIEW_TASKTYPEFILTER_ITEMSINPROGRESS_TEXT),
          'data': QUEST_TASK_FILTERS_TYPES.IN_PROGRESS},
         {'label': _ms(QUESTS.TILECHAINSVIEW_TASKTYPEFILTER_COMPLETEDITEMS_TEXT),
          'data': QUEST_TASK_FILTERS_TYPES.COMPLETED},
         {'label': _ms(QUESTS.TILECHAINSVIEW_TASKTYPEFILTER_AWARDSNOTRECEIVEDITEMS_TEXT),
          'data': QUEST_TASK_FILTERS_TYPES.NEED_RECEIVE_AWARD},
         {'label': _ms(QUESTS.TILECHAINSVIEW_TASKTYPEFILTER_ALLITEMS_TEXT),
          'data': QUEST_TASK_FILTERS_TYPES.ALL}]

    def __getIconText(self, textStyle, textAlias, iconPath = None, width = 16, height = 16, vSpace = -3, hSpace = 0):
        ctx = {}
        if iconPath is not None:
            ctx['icon'] = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(iconPath, width, height, vSpace, hSpace))
        return self.app.utilsManager.textManager.getText(textStyle, _ms(textAlias, **ctx))

    def __getChainUserName(self, chainID):
        vehType = self.__tile.getChainVehicleClass(chainID)
        if vehType is not None:
            return _ms('#quests:tileChainsView/chainName/%s' % vehType)
        else:
            return ''
