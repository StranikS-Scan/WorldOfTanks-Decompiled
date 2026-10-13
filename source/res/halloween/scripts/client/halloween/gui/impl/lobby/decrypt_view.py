# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/decrypt_view.py
from __future__ import absolute_import
import typing
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from halloween.gui import halloween_account_settings
from halloween.gui.halloween_account_settings import AccountSettingsKeys
from halloween.gui.impl.gen.view_models.views.lobby.decrypt_view_model import DecryptViewModel
from halloween.gui.impl.lobby.hw_helpers import fillRewards
from halloween.gui.impl.lobby.tooltips.vehicle_tooltip import VehicleTooltipView
from halloween.gui.shared.event_dispatcher import showOutroVideo, showDecryptWindowView
from halloween.gui.shared.events import HWHangarEvent
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import META_QUANTUM_VO_ON, META_QUANTUM_VO_OFF, META_QUANTUM_SCREEN_ENTER, META_QUANTUM_SCREEN_EXIT
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_bestiary_controller import IHalloweenBestiaryController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.uilogging.loggers import DecryptionMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys
from helpers import dependency
from ids_generators import SequenceIDGenerator
from halloween_common.halloween_constants import HWStoryChoiceSettings
if typing.TYPE_CHECKING:
    from halloween.gui.game_control.halloween_artefacts_controller import Artefact
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
_SOUND_TAG = 'sound'

