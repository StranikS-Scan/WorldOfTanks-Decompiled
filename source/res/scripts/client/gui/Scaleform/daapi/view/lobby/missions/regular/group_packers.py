# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/group_packers.py
import locale
import logging
import time
import weakref
from collections import namedtuple, defaultdict, OrderedDict
import BigWorld
from CurrentVehicle import g_currentVehicle
from Event import EventManager, Event
from constants import EVENT_TYPE, PREMIUM_TYPE
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.view.lobby.event_boards.event_helpers import EventInfo, EventHeader
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatErrorTextWithIcon
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import MarathonAwardComposer
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.LINKEDSET import LINKEDSET
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.MOTIVATION_QUESTS import MOTIVATION_QUESTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.event_boards.settings import isGroupMinimized, expandGroup
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.server_events import settings
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.cond_formatters.tokens import TokensMarathonFormatter
from gui.server_events.event_items import DEFAULTS_GROUPS
from gui.server_events.events_helpers import hasAtLeastOneAvailableQuest, isAllQuestsCompleted, isLinkedSet, getLocalizedQuestNameForLinkedSetQuest, getLocalizedQuestDescForLinkedSetQuest, getLinkedSetMissionIDFromQuest, isPremium, premMissionsSortFunc, isPremiumQuestsEnable, getPremiumGroup
from gui.server_events.events_helpers import missionsSortFunc
from gui.server_events.formatters import DECORATION_SIZES
from gui.shared.formatters import text_styles
from gui.shared.formatters.icons import makeImageTag
from helpers import dependency, time_utils, getLanguageCode
from helpers.i18n import makeString as _ms
from skeletons.gui.linkedset import ILinkedSetController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
_EventsBlockData = namedtuple('EventsBlockData', 'filteredCount totalCount blockData')
_MAIN_QUEST_AWARDS_COUNT = 6
_BIG_TOKENS_TRESHOLD = 2
awardsFormatters = MarathonAwardComposer(_MAIN_QUEST_AWARDS_COUNT)
tokenMarathonsCondFormatter = TokensMarathonFormatter()
_logger = logging.getLogger(__name__)

class GuiGroupBlockID(object):
    BASE = 'base'
    UNGROUPED_BLOCK = 'ungroupedBlock'
    REGULAR_GROUPED_BLOCK = 'regularGroupedBlock'
    MOTIVE_QUESTS_BLOCK = 'motiveQuestsBlock'
    MARATHON_GROUPED_BLOCK = 'marathonGroupedBlock'
    ELEN_QUEST_BLOCK = 'elenQuest'
    LINKEDSET_QUESTS_BLOCK = 'linkedSet'
    PREMIUM_QUESTS_BLOCK = 'premiumQuests'
    ORDER = (BASE,
     PREMIUM_QUESTS_BLOCK,
     UNGROUPED_BLOCK,
     REGULAR_GROUPED_BLOCK,
     MOTIVE_QUESTS_BLOCK,
     MARATHON_GROUPED_BLOCK,
     ELEN_QUEST_BLOCK,
     LINKEDSET_QUESTS_BLOCK)
    ORDER_INDICES = dict(((n, i) for i, n in enumerate(ORDER)))

    @classmethod
    def getBlockPriority(cls, blockID):
        return cls.ORDER_INDICES.get(blockID, 0)


def getGroupPackerByContextID(contextID, proxy):
    if contextID == DEFAULTS_GROUPS.UNGROUPED_QUESTS:
        return _UngroupedQuestsBlockInfo()
    elif contextID == DEFAULTS_GROUPS.MOTIVE_QUESTS:
        return _MotiveQuestsBlockInfo()
    else:
        if contextID is not None and contextID != DEFAULTS_GROUPS.FOR_CURRENT_VEHICLE:
            groups = proxy.getGroups()
            group = groups.get(contextID)
            if group:
                if group.isMarathon():
                    return _MissionsGroupQuestsBlockInfo(group)
                if group.isLinkedSet():
                    return _LinkedSetQuestsBlockInfo()
                if group.isPremium():
                    return _PremiumGroupedQuestsBlockInfo()
                return _GroupedEventsBlockInfo(group)
        return


def _getMissionsCountLabel(completed, total):
    completed = text_styles.stats(completed)
    total = text_styles.standard(total)
    return text_styles.concatStylesToSingleLine(text_styles.standard(QUESTS.MISSIONS_TAB_CATEGORY_HEADER_PERFORMEDTASKS), text_styles.disabled('  %s / %s' % (completed, total)))


