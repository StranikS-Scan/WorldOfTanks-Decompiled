# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_objectives.py
import SoundGroups
from gui.Scaleform.daapi.view.meta.EventObjectivesMeta import EventObjectivesMeta
from gui.Scaleform.locale.EVENT import EVENT
from gui.shared.utils.TimeInterval import TimeInterval
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.shared.formatters import text_styles
from helpers import time_utils
_SCENARIO_APPEAR_SOUND = 'ev_halloween_additional_conditions_appearance'
_SCENARIO_DONE_SOUND = 'ev_halloween_additional_conditions_done'

class EventObjectives(EventObjectivesMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _GUI_UPDATE_INTERVAL = 1

    def __init__(self):
        super(EventObjectives, self).__init__()
        self._scenario = None
        self._scenarioShown = False
        self._objectiveDoneSoundPlayed = False
        self._guiUpdateInterval = None
        return

    def _populate(self):
        super(EventObjectives, self)._populate()
        randomEventComponent = self._getRandomEventComponent()
        randomEventComponent.onScenarioUpdated += self._onScenariosUpdated
        self._onScenariosUpdated()

    def _dispose(self):
        self._scenario = None
        self._safeStopUpdateInterval()
        randomEventComponent = self._getRandomEventComponent()
        if randomEventComponent is not None:
            randomEventComponent.onScenarioUpdated -= self._onScenariosUpdated()
        super(EventObjectives, self)._dispose()
        return

    def _update(self, scenario):
        isFirstAppear = self._scenario is None and scenario is not None
        self._scenario = scenario
        if self._scenario is not None:
            scenarioDesc = _ms(EVENT.getScenarioDesc(self._scenario.getName()))
            timeStr = ''
            collectedText = ''
            statusStr = ''
            if isFirstAppear:
                SoundGroups.g_instance.playSound2D(_SCENARIO_APPEAR_SOUND)
            if self._scenario.getObjectives():
                objectivesCount = len(self._scenario.getObjectives())
                if objectivesCount > 1:
                    collectedText = text_styles.eventObjectiveStatus(_ms(EVENT.SCENARIOS_COLLECTED, max=objectivesCount, current=sum((1 for objective in self._scenario.getObjectives() if objective.isCompleted())), start=0))
                if self._isActive(self._scenario):
                    if self._scenario.getTimeLeft():
                        timeStr = text_styles.eventObjectiveStatus(time_utils.getTimeLeftFormat(self._scenario.getTimeLeft(), True))
                        self._safeStartUpdateInterval()
                    else:
                        self._safeStopUpdateInterval()
                else:
                    self._safeStopUpdateInterval()
                    if self._isCompleted(self._scenario):
                        statusStr = text_styles.successSimple(_ms(EVENT.SCENARIOS_SUCCESS))
                        if not self._objectiveDoneSoundPlayed:
                            self._objectiveDoneSoundPlayed = True
                            SoundGroups.g_instance.playSound2D(_SCENARIO_DONE_SOUND)
                    else:
                        statusStr = text_styles.failedSimple(_ms(EVENT.SCENARIOS_FAILED))
            if collectedText and statusStr:
                scenarioStatusStr = text_styles.concatStylesWithDelimiter('  ', collectedText, statusStr)
            else:
                scenarioStatusStr = text_styles.concatStylesToSingleLine(collectedText, statusStr)
            self.as_setMainTextS(scenarioDesc, scenarioStatusStr)
            self.as_setTimeS(timeStr)
            if not self._scenarioShown:
                self.as_showS()
                self._scenarioShown = True
        elif self._scenarioShown:
            self.as_hideS()
            self._scenarioShown = False
        return

    def _isCompleted(self, scenario):
        return all((objective.isCompleted() for objective in scenario.getObjectives()))

    def _isFailed(self, scenario):
        return any((objective.isFailed() for objective in scenario.getObjectives()))

    def _isActive(self, scenario):
        return not (self._isCompleted(scenario) or self._isFailed(scenario))

    def _onScenariosUpdated(self):
        randomEventComponent = self._getRandomEventComponent()
        if randomEventComponent is None:
            scenario = None
        else:
            scenario = randomEventComponent.getScenario()
        self._update(scenario)
        return

    def _getRandomEventComponent(self):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        return None if componentSystem is None else getattr(componentSystem, 'randomEventComponent', None)

    def _safeStartUpdateInterval(self):
        if self._guiUpdateInterval is None:
            self._guiUpdateInterval = TimeInterval(self._GUI_UPDATE_INTERVAL, self, '_updateCallback')
            self._guiUpdateInterval.start()
        return

    def _safeStopUpdateInterval(self):
        if self._guiUpdateInterval is not None:
            self._guiUpdateInterval.stop()
            self._guiUpdateInterval = None
        return

    def _updateCallback(self):
        self._update(self._scenario)
