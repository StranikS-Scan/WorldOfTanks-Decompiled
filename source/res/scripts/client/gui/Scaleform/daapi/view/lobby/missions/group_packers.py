# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/group_packers.py
from collections import namedtuple, defaultdict
import BigWorld
from CurrentVehicle import g_currentVehicle
from Event import EventManager, Event
from constants import EVENT_TYPE
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import MarathonAwardComposer
from gui.Scaleform.daapi.view.lobby.missions.conditions_formatters.tokens import TokensMarathonFormatter
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.MOTIVATION_QUESTS import MOTIVATION_QUESTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import settings
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.event_items import DEFAULTS_GROUPS
from gui.server_events.events_helpers import missionsSortFunc
from gui.server_events.formatters import DECORATION_SIZES
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.server_events import IEventsCache
_EventsBlockData = namedtuple('EventsBlockData', 'filteredCount totalCount blockData')
_MAIN_QUEST_AWARDS_COUNT = 6
_BIG_TOKENS_TRESHOLD = 2
awardsFormatters = MarathonAwardComposer(_MAIN_QUEST_AWARDS_COUNT)
tokenMarathonsCondFormatter = TokensMarathonFormatter()

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
                    return _MarathonQuestsBlockInfo(group)
                else:
                    return _GroupedEventsBlockInfo(group)
        return


def _getMissionsCountLabel(completed, total):
    completed = text_styles.stats(completed)
    total = text_styles.standard(total)
    return text_styles.concatStylesToSingleLine(text_styles.standard(QUESTS.MISSIONS_TAB_CATEGORY_HEADER_PERFORMEDTASKS), text_styles.disabled('  %s / %s' % (completed, total)))


class _EventsBlockBuilder(object):
    """
    Base class to build and collect blocks with server events data for mission view tab
    """

    def __init__(self):
        self._cache = defaultdict(dict)
        self.__initDefaultBlocks()
        self.__cachedSortedDataBlocks = None
        return

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
        """ Set quests of all the blocks as viewed.
        """
        for groupInfo in self.__getBlocksInfos():
            groupInfo.markVisited()

    def getBlocksAdvisableEvents(self, events):
        """ Get events that can be notified as new from the current block.
        """
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

        return sorted(result, key=lambda e: e.getSortPriority(), reverse=True)


class VehicleGroupFinder(_EventsBlockBuilder):
    """
    Build and collect block with server events data for current vehicle tab on mission page
    """

    def __init__(self):
        super(VehicleGroupFinder, self).__init__()
        self.__em = EventManager()
        self.onBlocksDataChanged = Event(self.__em)

    def init(self):
        super(VehicleGroupFinder, self).init()
        g_currentVehicle.onChanged += self.__onVehicleChanged

    def clear(self):
        super(VehicleGroupFinder, self).init()
        g_currentVehicle.onChanged -= self.__onVehicleChanged
        self.__em.clear()

    def _getDefaultBlocks(self):
        return [_VehicleQuestsBlockInfo()]

    def __onVehicleChanged(self):
        self.onBlocksDataChanged()


class GroupedEventsBlocksFinder(_EventsBlockBuilder):
    """
    Base class to build and collect blocks with server events data by a specific group
    """
    eventsCache = dependency.descriptor(IEventsCache)

    def clear(self):
        cachedGroups = self._cache['groupedEvents']
        for blockInfo in cachedGroups.itervalues():
            blockInfo.clear()

        cachedGroups.clear()
        super(GroupedEventsBlocksFinder, self).clear()

    def invalidateBlocks(self):
        super(GroupedEventsBlocksFinder, self).invalidateBlocks()
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
            cachedGroups[gID].invalidate()

        for gID in newGroupsIds:
            cachedGroups[gID] = self._createGroupedEventsBlock(newEventsGroups[gID])

    def _createGroupedEventsBlock(self, group):
        raise NotImplementedError

    def _getEventsGroups(self):
        raise NotImplementedError


class MarathonsGroupsFinder(GroupedEventsBlocksFinder):
    """
    Build and collect blocks with server events data for marathon tab on mission page
    Each marathon is a separate block in GUI.
    Marathon has header with reward and token conditions (main token quest) and missions cards.
    Missions cards are colled by groupID inside marathon.
    """

    def _createGroupedEventsBlock(self, group):
        return _MarathonQuestsBlockInfo(group)

    def _getEventsGroups(self):
        return self.eventsCache.getGroups(filterFunc=lambda g: g.isMarathon())


class QuestsGroupsFinder(GroupedEventsBlocksFinder):
    """
    Build and collect blocks with server events data for categories mission tab on mission page
    Each categories is a separate block in GUI.
    All quests that have groupID and don't belong to marathons are placed in group categories by groupID
    All others quests are placed in non group categorie.
    Categorie hasn't reward.
    """

    def _getDefaultBlocks(self):
        return [_MotiveQuestsBlockInfo(), _UngroupedQuestsBlockInfo()]

    def _createGroupedEventsBlock(self, group):
        return _GroupedQuestsBlockInfo(group)

    def _getEventsGroups(self):
        return self.eventsCache.getGroups(filterFunc=lambda g: not g.isMarathon())