class _EventsBlockBuilder(object):

    def __init__(self):
        self._cache = defaultdict(dict)
        self.__initDefaultBlocks()

    def init(self):
        self.invalidateBlocks()

    def clear(self):
        self.__clearDefaultBlocks()
        self._cache.clear()
        self.__cachedSortedDataBlocks = None
        return

    def getBlocksData(self, srvEvents, filterFunc):
        result = []
        for groupInfo in self.__getBlocksInfos():
            blockData = groupInfo.buildEventsBlockData(srvEvents, filterFunc)
            if blockData is not None:
                result.append(blockData)

        return result

    def getSuitableEvents(self):
        result = []
        for groupInfo in self.__getBlocksInfos():
            result.extend(groupInfo.getSuitableEvents())

        return result

    def markVisited(self):
        for groupInfo in self.__getBlocksInfos():
            groupInfo.markVisited()

    def getBlocksAdvisableEvents(self, events):
        result = []
        for groupInfo in self.__getBlocksInfos():
            result.extend(groupInfo.getBlockAdvisableEvents(events))

        return result

    def invalidateBlocks(self):
        for groupInfo in self.__getBlocksInfos():
            groupInfo.invalidate()

    def _getDefaultBlocks(self):
        return []

    def __initDefaultBlocks(self):
        defaults = self._cache['defaults']
        for blockInfo in self._getDefaultBlocks():
            defaults[blockInfo.getEventsBlockID()] = blockInfo

    def __clearDefaultBlocks(self):
        defaults = self._cache['defaults']
        for gInfo in defaults.itervalues():
            gInfo.clear()

        defaults.clear()

    def __getBlocksInfos(self):
        result = []
        resultExtend = result.extend
        for group in self._cache.itervalues():
            resultExtend(group.values())

        return sorted(result, key=lambda blockInfo: blockInfo.getSortPriority(), reverse=True)


class VehicleGroupBuilder(_EventsBlockBuilder):

    def __init__(self):
        super(VehicleGroupBuilder, self).__init__()
        self.__em = EventManager()
        self.onBlocksDataChanged = Event(self.__em)

    def init(self):
        super(VehicleGroupBuilder, self).init()
        g_currentVehicle.onChanged += self.__onVehicleChanged

    def clear(self):
        super(VehicleGroupBuilder, self).init()
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self.__em.clear()

    def _getDefaultBlocks(self):
        return [_VehicleQuestsBlockInfo()]

    def __onVehicleChanged(self):
        self.onBlocksDataChanged()


class GroupedEventsBlocksBuilder(_EventsBlockBuilder):
    eventsCache = dependency.descriptor(IEventsCache)

    def clear(self):
        cachedGroups = self._cache['groupedEvents']
        for blockInfo in cachedGroups.itervalues():
            blockInfo.clear()

        cachedGroups.clear()
        super(GroupedEventsBlocksBuilder, self).clear()

    def invalidateBlocks(self):
        super(GroupedEventsBlocksBuilder, self).invalidateBlocks()
        newEventsGroups = self._getEventsGroups()
        cachedGroups = self._cache['groupedEvents']
        newGroupsKeys = set(newEventsGroups.keys())
        oldGroupsKeys = set(cachedGroups.keys())
        invalidGroupsIds = oldGroupsKeys.intersection(newGroupsKeys)
        newGroupsIds = newGroupsKeys.difference(invalidGroupsIds)
        lostGroupsIds = oldGroupsKeys.difference(invalidGroupsIds)
        for gID in lostGroupsIds:
            cachedGroups.pop(gID).clear()

        for gID in invalidGroupsIds:
            cachedGroups[gID].clear()
            cachedGroups[gID] = self._createGroupedEventsBlock(newEventsGroups[gID])

        for gID in newGroupsIds:
            cachedGroups[gID] = self._createGroupedEventsBlock(newEventsGroups[gID])

    def _createGroupedEventsBlock(self, group):
        raise NotImplementedError

    def _getEventsGroups(self):
        raise NotImplementedError


class MissionsGroupsBuilder(GroupedEventsBlocksBuilder):

    def _createGroupedEventsBlock(self, group):
        return _MissionsGroupQuestsBlockInfo(group)

    def _getEventsGroups(self):
        return self.eventsCache.getGroups(filterFunc=lambda g: g.isMarathon())


class MarathonsDumbBuilder(GroupedEventsBlocksBuilder):

    def _createGroupedEventsBlock(self, group):
        return []

    def _getEventsGroups(self):
        return {}


