# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_quests_progress_view.py
import logging
import GUI
from helpers import dependency, int2roman
from constants import EVENT_MISSION_ICON_SIZES
from gui.Scaleform.daapi.view.meta.EventQuestsProgressMeta import EventQuestsProgressMeta
from gui.server_events.awards_formatters import getEventAwardFormatter, AWARDS_SIZES
from gui.server_events.conditions import getProgressFromQuestWithSingleAccumulative
from gui.server_events.events_dispatcher import showEventHangar
from gui.shared import events, EVENT_BUS_SCOPE
from skeletons.gui.game_event_controller import IGameEventController
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
_logger = logging.getLogger(__name__)
_MAX_PROGRESS_BAR_VALUE = 100

class EventQuestsProgressView(EventQuestsProgressMeta):
    gameEventController = dependency.descriptor(IGameEventController)
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=VIEW_ALIAS.EVENT_QUESTS, entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_halloween_2019_hangar_metagame_music_missions', exitEvent='ev_halloween_2019_hangar_metagame_music_base')

    def __init__(self, ctx=None):
        super(EventQuestsProgressView, self).__init__(ctx)
        self.__isNavigationEnabled = True
        self.__blur = GUI.WGUIBackgroundBlur()
        self._forceSelectedQuestID = ctx.get('forceSelectedQuestID', None)
        return

    def closeView(self):
        showEventHangar()

    def _populate(self):
        super(EventQuestsProgressView, self)._populate()
        self._updateMissions()
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.__blur.enable = True
        self.gameEventController.getMissionsController().onUpdated += self._updateMissions

    def _dispose(self):
        super(EventQuestsProgressView, self)._dispose()
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.__blur.enable = False
        self.gameEventController.getMissionsController().onUpdated -= self._updateMissions

    def _updateMissions(self):
        result = [ self.getMissionVO(mission) for mission in sorted(self.gameEventController.getMissionsController().getMissions().itervalues(), key=lambda m: m.getID()) ]
        self.as_setDataS({'levels': result})

    def getMissionVO(self, mission):
        quests = []
        currentIndex = None
        selectedItem = mission.getSelectedItem()
        lastItem = mission.getItems()[-1]
        for index, item in enumerate(mission.getItems()):
            bonuses = getEventAwardFormatter().format(item.getBonuses())
            rewards = [ {'icon': bonus.getImage(AWARDS_SIZES.BIG),
             'value': bonus.label,
             'isMoney': True,
             'tooltip': bonus.tooltip,
             'specialArgs': bonus.specialArgs,
             'specialAlias': bonus.specialAlias,
             'isSpecial': bonus.isSpecial} for bonus in bonuses ]
            quest = item.getQuest()
            currentProgress, totalProgress = getProgressFromQuestWithSingleAccumulative(quest)
            if not item.isCompleted() and totalProgress and totalProgress > 1:
                if currentProgress is None:
                    currentProgress = 0
                progress = int(currentProgress / float(totalProgress) * _MAX_PROGRESS_BAR_VALUE)
            else:
                progress = -1
            if currentIndex is None and item.getID() == selectedItem.getID():
                currentIndex = index
            if self._forceSelectedQuestID is not None and quest.getID() == self._forceSelectedQuestID:
                currentIndex = index
                self._forceSelectedQuestID = None
            isAvailable = item.isAvailable()
            quests.append({'label': int2roman(index + 1),
             'header': item.getDescr(),
             'progress': progress,
             'progressTotal': totalProgress,
             'progressCurrent': currentProgress,
             'rewards': rewards,
             'current': item.getID() == selectedItem.getID(),
             'unlocked': isAvailable,
             'completed': item.isCompleted(),
             'status': item.getStatusLocalized(),
             'isLast': item.getID() == lastItem.getID()})

        if currentIndex is None:
            currentIndex = 0
        return {'quests': quests,
         'icon': mission.getIcon(EVENT_MISSION_ICON_SIZES.BIG),
         'label': mission.getName(),
         'currentIndex': currentIndex}
