# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsSeasonsView.py
import weakref
import operator
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_CURRENT_EXCEPTION
from helpers import i18n
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.server_events import event_items
from gui.shared.gui_items import Vehicle
from gui.server_events import g_eventsCache, events_dispatcher as quest_events, settings as quest_settings, formatters as quests_fmts
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.Scaleform.daapi.view.meta.QuestsSeasonsViewMeta import QuestsSeasonsViewMeta
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties

class QuestsSeasonsView(QuestsSeasonsViewMeta, AppRef):

    def __init__(self):
        super(QuestsSeasonsView, self).__init__()
        self.__proxy = None
        return

    def onShowAwardsClick(self, seasonID):
        quest_events.showPQSeasonAwardsWindow(int(seasonID))

    def onTileClick(self, tileID):
        try:
            self.__proxy._showTileChainsView(tileID)
        except:
            LOG_WARNING('Error while getting event window for showing quests list window')
            LOG_CURRENT_EXCEPTION()

    def onSlotClick(self, questID):
        try:
            quest = g_eventsCache.potapov.getQuests()[questID]
            self.__proxy._showTileChainsView(quest.getTileID(), questID)
        except:
            LOG_WARNING('Error while getting event window for showing quests list window')
            LOG_CURRENT_EXCEPTION()

    def _populate(self):
        super(QuestsSeasonsView, self)._populate()
        g_eventsCache.potapov.onSelectedQuestsChanged += self._onSelectedQuestsChanged
        g_eventsCache.potapov.onProgressUpdated += self._onProgressUpdated
        self.__populateSeasonsData()
        self.__populateSlotsData()

    def _dispose(self):
        g_eventsCache.potapov.onProgressUpdated -= self._onProgressUpdated
        g_eventsCache.potapov.onSelectedQuestsChanged -= self._onSelectedQuestsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__proxy = None
        super(QuestsSeasonsView, self)._populate()
        return

    def _setMainView(self, eventsWindow):
        self.__proxy = weakref.proxy(eventsWindow)

    def _onSelectedQuestsChanged(self, _):
        self.__populateSlotsData()

    def _onProgressUpdated(self):
        self.__populateSeasonsData()
        self.__populateSlotsData()

    def __populateSeasonsData(self):
        _getText = self.app.utilsManager.textManager.getText
        pqSettings = quest_settings.get()
        seasons = []
        for seasonID, season in g_eventsCache.potapov.getSeasons().iteritems():
            tiles = []
            for tile in sorted(season.getTiles().values(), key=operator.methodcaller('getID')):
                isCompleted, isUnlocked = tile.isAwardAchieved(), tile.isUnlocked()
                iconID = tile.getIconID()
                if isCompleted:
                    bgImgUp, bgImgOver = event_items.getTileNormalUpIconPath(iconID), event_items.getTileNormalOverIconPath(iconID)
                else:
                    bgImgUp, bgImgOver = event_items.getTileGrayUpIconPath(iconID), event_items.getTileGrayOverIconPath(iconID)
                vehicleBonus = tile.getVehicleBonus()
                if vehicleBonus is not None:
                    vehLevelStr = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(Vehicle.getLevelSmallIconPath(vehicleBonus.level), 16, 16, -3, 0))
                    vehTypeStr = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(Vehicle.getTypeSmallIconPath(vehicleBonus.type), 16, 16, -3, 0))
                    vehicleBonusLabel = i18n.makeString(QUESTS.PERSONAL_SEASONS_TILELABEL, type=vehTypeStr, level=vehLevelStr, name=vehicleBonus.longUserName)
                else:
                    vehicleBonusLabel = ''
                tokenIcon = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_QUESTS_TOKEN16, 16, 16, -3, 0))
                if isUnlocked and not isCompleted:
                    gottenTokensCount, totalTokensCount = tile.getTokensCount()
                    progress = _getText(TextType.STANDARD_TEXT, i18n.makeString(QUESTS.PERSONAL_SEASONS_TILEPROGRESS, count=_getText(TextType.GOLD_TEXT, str(gottenTokensCount)), total=str(totalTokensCount), icon=tokenIcon))
                else:
                    progress = ''
                if tile.isFullCompleted():
                    animation = event_items.getTileAnimationPath(iconID)
                else:
                    animation = None
                tiles.append({'id': tile.getID(),
                 'isNew': isUnlocked and quest_settings.isPQTileNew(tile.getID(), pqSettings),
                 'label': _getText(TextType.STANDARD_TEXT, vehicleBonusLabel),
                 'progress': progress,
                 'isCompleted': isUnlocked and isCompleted,
                 'enabled': isUnlocked,
                 'image': bgImgUp,
                 'imageOver': bgImgOver,
                 'animation': animation})

            seasons.append({'id': seasonID,
             'title': i18n.makeString(QUESTS.PERSONAL_SEASONS_ITEMTITLE, num=seasonID, name=season.getUserName()),
             'tiles': tiles})

        self.as_setSeasonsDataS(seasons)
        return

    def __populateSlotsData(self):
        selectedQuests = g_eventsCache.potapov.getSelectedQuests().values()
        freeSlotsCount = g_eventsCache.questsProgress.getPotapovQuestsFreeSlots()
        slotIdx, slots = 0, []
        for slotIdx, quest in enumerate(selectedQuests):
            tile = g_eventsCache.potapov.getTiles()[quest.getTileID()]
            slots.append((tile.getChainVehicleClass(quest.getChainID()), self.__packQuestSlot(quest)))

        slots = map(lambda (_, slot): slot, sorted(slots, key=operator.itemgetter(0), cmp=Vehicle.compareByVehTypeName))
        nextSlotIdx = slotIdx + 1
        for slotIdx in xrange(nextSlotIdx, nextSlotIdx + freeSlotsCount):
            slots.append(self.__packQuestSlot())

        self.as_setSlotsDataS(slots)

    def __packQuestSlot(self, quest = None):
        _getText = self.app.utilsManager.textManager.getText
        ttHeader, ttBody, ttAttention, ttNote = (None, None, None, None)
        if quest is not None:
            tile = g_eventsCache.potapov.getTiles()[quest.getTileID()]
            season = g_eventsCache.potapov.getSeasons()[tile.getSeasonID()]
            isInProgress = True
            ttHeader = quest.getUserName()
            ttBody = i18n.makeString(TOOLTIPS.PRIVATEQUESTS_SLOT_MISSIONCOMPLETE_BODY, season=season.getUserName(), tile=tile.getUserName())
            if quest.needToGetReward():
                icon = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, 16, 16, -3, 0))
                description = _getText(TextType.NEUTRAL_TEXT, i18n.makeString(QUESTS.PERSONAL_SEASONS_SLOTS_GETAWARD, icon=icon))
                ttAttention = i18n.makeString(TOOLTIPS.PRIVATEQUESTS_SLOT_MISSIONCOMPLETE_ATTENTION)
            else:
                description = _getText(TextType.STANDARD_TEXT, quests_fmts.getPQFullDescription(quest))
                ttNote = i18n.makeString(TOOLTIPS.PRIVATEQUESTS_SLOT_MISSION_NOTE)
            title = _getText(TextType.MIDDLE_TITLE, i18n.makeString(QUESTS.PERSONAL_SEASONS_SLOTS_TITLE, questName=quest.getUserName()))
        else:
            title, isInProgress = '', False
            description = _getText(TextType.DISABLE_TEXT, i18n.makeString(QUESTS.PERSONAL_SEASONS_SLOTS_NODATA))
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