class DecryptView(ViewImpl):
    _hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwBestiaryCtrl = dependency.descriptor(IHalloweenBestiaryController)
    _hwController = dependency.descriptor(IHalloweenController)
    _MAX_BONUSES_IN_VIEW = 5

    def __init__(self, artefactID, isRewardScreen=False, disableOutro=False, disableLastArtefact=False):
        settings = ViewSettings(R.views.halloween.mono.lobby.decrypt())
        settings.model = DecryptViewModel()
        super(DecryptView, self).__init__(settings)
        self.__artefactID = artefactID
        self.__isOutroDisabled = disableOutro
        self.__isLastArtefactDisabled = disableLastArtefact
        self.__isRewardScreen = isRewardScreen
        self.__bonusCache = {}
        self.__idGen = SequenceIDGenerator()
        self.__decryptUILogger = DecryptionMetricsLogger()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(DecryptView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.mono.lobby.tooltips.vehicle_tooltip():
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            vehicleCD = bonus.specialArgs[0]
            return VehicleTooltipView(vehicleCD=vehicleCD)
        return super(DecryptView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(DecryptView, self).getViewModel()

    @property
    def isMuted(self):
        return halloween_account_settings.getSettings(AccountSettingsKeys.ARTEFACT_VOICEOVER_MUTED)

    def _onLoading(self, *args, **kwargs):
        super(DecryptView, self)._onLoading()
        artefactIndex = self._hwArtefactsCtrl.getIndex(self.__artefactID)
        playSound(META_QUANTUM_SCREEN_ENTER.format(artefactIndex))
        self.__fillViewModel()

    def _onShown(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def _finalize(self):
        artefactIndex = self._hwArtefactsCtrl.getIndex(self.__artefactID)
        playSound(META_QUANTUM_SCREEN_EXIT.format(artefactIndex))
        if self.__isRewardScreen:
            self._hwArtefactsCtrl.needSelectNextSlide = True
        else:
            g_eventBus.handleEvent(HWHangarEvent(HWHangarEvent.REFRESH), EVENT_BUS_SCOPE.LOBBY)
        self.__decryptUILogger.onStopView(self.__artefactID, not self.isMuted)
        super(DecryptView, self)._finalize()

    def _getEvents(self):
        return [(self.viewModel.onAffirmation, self.__onClose),
         (self.viewModel.onMuted, self.__onMuted),
         (self.viewModel.onOutroVideo, self.__onOutroVideo),
         (self.viewModel.onChangeQuest, self.__onChangeQuest)]

    def __onClose(self):
        self.destroyWindow()

    def __onOutroVideo(self):
        showOutroVideo(callbackOnClose=lambda : showDecryptWindowView(self.__artefactID))

    def __onMuted(self):
        newStateMute = not self.isMuted
        halloween_account_settings.setSettings(AccountSettingsKeys.ARTEFACT_VOICEOVER_MUTED, newStateMute)
        self.viewModel.setIsMuted(newStateMute)
        artefactIndex = self._hwArtefactsCtrl.getIndex(self.__artefactID)
        if newStateMute:
            playSound(META_QUANTUM_VO_OFF.format(artefactIndex))
            self.__decryptUILogger.stopVO(self.__artefactID)
        else:
            playSound(META_QUANTUM_VO_ON.format(artefactIndex))
            self.__decryptUILogger.startVO()

    def __onChangeQuest(self, args):
        newIndex = int(args['index'])
        artefactIndex = self._hwArtefactsCtrl.getIndex(self.__artefactID)
        playSound(META_QUANTUM_SCREEN_EXIT.format(artefactIndex))
        maxIndex = self._hwArtefactsCtrl.getArtefactsCount()
        if newIndex < 0 or newIndex > maxIndex:
            return
        else:
            if newIndex == maxIndex:
                finalArtefact = self._hwArtefactsCtrl.getFinalArtefact()
                if finalArtefact is None:
                    return
                newArtefactId = finalArtefact.artefactID
            else:
                newArtefactId = self._hwArtefactsCtrl.getArtefactIDByIndex(newIndex)
            if newArtefactId is None or not self._hwArtefactsCtrl.isArtefactOpened(newArtefactId):
                return
            self.__decryptUILogger.onStopView(self.__artefactID, not self.isMuted)
            self.__decryptUILogger.onClick(HWLogKeys.ARROW, self.__artefactID)
            self.__artefactID = newArtefactId
            if not self.__isRewardScreen:
                self._hwArtefactsCtrl.selectedArtefactID = self.__artefactID
            self.__fillViewModel()
            return

    def __isPreviousArtefactAvailable(self, artefactIndex):
        artefact = self._hwArtefactsCtrl.getArtefact(self.__artefactID)
        if artefact and self._hwArtefactsCtrl.isFinalArtefact(artefact):
            lastRegularIndex = self._hwArtefactsCtrl.getArtefactsCount() - 1
            previousArtefactId = self._hwArtefactsCtrl.getArtefactIDByIndex(lastRegularIndex)
            return previousArtefactId is not None and self._hwArtefactsCtrl.isArtefactOpened(previousArtefactId)
        elif artefactIndex <= 0:
            return False
        else:
            previousArtefactId = self._hwArtefactsCtrl.getArtefactIDByIndex(artefactIndex - 1)
            return previousArtefactId is not None and self._hwArtefactsCtrl.isArtefactOpened(previousArtefactId)

    def __isNextArtefactAvailable(self, artefactIndex):
        artefact = self._hwArtefactsCtrl.getArtefact(self.__artefactID)
        if artefact and self._hwArtefactsCtrl.isFinalArtefact(artefact):
            return False
        else:
            maxIndex = self._hwArtefactsCtrl.getArtefactsCount()
            if artefactIndex == maxIndex - 1:
                finalArtefact = self._hwArtefactsCtrl.getFinalArtefact()
                if finalArtefact and not self.__isLastArtefactDisabled:
                    return self._hwArtefactsCtrl.isArtefactOpened(finalArtefact.artefactID)
                return False
            if artefactIndex >= maxIndex:
                return False
            nextArtefactId = self._hwArtefactsCtrl.getArtefactIDByIndex(artefactIndex + 1)
            return nextArtefactId is not None and self._hwArtefactsCtrl.isArtefactOpened(nextArtefactId)

    def __fillViewModel(self):
        artefact = self._hwArtefactsCtrl.getArtefact(self.__artefactID)
        if artefact is None:
            return
        else:
            isArtefactSoundEnabled = self._isArtefactSoundEnabled()
            isVoiceEnable = isArtefactSoundEnabled and not self.isMuted
            self.__decryptUILogger.onStartView()
            if isVoiceEnable:
                self.__decryptUILogger.startVO()
            with self.viewModel.transaction() as tx:
                tx.setId(self.__artefactID)
                tx.setName(artefact.questConditions.name)
                artefactIndex = self._hwArtefactsCtrl.getIndex(self.__artefactID)
                tx.setIndex(artefactIndex)
                tx.setIsMuted(self.isMuted)
                tx.setIsOutroDisabled(self.__isOutroDisabled)
                tx.setIsOutroVisible(self._hwController.isOutroVideoEnabled())
                if isVoiceEnable:
                    playSound(META_QUANTUM_VO_ON.format(artefactIndex))
                tx.setIsTransition(self.__isRewardScreen and (self._hwArtefactsCtrl.isArtefactHasTwitchConCertificate(self.__artefactID) or len(self._hwArtefactsCtrl.getRareAttachmentsFromArtefact(self.__artefactID)) > 0 or self._hwArtefactsCtrl.isProgressCompleted() or self._hwArtefactsCtrl.isFinalArtefact(artefact) or self._hwBestiaryCtrl.hasEnemy(self._hwArtefactsCtrl.getOpenedArtefactToken(self.__artefactID))))
                tx.setIsPreviousArtefactAvailable(self.__isPreviousArtefactAvailable(artefactIndex))
                tx.setIsNextArtefactAvailable(self.__isNextArtefactAvailable(artefactIndex))
                tx.getRewards().clear()
                self.__bonusCache = fillRewards(artefact, tx.getRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen, skipBonusNames=[HWStoryChoiceSettings.MEDAL_BONUS_NAME])
                artifactTypes = tx.getTypes()
                artifactTypes.clear()
                for type in artefact.artefactTypes:
                    artifactTypes.addString(type)

                artifactTypes.invalidate()
            return

    def _isArtefactSoundEnabled(self):
        artefact = self._hwArtefactsCtrl.getArtefact(self.__artefactID)
        return False if artefact is None else _SOUND_TAG in artefact.artefactTypes


class DecryptWindow(LobbyNotificationWindow):

    def __init__(self, artefactID, isRewardScreen=None, disableOutro=False, disableLastArtefact=False, parent=None):
        super(DecryptWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=DecryptView(artefactID, isRewardScreen, disableOutro, disableLastArtefact), parent=parent)
        self._args = (artefactID, isRewardScreen)

    def isParamsEqual(self, *args):
        return self._args == args