class _EventsBlockInfo(object):

    def __init__(self):
        self._events = ()
        self._suitableEvents = ()
        self._cachedInfo = {}

    def getSuitableEvents(self):
        return self._suitableEvents

    def invalidate(self):
        self._cachedInfo.clear()

    def getSortPriority(self):
        pass

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.findEvents(srvEvents)
        self._events = filter(filterFunc, self._suitableEvents)
        return _EventsBlockData(len(self._events), len(self._suitableEvents), self._getVO())

    def getBlockAdvisableEvents(self, srvEvents):
        """ Get events that can be notified as new from the current block.
        """
        return self.findEvents(srvEvents)

    def markVisited(self):
        """ Set events of the current block as viewed.
        """
        settings.visitEventsGUI(self._suitableEvents)

    def clear(self):
        self._events = ()
        self._suitableEvents = ()
        self._cachedInfo.clear()

    def getEventsBlockID(self):
        raise NotImplementedError

    def findEvents(self, srvEvents):
        return sorted(self._findEvents(srvEvents), missionsSortFunc, reverse=True)

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

    @classmethod
    def _getGuiLinkages(cls):
        return {'headerLinkage': '',
         'bodyLinkage': ''}

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

        if not cardsList and self._suitableEvents:
            return {'missions': cardsList,
             'dummy': {'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
                       'htmlText': text_styles.alert(_ms(QUESTS.MISSIONS_NOTASKSBODY_DUMMY_TEXT)),
                       'alignCenter': False,
                       'btnVisible': True,
                       'btnLabel': QUESTS.MISSIONS_NOTASKSBODY_DUMMY_BTNLABEL,
                       'btnTooltip': '',
                       'btnEvent': 'ResetFilterEvent'}}
        else:
            return {'missions': cardsList}

    def _getHeaderData(self):
        raise NotImplementedError

    def getTitle(self):
        raise NotImplementedError

    def getDetailedTitle(self):
        raise NotImplementedError


class _MinimizableEventsBlockInfo(_EventsBlockInfo):

    def _getVO(self):
        data = super(_MinimizableEventsBlockInfo, self)._getVO()
        data.update({'isCollapsed': settings.isGroupMinimized(self.getEventsBlockID())})
        return data


class _GroupedEventsBlockInfo(_MinimizableEventsBlockInfo):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, group):
        super(_GroupedEventsBlockInfo, self).__init__()
        self._group = group

    def getSortPriority(self):
        return (2, self._group.getPriority())

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.findEvents(srvEvents)
        self._events = filter(filterFunc, self._suitableEvents)
        if not self._suitableEvents:
            return None
        else:
            return _EventsBlockData(len(self._events), len(self._suitableEvents), self._getVO())
            return None

    def clear(self):
        self._group = None
        return

    def _findEvents(self, srvEvents):
        return self._group.getGroupContent(srvEvents)

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

    def __init__(self, group):
        super(_GroupedQuestsBlockInfo, self).__init__(group)
        self.__totalQuestsCount = 0
        self.__completedQuestsCount = 0

    @classmethod
    def _getGuiLinkages(cls):
        return {'headerLinkage': QUESTS_ALIASES.MISSION_PACK_CATEGORY_HEADER_LINKAGE,
         'bodyLinkage': QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE}

    def _findEvents(self, srvEvents):
        result = self._group.getGroupContent(srvEvents)
        self.__completedQuestsCount = 0
        for quest in result:
            if quest.isCompleted():
                self.__completedQuestsCount += 1

        self.__totalQuestsCount = len(result)
        return result

    def _getDescrBlock(self):
        data = super(_GroupedQuestsBlockInfo, self)._getDescrBlock()
        data.update({'isMultiline': False})
        data.update({'descr': _getMissionsCountLabel(self.__completedQuestsCount, self.__totalQuestsCount)})
        return data


class _MarathonQuestsBlockInfo(_GroupedEventsBlockInfo):

    def __init__(self, group):
        super(_MarathonQuestsBlockInfo, self).__init__(group)
        self._mainQuest = None
        return

    def clear(self):
        self._mainQuest = None
        super(_MarathonQuestsBlockInfo, self).clear()
        return

    def _findEvents(self, srvEvents):
        suitableEvents = self._group.getGroupContent(srvEvents)
        self._mainQuest = self._group.getMainQuest(suitableEvents)
        if self._mainQuest:
            suitableEvents.remove(self._mainQuest)
        return suitableEvents

    def _getMainQuest(self):
        return self._mainQuest

    @classmethod
    def _getGuiLinkages(cls):
        return {'headerLinkage': QUESTS_ALIASES.MISSION_PACK_MARATHON_HEADER_LINKAGE,
         'bodyLinkage': QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE}

    def _getDescrBlock(self):
        data = super(_MarathonQuestsBlockInfo, self)._getDescrBlock()
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
                 'specialArgs': awardsFormatters.getShortBonusesData(awardsFormatters.getPreformattedBonuses(self._mainQuest.getBonuses()))}
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


