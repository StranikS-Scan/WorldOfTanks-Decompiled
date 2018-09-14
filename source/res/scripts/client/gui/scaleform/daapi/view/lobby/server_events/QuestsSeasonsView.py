# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsSeasonsView.py
import weakref
import operator
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui.Scaleform.daapi.view.lobby.server_events import old_events_helpers
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES
from gui.shared.formatters import icons, text_styles
from helpers import dependency
from helpers import i18n
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.server_events import event_items, caches
from gui.shared.gui_items import Vehicle
from gui.server_events import events_dispatcher as quest_events, settings as quest_settings, formatters as quests_fmts
from gui.Scaleform.daapi.view.meta.QuestsSeasonsViewMeta import QuestsSeasonsViewMeta
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from skeletons.gui.server_events import IEventsCache

def _getQuestsCache():
    return old_events_helpers.getPotapovQuestsCache()


def _getQuestsProgress():
    return old_events_helpers.getPotapovQuestsProgress()


def _sortWithQuestType(items, key):
    return old_events_helpers.sortWithQuestType(items, key)


def _packTabDataItem(label, tabID):
    return {'label': label,
     'id': tabID}


class QuestsSeasonsView(QuestsSeasonsViewMeta):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(QuestsSeasonsView, self).__init__()
        self.__proxy = None
        self.__navInfo = caches.getNavInfo()
        return

    def onShowAwardsClick(self):
        quest_events.showPQSeasonAwardsWindow(self.__navInfo.selectedPQType)

    def onTileClick(self, tileID):
        try:
            self.__proxy.showTileChainsView(tileID)
        except:
            LOG_WARNING('Error while getting event window for showing quests list window')
            LOG_CURRENT_EXCEPTION()

    def onSlotClick(self, questID):
        try:
            quest = _getQuestsCache().getQuests()[questID]
            self.__proxy.showTileChainsView(quest.getTileID(), questID)
        except:
            LOG_WARNING('Error while getting event window for showing quests list window')
            LOG_CURRENT_EXCEPTION()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(QuestsSeasonsView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == QUESTS_ALIASES.QUESTS_CONTENT_TABS_PY_ALIAS:
            viewPy.selectTab(self.__navInfo.selectedPQType)
            viewPy.onTabSelected += self.__onTabSelected

    def __onTabSelected(self, tabId):
        self.__navInfo.setPQTypeByTabID(tabId)
        self.__populateSeasonsData()
        self.__populateSlotsData()

    @property
    def _contentTabs(self):
        return self.components.get(QUESTS_ALIASES.QUESTS_CONTENT_TABS_PY_ALIAS)

    def _populate(self):
        super(QuestsSeasonsView, self)._populate()
        self.eventsCache.onSelectedQuestsChanged += self._onSelectedQuestsChanged
        self.eventsCache.onProgressUpdated += self._onProgressUpdated
        self.__populateViewData()
        self.__populateSeasonsData()
        self.__populateSlotsData()

    def _dispose(self):
        self.eventsCache.onSelectedQuestsChanged -= self._onSelectedQuestsChanged
        self.eventsCache.onProgressUpdated -= self._onProgressUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__proxy = None
        super(QuestsSeasonsView, self)._dispose()
        return

    def _setMainView(self, eventsWindow):
        self.__proxy = weakref.proxy(eventsWindow)

    def _onSelectedQuestsChanged(self, _, pqType):
        targetTab = old_events_helpers.getTabAliasByQuestBranchName(pqType)
        if targetTab == self.__navInfo.selectedPQType:
            self.__populateSlotsData()

    def _onProgressUpdated(self, pqType):
        targetTab = old_events_helpers.getTabAliasByQuestBranchName(pqType)
        if targetTab == self.__navInfo.selectedPQType:
            self.__populateSeasonsData()
            self.__populateSlotsData()

    def __populateViewData(self):
        self.as_setDataS({'awardsButtonLabel': QUESTS.PERSONAL_SEASONS_AWARDSBUTTON,
         'awardsButtonTooltip': TOOLTIPS.PRIVATEQUESTS_AWARDSBUTTON,
         'background': RES_ICONS.MAPS_ICONS_QUESTS_SEASONSVIEWBG})

    def __populateSeasonsData(self):
        seasons = []
        pqType = self.__navInfo.selectedPQType
        for seasonID, season in _getQuestsCache().getSeasons().iteritems():
            tiles = []
            for tile in sorted(season.getTiles().values(), key=operator.methodcaller('getID')):
                isCompleted, isUnlocked = tile.isAwardAchieved(), tile.isUnlocked()
                iconID = tile.getIconID()
                if isCompleted:
                    bgImgUp = event_items.getTileNormalUpIconPath(iconID)
                    bgImgOver = event_items.getTileNormalOverIconPath(iconID)
                else:
                    bgImgUp = event_items.getTileGrayUpIconPath(iconID)
                    bgImgOver = event_items.getTileGrayOverIconPath(iconID)
                vehicleBonus = tile.getVehicleBonus()
                if vehicleBonus is not None:
                    vehLevelStr = icons.makeImageTag(Vehicle.getLevelSmallIconPath(vehicleBonus.level), 16, 16, -3, 0)
                    vehTypeStr = icons.makeImageTag(Vehicle.getTypeSmallIconPath(vehicleBonus.type), 16, 16, -3, 0)
                    vehicleBonusLabel = i18n.makeString(QUESTS.PERSONAL_SEASONS_TILELABEL, type=vehTypeStr, level=vehLevelStr, name=vehicleBonus.userName)
                else:
                    vehicleBonusLabel = ''
                tokenIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_QUESTS_TOKEN16, 16, 16, -3, 0)
                if isUnlocked and not isCompleted and pqType == QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM:
                    gottenTokensCount, totalTokensCount = tile.getTokensCount()
                    progress = text_styles.standard(i18n.makeString(QUESTS.PERSONAL_SEASONS_TILEPROGRESS, count=text_styles.gold(str(gottenTokensCount)), total=str(totalTokensCount), icon=tokenIcon))
                else:
                    progress = ''
                if tile.isFullCompleted():
                    animation = event_items.getTileAnimationPath(iconID)
                else:
                    animation = None
                if pqType == QUESTS_ALIASES.SEASON_VIEW_TAB_RANDOM:
                    tooltipType = TOOLTIPS_CONSTANTS.PRIVATE_QUESTS_TILE
                else:
                    tooltipType = TOOLTIPS_CONSTANTS.PRIVATE_QUESTS_FALLOUT_TILE
                tiles.append({'id': tile.getID(),
                 'isNew': isUnlocked and quest_settings.isPQTileNew(tile.getID()),
                 'label': text_styles.standard(vehicleBonusLabel),
                 'progress': progress,
                 'isCompleted': isUnlocked and isCompleted,
                 'enabled': isUnlocked,
                 'image': bgImgUp,
                 'imageOver': bgImgOver,
                 'animation': animation,
                 'tooltipType': tooltipType})

            seasons.append({'id': seasonID,
             'title': quests_fmts.getFullSeasonUserName(season),
             'tiles': tiles})

        self.as_setSeasonsDataS({'seasons': seasons})
        return

    def __populateSlotsData(self):
        selectedQuests = _getQuestsCache().getSelectedQuests().values()
        freeSlotsCount = _getQuestsProgress().getPotapovQuestsFreeSlots()
        slotIdx, slots = 0, []
        for slotIdx, quest in enumerate(selectedQuests):
            tile = _getQuestsCache().getTiles()[quest.getTileID()]
            slots.append((tile.getChainSortKey(quest.getChainID()), self.__packQuestSlot(quest)))

        slots = map(lambda (_, slot): slot, _sortWithQuestType(slots, operator.itemgetter(0)))
        nextSlotIdx = slotIdx + 1
        for slotIdx in xrange(nextSlotIdx, nextSlotIdx + freeSlotsCount):
            slots.append(self.__packQuestSlot())

        self.as_setSlotsDataS({'questSlots': slots,
         'hasActiveQuests': len(selectedQuests) > 0,
         'noActiveQuestsText': text_styles.builder('\n').addStyledText(TEXT_MANAGER_STYLES.MIDDLE_TITLE, QUESTS.PERSONAL_SEASONS_SLOTS_NOACTIVESLOTS_HEADER).addStyledText(TEXT_MANAGER_STYLES.STANDARD_TEXT, QUESTS.PERSONAL_SEASONS_SLOTS_NOACTIVESLOTS_BODY).render()})

    def __packQuestSlot(self, quest=None):
        ttHeader, ttBody, ttAttention, ttNote = (None, None, None, None)
        if quest is not None:
            tile = _getQuestsCache().getTiles()[quest.getTileID()]
            season = _getQuestsCache().getSeasons()[tile.getSeasonID()]
            isInProgress = True
            ttHeader = quest.getUserName()
            ttBody = quests_fmts.getFullTileUserName(season, tile)
            if quest.needToGetReward():
                icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, 16, 16, -3, 0)
                description = text_styles.neutral(i18n.makeString(QUESTS.PERSONAL_SEASONS_SLOTS_GETAWARD, icon=icon))
                ttAttention = i18n.makeString(TOOLTIPS.PRIVATEQUESTS_SLOT_MISSIONCOMPLETE_ATTENTION)
            else:
                description = text_styles.standard(quests_fmts.getPQFullDescription(quest))
                ttNote = i18n.makeString(TOOLTIPS.PRIVATEQUESTS_SLOT_MISSION_NOTE)
            title = text_styles.middleTitle(i18n.makeString(QUESTS.PERSONAL_SEASONS_SLOTS_TITLE, questName=quest.getUserName()))
        else:
            title, isInProgress = '', False
            description = text_styles.disabled(i18n.makeString(QUESTS.PERSONAL_SEASONS_SLOTS_NODATA))
            ttHeader = i18n.makeString(TOOLTIPS.PRIVATEQUESTS_SLOT_EMPTY_HEADER)
            ttBody = i18n.makeString(TOOLTIPS.PRIVATEQUESTS_SLOT_EMPTY_BODY)
        return {'id': quest.getID() if quest else None,
         'title': title,
         'description': description,
         'inProgress': isInProgress,
         'completed': quest and quest.needToGetReward(),
         'ttHeader': ttHeader,
         'ttBody': ttBody,
         'ttNote': ttNote,
         'ttAttention': ttAttention}
