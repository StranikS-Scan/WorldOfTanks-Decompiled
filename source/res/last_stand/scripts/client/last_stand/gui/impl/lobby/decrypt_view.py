# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/decrypt_view.py
import typing
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import g_eventBus, events
from last_stand.gui import ls_account_settings
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui.impl.gen.view_models.views.lobby.decrypt_view_model import DecryptViewModel
from last_stand.gui.impl.lobby.ls_helpers import fillRewards
from last_stand.gui.shared.event_dispatcher import showLootBoxMainViewInQueue
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import META_VOICEOVER_UNMUTE, META_VOICEOVER_BUTTON_CLICK_UNMUTE, META_VOICEOVER_MUTE, META_VOICEOVER_BUTTON_CLICK_MUTE, META_QUANTUM_OPEN_SOUND, META_QUANTUM_CLOSE_SOUND, META_QUANTUM_VIDEO_STOP
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_artefacts_controller import Artefact
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
_SOUND_TAG = 'sound'

class DecryptView(ViewImpl):
    _guiLoader = dependency.descriptor(IGuiLoader)
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsCtrl = dependency.descriptor(ILSController)
    _difficultyController = dependency.descriptor(IDifficultyLevelController)
    _MAX_BONUSES_IN_VIEW = 5

    def __init__(self, artefactID, isRewardScreen=False):
        settings = ViewSettings(R.views.last_stand.mono.lobby.decrypt_view())
        settings.model = DecryptViewModel()
        super(DecryptView, self).__init__(settings)
        self.__artefactID = artefactID
        self.__isRewardScreen = isRewardScreen
        self.__bonusCache = {}
        self.__idGen = SequenceIDGenerator()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(DecryptView, self).createToolTip(event)

    @property
    def viewModel(self):
        return super(DecryptView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DecryptView, self)._onLoading()
        self.__fillViewModel()

    def _onShown(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def _finalize(self):
        if self.__isRewardScreen:
            hangarView = self._guiLoader.windowsManager.getViewByLayoutID(R.views.last_stand.mono.lobby.hangar())
            if hangarView is not None:
                hangarView.selectNextSlide()
        if self._isArtefactSoundEnabled():
            artefactIndex = self.lsArtifactsCtrl.getIndex(self.__artefactID)
            playSound(META_QUANTUM_VIDEO_STOP.format(artefactIndex))
            playSound(META_QUANTUM_CLOSE_SOUND.format(artefactIndex))
        super(DecryptView, self)._finalize()
        return

    def _getEvents(self):
        return [(self.viewModel.onAffirmation, self.__onClose), (self.viewModel.onMuted, self.__onMuted)]

    def __onClose(self):
        if self.__isRewardScreen and self.lsArtifactsCtrl.isArtefactHasLootBoxGift(self.__artefactID) and not self.__isSpecificArtefact():
            showLootBoxMainViewInQueue(self.lsCtrl.lootBoxesEvent)
        self.destroyWindow()

    def __onMuted(self):
        isMuted = ls_account_settings.getSettings(AccountSettingsKeys.ARTEFACT_VOICEOVER_MUTED)
        newStateMute = not isMuted
        ls_account_settings.setSettings(AccountSettingsKeys.ARTEFACT_VOICEOVER_MUTED, newStateMute)
        self.viewModel.setIsMuted(newStateMute)
        if newStateMute:
            playSound(META_VOICEOVER_MUTE)
            playSound(META_VOICEOVER_BUTTON_CLICK_MUTE)
        else:
            playSound(META_VOICEOVER_UNMUTE)
            playSound(META_VOICEOVER_BUTTON_CLICK_UNMUTE)

    def __fillViewModel(self):
        artefact = self.lsArtifactsCtrl.getArtefact(self.__artefactID)
        if artefact is None:
            return
        else:
            with self.viewModel.transaction() as tx:
                tx.setId(self.__artefactID)
                tx.setName(artefact.questConditions.name)
                artefactIndex = self.lsArtifactsCtrl.getIndex(self.__artefactID)
                tx.setIndex(artefactIndex)
                tx.setSelectedDifficulty(self._difficultyController.getSelectedLevel())
                tx.setIsTransition(self.__isRewardScreen and self.lsArtifactsCtrl.isArtefactHasLootBoxGift(self.__artefactID) and not self.lsArtifactsCtrl.isFinalArtefact(artefact))
                isMuted = ls_account_settings.getSettings(AccountSettingsKeys.ARTEFACT_VOICEOVER_MUTED)
                tx.setIsMuted(isMuted)
                if self._isArtefactSoundEnabled():
                    if isMuted:
                        playSound(META_VOICEOVER_MUTE)
                    else:
                        playSound(META_VOICEOVER_UNMUTE)
                    playSound(META_QUANTUM_OPEN_SOUND.format(artefactIndex))
                self.__bonusCache = fillRewards(artefact.bonusRewards, tx.getRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen)
                for type in artefact.artefactTypes:
                    tx.getTypes().addString(type)

                tx.getTypes().invalidate()
            return

    def __isSpecificArtefact(self):
        artefact = self.lsArtifactsCtrl.getArtefact(self.__artefactID)
        if not artefact:
            return False
        isFinalArtefact = self.lsArtifactsCtrl.isFinalArtefact(artefact) if artefact else False
        isKingRewardArtefact = self.lsArtifactsCtrl.isKingRewardArtefact(artefact) if artefact else False
        return isFinalArtefact or isKingRewardArtefact

    def _isArtefactSoundEnabled(self):
        artefact = self.lsArtifactsCtrl.getArtefact(self.__artefactID)
        return False if artefact is None else _SOUND_TAG in artefact.artefactTypes


class DecryptWindow(LobbyNotificationWindow):

    def __init__(self, artefactID, isRewardScreen=None, parent=None):
        super(DecryptWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=DecryptView(artefactID, isRewardScreen), parent=parent)
        self._args = (artefactID, isRewardScreen)

    def isParamsEqual(self, *args):
        return self._args == args