class _UngroupedQuestsBlockInfo(_MinimizableEventsBlockInfo):

    def __init__(self):
        super(_UngroupedQuestsBlockInfo, self).__init__()
        self.__totalQuestsCount = 0
        self.__completedQuestsCount = 0

    def getSortPriority(self):
        pass

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.findEvents(srvEvents)
        self._events = filter(filterFunc, self._suitableEvents)
        if not self._suitableEvents:
            return None
        else:
            return _EventsBlockData(len(self._events), len(self._suitableEvents), self._getVO())
            return None

    def getEventsBlockID(self):
        return DEFAULTS_GROUPS.UNGROUPED_QUESTS

    def getTitle(self):
        return text_styles.promoTitle(QUESTS.QUESTS_TITLE_UNGOUPEDQUESTS)

    def getTitleBlock(self):
        return {'title': self.getTitle()}

    @classmethod
    def _getGuiLinkages(cls):
        return {'headerLinkage': QUESTS_ALIASES.MISSION_PACK_CATEGORY_HEADER_LINKAGE,
         'bodyLinkage': QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE}

    def _findEvents(self, srvEvents):
        suitabaleQuests = filter(lambda q: q.getGroupID() == DEFAULTS_GROUPS.UNGROUPED_QUESTS and q.getType() != EVENT_TYPE.MOTIVE_QUEST, srvEvents.itervalues())
        self.__totalQuestsCount = len(suitabaleQuests)
        self.__completedQuestsCount = len(filter(lambda q: q.isCompleted(), suitabaleQuests))
        return suitabaleQuests

    def _getHeaderData(self):
        return {'titleBlock': self.getTitleBlock(),
         'descBlock': self._getDescrBlock()}

    def _getDescrBlock(self):
        return {'descr': _getMissionsCountLabel(self.__completedQuestsCount, self.__totalQuestsCount),
         'period': text_styles.middleTitle(QUESTS.MISSIONS_GROUP_OTHERS_LABEL),
         'hasCalendarIcon': False,
         'isMultiline': False}


class _MotiveQuestsBlockInfo(_MinimizableEventsBlockInfo):

    def buildEventsBlockData(self, srvEvents, filterFunc):
        self._suitableEvents = self.findEvents(srvEvents)
        self._events = filter(filterFunc, self._suitableEvents)
        if not self._suitableEvents:
            return None
        else:
            return _EventsBlockData(len(self._events), len(self._suitableEvents), self._getVO())
            return None

    def getSortPriority(self):
        pass

    def getEventsBlockID(self):
        return DEFAULTS_GROUPS.MOTIVE_QUESTS

    def getTitle(self):
        return text_styles.promoTitle(MOTIVATION_QUESTS.GROUP)

    def getTitleBlock(self):
        return {'title': self.getTitle()}

    @classmethod
    def _getGuiLinkages(cls):
        return {'headerLinkage': QUESTS_ALIASES.MISSION_PACK_CATEGORY_HEADER_LINKAGE,
         'bodyLinkage': QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE}

    def _findEvents(self, srvEvents):
        suitabaleQuests = filter(lambda q: q.getType() == EVENT_TYPE.MOTIVE_QUEST and not q.isCompleted() and q.isAvailable()[0], srvEvents.itervalues())
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
        super(_VehicleQuestsBlockInfo, self).__init__()

    def getEventsBlockID(self):
        return DEFAULTS_GROUPS.FOR_CURRENT_VEHICLE

    def getTitleBlock(self):
        tankInfo = ''
        tankType = ''
        item = g_currentVehicle.item
        if item is not None:
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

    @classmethod
    def _getGuiLinkages(cls):
        return {'headerLinkage': QUESTS_ALIASES.MISSION_PACK_CURRENT_VEHICLE_HEADER_LINKAGE,
         'bodyLinkage': QUESTS_ALIASES.MISSION_PACK_MARATHON_BODY_LINKAGE}

    def __applyFilter(self, quest):
        if quest.getType() in (EVENT_TYPE.TOKEN_QUEST, EVENT_TYPE.REF_SYSTEM_QUEST):
            return False
        elif not quest.getFinishTimeLeft():
            return False
        elif quest.getType() != EVENT_TYPE.MOTIVE_QUEST:
            return quest.isValidVehicleCondition(g_currentVehicle.item)
        else:
            return not quest.isCompleted() and quest.isAvailable()[0]
