# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_quests_panel.py
import logging
from helpers import dependency
from constants import EVENT_MISSION_ICON_SIZES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.meta.EventQuestsPanelMeta import EventQuestsPanelMeta
from gui.server_events.conditions import getProgressFromQuestWithSingleAccumulative
from gui.server_events.events_dispatcher import showEventHangar
from skeletons.gui.game_event_controller import IGameEventController
from gui.server_events.events_dispatcher import showEventMissions
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.awards_formatters import getEventAwardFormatter, AWARDS_SIZES
_logger = logging.getLogger(__name__)
_MAX_PROGRESS_BAR_VALUE = 100

class EventQuestsPanelView(EventQuestsPanelMeta):
    gameEventController = dependency.descriptor(IGameEventController)

    def closeView(self):
        showEventHangar()

    def onQuestPanelClick(self):
        showEventMissions()

    def _populate(self):
        super(EventQuestsPanelView, self)._populate()
        self._updateMissions()
        self.gameEventController.getMissionsController().onUpdated += self._updateMissions

    def _dispose(self):
        super(EventQuestsPanelView, self)._dispose()
        self.gameEventController.getMissionsController().onUpdated -= self._updateMissions

    def _updateMissions(self):
        result = [ self.getItemVO(mission, mission.getSelectedItem()) for mission in sorted(self.gameEventController.getMissionsController().getMissions().itervalues(), key=lambda m: m.getID()) ]
        self.as_setListDataProviderS(result)

    def getItemVO(self, mission, item):
        quest = item.getQuest()
        currentProgress, totalProgress = getProgressFromQuestWithSingleAccumulative(quest)
        itemDescr = item.getDescr()
        progress = -1
        if item.isCompleted():
            if item.isDaily():
                header = backport.text(R.strings.event.missions.panel.dailyCompleted(), time=item.getDailyResetTime())
            else:
                header = backport.text(R.strings.event.missions.panel.allCompleted())
        else:
            header = itemDescr
            if totalProgress and totalProgress > 1:
                if currentProgress is None:
                    currentProgress = 0
                progress = int(currentProgress / float(totalProgress) * _MAX_PROGRESS_BAR_VALUE)
        bonuses = getEventAwardFormatter().format(item.getBonuses())
        rewards = [ {'icon': bonus.getImage(AWARDS_SIZES.SMALL),
         'label': bonus.label} for bonus in bonuses ]
        missionIconSmall = mission.getIcon(EVENT_MISSION_ICON_SIZES.SMALL)
        missionIconBig = mission.getIcon(EVENT_MISSION_ICON_SIZES.BIG)
        return {'header': header,
         'progressTotal': totalProgress,
         'progressCurrent': currentProgress,
         'progress': progress,
         'icon': missionIconSmall,
         'tooltipData': {'isSpecial': True,
                         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_MISSION_INFO,
                         'specialArgs': [itemDescr,
                                         missionIconBig,
                                         totalProgress,
                                         currentProgress,
                                         rewards,
                                         item.getStatusLocalized()]},
         'completed': item.isCompleted()}
