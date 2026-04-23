# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/views/quests_view.py
import CommandMapping
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import CONTROLS
from constants import QUEST_PROGRESS_STATE as STATE
from frameworks.wulf import ViewFlags, ViewSettings
from frontline.gui.impl.gen.view_models.views.battle.quests_model import QuestsModel
from frontline.quests.utils import getQuestUiData
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.utils.key_mapping import getReadableKey
from gui.sounds.epic_sound_constants import EPIC_SOUND
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleController

class EpicBattleQuestsView(ViewImpl):
    __battleController = dependency.descriptor(IEpicBattleController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, settings=None):
        if settings is None:
            settings = ViewSettings(R.views.frontline.battle.QuestView())
            settings.flags = ViewFlags.VIEW
            settings.model = QuestsModel()
        super(EpicBattleQuestsView, self).__init__(settings)
        self.__isInOwnLine = self.__battleController.isOnOwnSector()
        self.__currentSectorID = self.__battleController.getCurrentSector()
        return

    @property
    def viewModel(self):
        return super(EpicBattleQuestsView, self).getViewModel()

    def _onLoading(self):
        with self.viewModel.transaction() as tx:
            tx.setButtonKey(getReadableKey(CommandMapping.CMD_QUEST_PROGRESS_SHOW))
            self.__setQuest(tx, self.__battleController.getQuest())
            value, state = self.__battleController.getQuestProgress()
            if state != STATE.NOT_STARTED:
                self.__setProgress(tx, value, state)
                self.__updateBlockReason(tx, self.__battleController.getCurrentSector())
        super(EpicBattleQuestsView, self)._onLoading()

    def _getEvents(self):
        result = ((self.__battleController.onQuestChanged, self.__onQuestChanged),
         (self.__battleController.onQuestProgressChanged, self.__onQuestProgressChanged),
         (self.__battleController.onCurrentSectorChanged, self.__onSectorChanged),
         (self.__battleController.onOwnSectorsChanged, self.__onOwnSectorsChanged),
         (self.__settingsCore.onSettingsApplied, self.__onSettingsApplied))
        vehCtrl = self.__sessionProvider.shared.vehicleState
        if vehCtrl:
            result += ((self.__sessionProvider.shared.vehicleState.onPostMortemSwitched, self.__onPostMortemSwitched), (self.__sessionProvider.shared.vehicleState.onRespawnBaseMoving, self.__onRespawnBaseMoving), (self.__sessionProvider.dynamic.respawn.onRespawnVisibilityChanged, self.__onRespawnVisibilityChanged))
        return result

    @classmethod
    def _playSoundNotification(cls, sound):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications:
            soundNotifications.play(sound)

    def _playSound(self, sound):
        self.soundManager.playSound(sound)

    def __onOwnSectorsChanged(self, _):
        with self.viewModel.transaction() as tx:
            self.__updateBlockReason(tx, self.__battleController.getCurrentSector())

    def __onQuestChanged(self, questName):
        with self.viewModel.transaction() as tx:
            self.__setQuest(tx, questName)
            if questName and self.__isInOwnLine:
                self._playSoundNotification(EPIC_SOUND.QUESTS_VIEW_NEW)

    def __onQuestProgressChanged(self, value, state):
        with self.viewModel.transaction() as tx:
            self.__setProgress(tx, value, state)

    def __onSectorChanged(self, sectorID):
        with self.viewModel.transaction() as tx:
            self.__updateBlockReason(tx, sectorID)
            self.__currentSectorID = sectorID
            self.__isInOwnLine = self.__battleController.isOnOwnSector()

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        with self.viewModel.transaction() as tx:
            tx.setIsObserver(noRespawnPossible or not respawnAvailable)

    def __onRespawnBaseMoving(self):
        with self.viewModel.transaction() as tx:
            tx.setIsObserver(False)

    def __setProgress(self, tx, value, state):
        tx.setProgressValue(value)
        tx.setIsCompleted(state in STATE.COMPLETED_STATES)
        self._playSound(EPIC_SOUND.QUESTS_VIEW_PROGRESSION)
        if state in STATE.COMPLETED_STATES:
            self._playSoundNotification(EPIC_SOUND.QUESTS_VIEW_COMPLETED)

    def __updateBlockReason(self, tx, sectorID):
        if self.__sessionProvider.shared.vehicleState.isInPostmortem:
            return
        description, direction = self.__getBlockReason(sectorID)
        tx.setBlockDescription(description)
        tx.setDirectionName(direction)
        if self.__currentSectorID > 0 and self.__currentSectorID != sectorID and self.__battleController.getQuest():
            self.__playQuestStateSounds()

    def __getBlockReason(self, sectorID):
        questSectors = self.__battleController.getOwnSectors()
        if not questSectors:
            return (backport.text(R.strings.fl_quests.quest.blocked.description.undefined()), '')
        if sectorID in questSectors:
            return ('', '')
        lineLetters = self.__getLineLetters(questSectors[0])
        return (backport.text(R.strings.fl_quests.quest.blocked.description()), lineLetters) if lineLetters else (backport.text(R.strings.fl_quests.quest.blocked.description.undefined()), '')

    def __playQuestStateSounds(self):
        isInOwnLine = self.__battleController.isOnOwnSector()
        if self.__isInOwnLine != isInOwnLine:
            if isInOwnLine:
                self._playSoundNotification(EPIC_SOUND.QUESTS_VIEW_AVAILABLE)
            else:
                self._playSound(EPIC_SOUND.QUESTS_VIEW_ACTIVATION)
                self._playSoundNotification(EPIC_SOUND.QUESTS_VIEW_NOT_AVAILABLE)

    def __getLineLetters(self, lineID):
        item = 'line{}'.format(lineID)
        lineDyn = R.strings.fl_quests.quest.dyn(item)
        return backport.text(lineDyn()) if lineDyn.isValid() else ''

    def __setQuest(self, tx, questName):
        if questName:
            icon, description, goal = getQuestUiData(questName)
            tx.setIcon(icon)
            tx.setDescription(description)
            tx.setProgressGoal(goal)
            self._playSound(EPIC_SOUND.QUESTS_VIEW_ACTIVATION)
        else:
            tx.setDescription('')
        tx.setProgressValue(0)
        tx.setIsCompleted(False)

    def __onSettingsApplied(self, diff):
        if CONTROLS.KEYBOARD in diff:
            with self.viewModel.transaction() as tx:
                tx.setButtonKey(getReadableKey(CommandMapping.CMD_QUEST_PROGRESS_SHOW))

    def __onRespawnVisibilityChanged(self, isVisible):
        if not isVisible:
            return
        with self.viewModel.transaction() as tx:
            tx.setBlockDescription('')
            tx.setDirectionName('')


class EpicBattleQuestInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        self.__view = EpicBattleQuestsView()
        self.flashObject.visible = False
        return self.__view

    def _onPopulate(self):
        super(EpicBattleQuestInject, self)._onPopulate()
        g_playerEvents.onAvatarReady += self.__onAvatarReady
        self.addListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self._handleToggleFullStatsQuestProgress, EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_STATS, self._handleToggleFullStatsQuestProgress, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self._handleToggleFullStatsQuestProgress, EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_STATS, self._handleToggleFullStatsQuestProgress, EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        super(EpicBattleQuestInject, self)._dispose()

    def _handleToggleFullStatsQuestProgress(self, event):
        if self.app.containerManager.isModalViewsIsExists():
            return
        if self.flashObject:
            self.flashObject.visible = not event.ctx['isDown']

    def __onAvatarReady(self):
        self.flashObject.visible = True