class QuestsGroupsBuilder(GroupedEventsBlocksBuilder):
    linkedSet = dependency.descriptor(ILinkedSetController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(QuestsGroupsBuilder, self).__init__()
        self.__wasLinkedSetShowed = False

    def invalidateBlocks(self):
        super(QuestsGroupsBuilder, self).invalidateBlocks()
        if self.linkedSet.isLinkedSetEnabled() and (self.__wasLinkedSetShowed or not self.linkedSet.isLinkedSetFinished()):
            self._cache['groupedEvents']['linkedset'] = _LinkedSetQuestsBlockInfo()
            self.__wasLinkedSetShowed = True
        group = getPremiumGroup()
        if isPremiumQuestsEnable() and 'premium' not in self._cache['groupedEvents'].iterkeys() and group:
            self._cache['groupedEvents']['premium'] = _PremiumGroupedQuestsBlockInfo()

    def _getDefaultBlocks(self):
        return [_MotiveQuestsBlockInfo(), _UngroupedQuestsBlockInfo()]

    def _createGroupedEventsBlock(self, group):
        return _GroupedQuestsBlockInfo(group)

    def _getEventsGroups(self):
        return self.eventsCache.getGroups(filterFunc=lambda g: g.isRegularQuest())


class ElenGroupsBuilder(_EventsBlockBuilder):

    def __init__(self):
        super(ElenGroupsBuilder, self).__init__()
        self._eventsData = None
        self._playerData = None
        self._myEventsTop = None
        self._currentEventID = None
        return

    def invalidateBlocks(self):
        super(ElenGroupsBuilder, self).invalidateBlocks()
        cachedGroups = OrderedDict()
        self._cache['elenEvents'] = cachedGroups
        events = self._eventsData.getEvents() if self._eventsData is not None else None
        if events is None:
            return
        else:
            for event in events:
                isChosen = self._currentEventID == event.getEventID()
                cachedGroups[event.getEventID()] = _ElenBlockInfo(event, self._myEventsTop, self._playerData, isChosen)

            return

    def setEventsData(self, eventsData, playerData, myEventsTop, currentEventID):
        self._eventsData = weakref.proxy(eventsData)
        self._playerData = weakref.proxy(playerData)
        self._myEventsTop = weakref.proxy(myEventsTop)
        self._currentEventID = currentEventID
        self.invalidateBlocks()


class _EventsBlockInfo(object):
    blockType = GuiGroupBlockID.BASE

    def __init__(self, headerLinkage='', bodyLinkage=''):
        self._headerLinkage = headerLinkage
        self._bodyLinkage = bodyLinkage
        self._events = ()
        self._suitableEvents = ()
        self._cachedInfo = {}

    def getSuitableEvents(self):
        return self._suitableEvents

    def invalidate(self):
        self._cachedInfo.clear()

    def getSortPriority(self):
        return (self._getGuiBlockPriority(), self._getAdvancePriority())

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.findEvents(srvEvents)
        self._events = filter(filterFunc, self._suitableEvents)
        return _EventsBlockData(len(self._events), len(self._suitableEvents), self._getVO())

    def getBlockAdvisableEvents(self, srvEvents):
        return self.findEvents(srvEvents)

    def markVisited(self):
        settings.visitEventsGUI(self._suitableEvents)

    def clear(self):
        self._events = ()
        self._suitableEvents = ()
        self._cachedInfo.clear()

    def getEventsBlockID(self):
        raise NotImplementedError

    def findEvents(self, srvEvents):
        return sorted(self._findEvents(srvEvents), cmp=missionsSortFunc, reverse=True)

    def _getGuiBlockPriority(self):
        return GuiGroupBlockID.getBlockPriority(self.blockType)

    def _getAdvancePriority(self):
        pass

    def _findEvents(self, srvEvents):
        raise NotImplementedError

    def _getVO(self):
        vo = self._getGuiLinkages()
        vo.update({'blockId': self.getEventsBlockID(),
         'headerData': self._getHeaderData(),
         'bodyData': self._getBodyData()})
        return vo

    def _getMainQuest(self):
        return None

    def _getGuiLinkages(self):
        return {'headerLinkage': self._headerLinkage,
         'bodyLinkage': self._bodyLinkage}

    def _getBodyData(self):
        cardsList = []
        for e in self._events:
            eventID = e.getID()
            if eventID in self._cachedInfo:
                missionData = self._cachedInfo[eventID]
            else:
                missionData = getMissionInfoData(e)
                self._cachedInfo[eventID] = missionData
            cardsList.append(missionData.getInfo())

        return {'missions': cardsList,
         'dummy': {'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
                   'htmlText': text_styles.alert(_ms(QUESTS.MISSIONS_NOTASKSBODY_DUMMY_TEXT)),
                   'alignCenter': False,
                   'btnVisible': True,
                   'btnLabel': QUESTS.MISSIONS_NOTASKSBODY_DUMMY_BTNLABEL,
                   'btnTooltip': '',
                   'btnEvent': 'ResetFilterEvent',
                   'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK}} if not cardsList and self._suitableEvents else {'missions': cardsList}

    def _getHeaderData(self):
        raise NotImplementedError


class _CollapsableEventsBlockInfo(_EventsBlockInfo):

    def _getVO(self):
        data = super(_CollapsableEventsBlockInfo, self)._getVO()
        data.update({'isCollapsed': settings.isGroupMinimized(self.getEventsBlockID())})
        return data


class _GroupedEventsBlockInfo(_CollapsableEventsBlockInfo):
    eventsCache = dependency.descriptor(IEventsCache)
    blockType = GuiGroupBlockID.REGULAR_GROUPED_BLOCK

    def __init__(self, group, headerLinkage='', bodyLinkage=''):
        super(_GroupedEventsBlockInfo, self).__init__(headerLinkage, bodyLinkage)
        self._group = group
        self._filterEnable = True

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.findEvents(srvEvents)
        self._events = filter(filterFunc, self._suitableEvents) if self._filterEnable else self._suitableEvents
        return None if not self._suitableEvents else _EventsBlockData(len(self._events), len(self._suitableEvents), self._getVO())

    def clear(self):
        self._group = None
        return

    def getEventsBlockID(self):
        return self._group.getID()

    def getTitle(self):
        return text_styles.promoTitle(self._group.getUserName())

    def getTitleBlock(self):
        linkedActionID = self._group.getLinkedAction(self.eventsCache.getActions())
        return {'title': self.getTitle(),
         'action': {'actionID': linkedActionID,
                    'label': text_styles.tutorial(QUESTS.MISSIONS_TAB_MARATHONS_HEADER_TITLE_ACTION),
                    'visible': linkedActionID is not None}}

    def _findEvents(self, srvEvents):
        return self._group.getGroupContent(srvEvents)

    def _getAdvancePriority(self):
        return 0 if not self._group else self._group.getPriority()

    def _getDescrBlock(self):
        minStartTime = min([ q.getStartTime() for q in self._suitableEvents ])
        maxFinishTime = max([ q.getFinishTime() for q in self._suitableEvents ])
        return {'period': text_styles.middleTitle(_ms(QUESTS.MISSIONS_TAB_MARATHONS_HEADER_PERIOD, startDate=BigWorld.wg_getLongDateFormat(minStartTime), endDate=BigWorld.wg_getLongDateFormat(maxFinishTime))),
         'isMultiline': True,
         'hasCalendarIcon': True}

    def _getHeaderData(self):
        return {'titleBlock': self.getTitleBlock(),
         'descBlock': self._getDescrBlock()}


class _GroupedQuestsBlockInfo(_GroupedEventsBlockInfo):
    blockType = GuiGroupBlockID.REGULAR_GROUPED_BLOCK

    def __init__(self, group, headerLinkage=QUESTS_ALIASES.MISSION_PACK_CATEGORY_HEADER_LINKAGE, bodyLinkage=QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE):
        super(_GroupedQuestsBlockInfo, self).__init__(group, headerLinkage, bodyLinkage)
        self._totalQuestsCount = 0
        self._completedQuestsCount = 0

    def _findEvents(self, srvEvents):
        result = self._group.getGroupContent(srvEvents)
        self._completedQuestsCount = 0
        for quest in result:
            if quest.isCompleted():
                self._completedQuestsCount += 1

        self._totalQuestsCount = len(result)
        return result

    def _getDescrBlock(self):
        data = super(_GroupedQuestsBlockInfo, self)._getDescrBlock()
        data.update({'isMultiline': False})
        data.update({'descr': _getMissionsCountLabel(self._completedQuestsCount, self._totalQuestsCount)})
        return data


class _MissionsGroupQuestsBlockInfo(_GroupedEventsBlockInfo):
    blockType = GuiGroupBlockID.MARATHON_GROUPED_BLOCK

    def __init__(self, group):
        super(_MissionsGroupQuestsBlockInfo, self).__init__(group, headerLinkage=QUESTS_ALIASES.MISSION_PACK_MARATHON_HEADER_LINKAGE, bodyLinkage=QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE)
        self._mainQuest = None
        return

    def clear(self):
        self._mainQuest = None
        super(_MissionsGroupQuestsBlockInfo, self).clear()
        return

    def _findEvents(self, srvEvents):
        suitableEvents = self._group.getGroupContent(srvEvents)
        self._mainQuest = self._group.getMainQuest(suitableEvents)
        if self._mainQuest:
            suitableEvents.remove(self._mainQuest)
        return suitableEvents

    def _getMainQuest(self):
        return self._mainQuest

    def _getDescrBlock(self):
        data = super(_MissionsGroupQuestsBlockInfo, self)._getDescrBlock()
        if self._mainQuest:
            data.update({'descr': text_styles.main(self._mainQuest.getDescription())})
        return data

    def _getHeaderData(self):
        tokensData = []
        awardsData = []
        awardImgTooltip = None
        awardImgSource = ''
        prefetcher = self.eventsCache.prefetcher
        if self._mainQuest:
            tokensData = tokenMarathonsCondFormatter.format(self._mainQuest)
            uiDecoration = self._mainQuest.getIconID()
            if uiDecoration:
                awardImgSource = prefetcher.getMissionDecoration(uiDecoration, DECORATION_SIZES.BONUS)
                awardImgTooltip = {'isSpecial': True,
                 'specialAlias': TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS,
                 'specialArgs': awardsFormatters.getShortBonusesData(self._mainQuest.getBonuses())}
            else:
                awardsData = awardsFormatters.getFormattedBonuses(self._mainQuest.getBonuses(), AWARDS_SIZES.BIG)
        return {'uiDecoration': prefetcher.getMissionDecoration(self._group.getIconID(), DECORATION_SIZES.MARATHON),
         'titleBlock': self.getTitleBlock(),
         'descBlock': self._getDescrBlock(),
         'conditionBlock': {'title': text_styles.middleTitle(QUESTS.MISSIONS_TAB_MARATHONS_HEADER_CONDITION),
                            'tokensData': tokensData},
         'awardBlock': {'title': text_styles.middleTitle(QUESTS.MISSIONS_TAB_MARATHONS_HEADER_AWARD),
                        'awardsData': awardsData,
                        'awardImgSource': awardImgSource,
                        'awardImgTooltip': awardImgTooltip}}


class _UngroupedQuestsBlockInfo(_CollapsableEventsBlockInfo):
    blockType = GuiGroupBlockID.UNGROUPED_BLOCK

    def __init__(self):
        super(_UngroupedQuestsBlockInfo, self).__init__(headerLinkage=QUESTS_ALIASES.MISSION_PACK_CATEGORY_HEADER_LINKAGE, bodyLinkage=QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE)
        self.__totalQuestsCount = 0
        self.__completedQuestsCount = 0

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.findEvents(srvEvents)
        self._events = filter(filterFunc, self._suitableEvents)
        return None if not self._suitableEvents else _EventsBlockData(len(self._events), len(self._suitableEvents), self._getVO())

    def getEventsBlockID(self):
        return DEFAULTS_GROUPS.UNGROUPED_QUESTS

    def getTitle(self):
        return text_styles.promoTitle(QUESTS.QUESTS_TITLE_UNGOUPEDQUESTS)

    def getTitleBlock(self):
        return {'title': self.getTitle()}

    def getDetailedTitle(self):
        raise SoftException('This method should not be reached in this context')

    def _findEvents(self, srvEvents):
        suitabaleQuests = [ q for q in srvEvents.itervalues() if q.getGroupID() == DEFAULTS_GROUPS.UNGROUPED_QUESTS and q.getType() != EVENT_TYPE.MOTIVE_QUEST ]
        self.__totalQuestsCount = len(suitabaleQuests)
        self.__completedQuestsCount = len([ q for q in suitabaleQuests if q.isCompleted() ])
        return suitabaleQuests

    def _getHeaderData(self):
        return {'titleBlock': self.getTitleBlock(),
         'descBlock': self._getDescrBlock()}

    def _getDescrBlock(self):
        return {'descr': _getMissionsCountLabel(self.__completedQuestsCount, self.__totalQuestsCount),
         'period': text_styles.middleTitle(QUESTS.MISSIONS_GROUP_OTHERS_LABEL),
         'hasCalendarIcon': False,
         'isMultiline': False}


class _MotiveQuestsBlockInfo(_CollapsableEventsBlockInfo):
    blockType = GuiGroupBlockID.MOTIVE_QUESTS_BLOCK

    def __init__(self):
        super(_MotiveQuestsBlockInfo, self).__init__(headerLinkage=QUESTS_ALIASES.MISSION_PACK_CATEGORY_HEADER_LINKAGE, bodyLinkage=QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE)

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.findEvents(srvEvents)
        self._events = filter(filterFunc, self._suitableEvents)
        return None if not self._suitableEvents else _EventsBlockData(len(self._events), len(self._suitableEvents), self._getVO())

    def getEventsBlockID(self):
        return DEFAULTS_GROUPS.MOTIVE_QUESTS

    def getTitle(self):
        return text_styles.promoTitle(MOTIVATION_QUESTS.GROUP)

    def getTitleBlock(self):
        return {'title': self.getTitle()}

    def _findEvents(self, srvEvents):
        suitabaleQuests = [ q for q in srvEvents.itervalues() if q.getType() == EVENT_TYPE.MOTIVE_QUEST and not q.isCompleted() and q.isAvailable()[0] ]
        return suitabaleQuests

    def _getHeaderData(self):
        return {'titleBlock': self.getTitleBlock(),
         'descBlock': self._getDescrBlock()}

    def _getDescrBlock(self):
        return {'descr': '',
         'period': text_styles.middleTitle(QUESTS.MISSIONS_GROUP_MOTIVE_LABEL),
         'hasCalendarIcon': False,
         'isMultiline': False}


class _VehicleQuestsBlockInfo(_EventsBlockInfo):

    def __init__(self):
        super(_VehicleQuestsBlockInfo, self).__init__(headerLinkage=QUESTS_ALIASES.MISSION_PACK_CURRENT_VEHICLE_HEADER_LINKAGE, bodyLinkage=QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE)

    def getEventsBlockID(self):
        return DEFAULTS_GROUPS.FOR_CURRENT_VEHICLE

    def getTitleBlock(self):
        tankInfo = ''
        tankType = ''
        if g_currentVehicle.isPresent():
            item = g_currentVehicle.item
            tankInfo = text_styles.concatStylesToMultiLine(text_styles.promoSubTitle(item.userName), text_styles.stats(MENU.levels_roman(item.level)))
            tankType = '../maps/icons/vehicleTypes/big/%s.png' % item.type
        return {'title': self.getTitle(),
         'tankType': tankType,
         'tankInfo': tankInfo}

    def _findEvents(self, srvEvents):
        return filter(self.__applyFilter, srvEvents.itervalues())

    def getTitle(self):
        return text_styles.promoTitle(QUESTS.QUESTS_TITLE_CURRENTLYAVAILABLE)

    def _getHeaderData(self):
        return {'titleBlock': self.getTitleBlock()}

    def __applyFilter(self, quest):
        forbiddenQuestConditions = [lambda q: q.getType() in (EVENT_TYPE.TOKEN_QUEST,), lambda q: not q.getFinishTimeLeft(), lambda q: isLinkedSet(q.getGroupID()) or isPremium(q.getGroupID())]
        if any((isForbidden(quest) for isForbidden in forbiddenQuestConditions)):
            return False
        if not g_currentVehicle.isPresent():
            return False
        return quest.isValidVehicleCondition(g_currentVehicle.item) if quest.getType() != EVENT_TYPE.MOTIVE_QUEST else quest.isValidVehicleCondition(g_currentVehicle.item) and not quest.isCompleted() and quest.isAvailable()[0]


class _ElenBlockInfo(_EventsBlockInfo):
    blockType = GuiGroupBlockID.ELEN_QUEST_BLOCK

    def __init__(self, event, eventsTop, playerData, isChosen):
        super(_ElenBlockInfo, self).__init__(headerLinkage=QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_HEADER_LINKAGE, bodyLinkage=QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_BODY_LINKAGE)
        self._event = event
        self._eventsTop = eventsTop
        self._playerData = playerData
        self._isChosen = isChosen

    def getEventsBlockID(self):
        return self._event.getEventID()

    def getTitleBlock(self):
        return {'title': self._event.getName()}

    def buildEventsBlockData(self, srvEvents, filterFunc):
        return _EventsBlockData(1, 1, self._getVO())

    def _findEvents(self, srvEvents):
        raise SoftException('This method should not be reached in this context')

    def _getHeaderData(self):
        eventInfo = EventHeader(self._event, self._playerData)
        data = {'titleBlock': self.getTitleBlock()}
        data.update(eventInfo.getInfo())
        return data

    def _getVO(self):
        data = super(_ElenBlockInfo, self)._getVO()
        minimized = isGroupMinimized(self._event)
        if self._isChosen and minimized:
            expandGroup(self._event, True)
            minimized = False
        data.update({'isCollapsed': minimized})
        data['bgAlpha'] = 1
        return data

    def _getBodyData(self):
        event = EventInfo(self._event, self._playerData, self._eventsTop)
        top = event.getTopInfo()
        result = {'missions': top,
         'taskBlock': event.getTaskInfo(),
         'conditionBlock': event.getConditionInfo(),
         'awardBlock': event.getAwardInfo(),
         'isEventBegan': self._event.isStarted(),
         'uiDecoration': self._event.getKeyArtBig(),
         'popoverAlias': event.getPopoverAlias(),
         'eventID': self._event.getEventID()}
        result.update(event.getServerData())
        result.update(event.getStatusData())
        if top:
            result.update({'taskBlock': event.getTaskInfo(),
             'conditionBlock': event.getConditionInfo(),
             'awardBlock': event.getAwardInfo()})
        return result


class _LinkedSetQuestsBlockInfo(_EventsBlockInfo):
    eventsCache = dependency.descriptor(IEventsCache)
    linkedSet = dependency.descriptor(ILinkedSetController)
    blockType = GuiGroupBlockID.LINKEDSET_QUESTS_BLOCK

    def __init__(self):
        super(_LinkedSetQuestsBlockInfo, self).__init__(headerLinkage=QUESTS_ALIASES.MISSIONS_LINKED_SET_HEADER_LINKAGE, bodyLinkage=QUESTS_ALIASES.MISSIONS_LINKED_SET_BODY_LINKAGE)
        self._questMissions = []
        self.mainQuest = None
        return

    @property
    def questMissions(self):
        return self._questMissions

    def getEventsBlockID(self):
        return DEFAULTS_GROUPS.LINKEDSET_QUESTS

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.linkedSet.getLinkedSetQuests().values()
        self._events = self._suitableEvents
        self._updateLinkedSetMissions()
        return _EventsBlockData(len(self._suitableEvents), len(self._suitableEvents), self._getVO())

    def getTitleBlock(self):
        return {'title': _ms(LINKEDSET.LINKEDSET_GROUP_TITLE)}

    def isLinkedSetCompleted(self):
        return self.getTotalMissionsCount() == self.getCompletedMissionsCount()

    def getTotalMissionsCount(self):
        return len(self._questMissions)

    def getCompletedMissionsCount(self):
        return sum((1 for quests in self._questMissions if isAllQuestsCompleted(quests)))

    def getTitle(self):
        return _ms(getLocalizedQuestNameForLinkedSetQuest(self.mainQuest))

    def markVisited(self):
        if self.mainQuest and (self.mainQuest.isAvailable().isValid or self.mainQuest.isCompleted()):
            settings.visitEventGUI(self.mainQuest)

    def _findEvents(self, srvEvents):
        return filter(self.__applyFilter, srvEvents.itervalues())

    def _getHeaderData(self):
        info = text_styles.standard(_ms(LINKEDSET.MISSIONS_COMPLETED, cur_count=self.getCompletedMissionsCount(), total_count=self.getTotalMissionsCount()))
        return {'titleBlock': self.getTitleBlock(),
         'info': info}

    def _getVO(self):
        vo = super(_LinkedSetQuestsBlockInfo, self)._getVO()
        vo['bodyDataLinkedSet'] = vo.pop('bodyData')
        vo['isLinkedSet'] = True
        return vo

    def _getBodyData(self):
        missions = []
        for quests in self._questMissions:
            status = None
            checkStates = []
            groupIsCompleted = isAllQuestsCompleted(quests)
            groupIsAvailable = groupIsCompleted or hasAtLeastOneAvailableQuest(quests)
            if not groupIsAvailable:
                status = formatErrorTextWithIcon(_ms(LINKEDSET.NOT_AVAILABLE))
            else:
                isSingleQuest = len(quests) == 1
                if not groupIsCompleted and isSingleQuest:
                    status = _ms(LINKEDSET.MISSION_NOT_COMPLETE)
                else:
                    checkStates = [ quest.isCompleted() for quest in quests ]
            missionID = getLinkedSetMissionIDFromQuest(quests[0])
            if groupIsAvailable:
                uiDecoration = RES_ICONS.getLinkedSetMissionItemActive(missionID)
            else:
                uiDecoration = RES_ICONS.getLinkedSetMissionItemDisable(missionID)
            advisable = self.eventsCache.getAdvisableQuests()
            advisableQuests = [ quest for quest in quests if quest.getID() in advisable ]
            isCornerEnable = bool(len(settings.getNewCommonEvents(advisableQuests)))
            missions.append({'eventID': str(missionID),
             'title': _ms(LINKEDSET.getMissionName(missionID)),
             'status': status,
             'isAvailable': True,
             'isCornerEnable': isCornerEnable,
             'uiPicture': RES_ICONS.getLinkedSetMissionIconItem(missionID),
             'uiDecoration': uiDecoration,
             'checkStates': checkStates})

        result = {'title': _ms(getLocalizedQuestNameForLinkedSetQuest(self.mainQuest)),
         'description': _ms(getLocalizedQuestDescForLinkedSetQuest(self.mainQuest)),
         'isButtonUseTokenEnabled': self.linkedSet.hasLinkedSetFinishToken(),
         'buttonUseTokenLabel': _ms(LINKEDSET.USE_THE_TOKEN),
         'uiDecoration': RES_ICONS.MAPS_ICONS_LINKEDSET_LINKEDSET_BGR_LANDING,
         'missions': missions}
        return result

    def _updateLinkedSetMissions(self):
        self._questMissions = self.linkedSet.getMissions()
        self.mainQuest = self._questMissions.pop()[0]

    def __applyFilter(self, quest):
        return isLinkedSet(quest.getGroupID())


class _PremiumGroupedQuestsBlockInfo(_GroupedQuestsBlockInfo):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    blockType = GuiGroupBlockID.PREMIUM_QUESTS_BLOCK
    groupID = 'prem_acc_qroup'

    def __init__(self):
        group = getPremiumGroup()
        super(_PremiumGroupedQuestsBlockInfo, self).__init__(group, headerLinkage=QUESTS_ALIASES.MISSIONS_LINKED_SET_HEADER_LINKAGE, bodyLinkage=QUESTS_ALIASES.MISSIONS_PREMIUM_BODY_LINKAGE)
        self._filterEnable = False

    def findEvents(self, srvEvents):
        return sorted(self._findEvents(srvEvents), cmp=premMissionsSortFunc, reverse=False)

    def getTitle(self):
        title = backport.text(R.strings.quests.premiumQuest.header.title())
        return '{}{}'.format(makeImageTag(backport.image(R.images.gui.maps.icons.premacc.icons.premium_40x40()), 40, 40, -12), title)

    def _getVO(self):
        vo = super(_PremiumGroupedQuestsBlockInfo, self)._getVO()
        vo['bodyDataPremium'] = vo.pop('bodyData')
        vo['isPremium'] = True
        return vo

    def _getBodyData(self):
        cardsList = []
        for e in self._events:
            eventID = e.getID()
            if eventID in self._cachedInfo:
                missionData = self._cachedInfo[eventID]
            else:
                missionData = getMissionInfoData(e)
                self._cachedInfo[eventID] = missionData
            cardsList.append(missionData.getInfo())

        isPremEnabled = self.__isPremiumEnabled()
        isAllCompleted = self._completedQuestsCount == self._totalQuestsCount
        timeStr = self._getDailyResetStatus()
        completeTitle = text_styles.missionStatusAvailable(backport.text(R.strings.quests.premiumQuest.body.complete(), time=timeStr) if isAllCompleted else '')
        return {'missions': cardsList,
         'title': text_styles.promoTitle(QUESTS.PREMIUMQUEST_BODY_TITLE),
         'description': text_styles.highlightText(QUESTS.PREMIUMQUEST_BODY_DESCRIPTION),
         'buttonDetails': QUESTS.PREMIUMQUEST_BODY_BUTTONDETAILS,
         'icon': backport.image(R.images.gui.maps.icons.premacc.icons.premium_256x242()),
         'hasPremium': isPremEnabled,
         'completeTitle': completeTitle,
         'uiDecoration': backport.image(R.images.gui.maps.icons.premacc.quests.background())}

    def _getDailyResetStatus(self):
        resetHourUTC = self.lobbyContext.getServerSettings().regionals.getDayStartingTime() / time_utils.ONE_HOUR
        deltaTimeUTC = time_utils.getTimeDeltaFromNow(time_utils.getDailyTimeForUTC(hour=resetHourUTC))
        if resetHourUTC >= 0:
            timeFmt = backport.text(R.strings.quests.details.conditions.postBattle.deltaDailyReset.timeFmt())
            parts = time_utils.getTimeStructInUTC(deltaTimeUTC)
            try:
                return time.strftime(timeFmt, parts)
            except ValueError:
                _logger.error('Current time locale: %r', locale.getlocale(locale.LC_TIME))
                _logger.error('Selected language: %r', getLanguageCode())
                _logger.exception('Invalid formatting string %r to delta of time %r', timeFmt, parts)

    def _getHeaderData(self):
        info = _getMissionsCountLabel(self._completedQuestsCount, self._totalQuestsCount)
        return {'titleBlock': self.getTitleBlock(),
         'info': info}

    def __isPremiumEnabled(self):
        return self.itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
