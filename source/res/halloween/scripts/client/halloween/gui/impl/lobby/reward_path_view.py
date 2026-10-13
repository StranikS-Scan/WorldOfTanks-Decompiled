# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/reward_path_view.py
from __future__ import absolute_import
import typing
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.shared.event_dispatcher import showVehicleHubOverview
from halloween.gui.impl.gen.view_models.views.lobby.reward_path_item_view_model import RewardPathItemViewModel
from halloween.gui.impl.lobby.gsw_cards.key_card_presenter import KeyCardPresenter
from halloween.gui.impl.lobby.gsw_cards.quests_card_presenter import QuestsCardPresenter
from halloween.gui.impl.lobby.hw_helpers import getArtefactState, fillRewards, fillGiftVehicleModel
from halloween.gui.impl.lobby.base_view import SwitcherPresenter
from halloween.gui.impl.lobby.tooltips.event_mission_tooltip import MissionsTooltip
from halloween.gui.impl.lobby.tooltips.vehicle_tooltip import VehicleTooltipView
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import REWARD_PATH_EXIT, REWARD_PATH_ENTER
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.skeletons.halloween_twitch_con_controller import IHalloweenTwitchConController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys
from ids_generators import SequenceIDGenerator
from CurrentVehicle import g_currentPreviewVehicle
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.shared import g_eventBus, events
from halloween.gui.impl.gen.view_models.views.lobby.reward_path_view_model import RewardPathViewModel
from halloween.gui.impl.lobby.widgets.crew_members_flag import CrewMembersFlag
from halloween.gui.shared.event_dispatcher import showTwitchConExchangeView, showMetaIntroView
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from helpers import dependency
if typing.TYPE_CHECKING:
    from halloween.gui.game_control.halloween_artefacts_controller import Artefact
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class RewardPathView(ViewComponent[RewardPathViewModel]):
    _hwController = dependency.descriptor(IHalloweenController)
    _hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwTwitchConCtrl = dependency.descriptor(IHalloweenTwitchConController)
    _MAX_BONUSES_IN_VIEW = 3

    def __init__(self, *args, **kwargs):
        super(RewardPathView, self).__init__(R.views.halloween.mono.lobby.reward_path(), RewardPathViewModel, *args, **kwargs)
        self.__bonusCache = {}
        self.__idGen = SequenceIDGenerator()
        self.__uiLogger = HWMetricsLogger(HWLogKeys.REWARD_PATH_VIEW)

    @property
    def viewModel(self):
        return super(RewardPathView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(RewardPathView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.mono.lobby.tooltips.mission_tooltip():
            artefactID = event.getArgument('artefactID', '')
            return MissionsTooltip(selectedArtefactID=artefactID, isHangar=False)
        if contentID == R.views.halloween.mono.lobby.tooltips.vehicle_tooltip():
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            vehicleCD = bonus.specialArgs[0]
            return VehicleTooltipView(vehicleCD=vehicleCD)
        return super(RewardPathView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return [(self.viewModel.onPreview, self.__onPreview),
         (self.viewModel.onViewLoaded, self.__onViewLoaded),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.goToMission, self.__goToMission),
         (self.viewModel.goToCrewSelect, self.__goToCrewSelect),
         (self._hwArtefactsCtrl.onArtefactSettingsUpdated, self.__fillArtefacts),
         (self._hwTwitchConCtrl.onCertificateCountUpdated, self.__fillArtefacts),
         (self._hwTwitchConCtrl.onLimitsUpdated, self.__fillArtefacts)]

    def _onLoading(self, *args, **kwargs):
        super(RewardPathView, self)._onLoading()
        self.__fillGiftVehicle()
        self.__fillArtefacts()

    def _getChildComponents(self):
        halloween = R.aliases.halloween.shared
        return {halloween.CrewMembers(): CrewMembersFlag,
         halloween.Keys(): lambda : KeyCardPresenter(HWLogKeys.REWARD_PATH_UMG_WIDGET),
         halloween.Quests(): QuestsCardPresenter,
         halloween.Switcher(): SwitcherPresenter}

    def _onLoaded(self, *args, **kwargs):
        super(RewardPathView, self)._onLoaded(*args, **kwargs)
        if g_currentPreviewVehicle is not None:
            g_currentPreviewVehicle.selectNoVehicle()
        return

    def _initialize(self, *args, **kwargs):
        super(RewardPathView, self)._initialize(*args, **kwargs)
        playSound(REWARD_PATH_ENTER)
        showMetaIntroView(forceOpen=False, parent=self.getParentWindow())

    def _finalize(self):
        playSound(REWARD_PATH_EXIT)
        super(RewardPathView, self)._finalize()

    def __goToMission(self, args):
        artefactID = args.get('artefactID', None)
        if artefactID is not None:
            self.__uiLogger.onClick(HWLogKeys.THUMBNAIL, artefactID)
            self._hwArtefactsCtrl.selectedArtefactID = artefactID
            self.__onClose()
        return

    def __goToCrewSelect(self):
        showTwitchConExchangeView(useQueue=False)

    def __fillArtefacts(self):
        availableCertInArtefacts = self.__getArtefactsIDsWithReceivedCert()
        with self.viewModel.transaction() as tx:
            artefacts = tx.getArtefacts()
            artefacts.clear()
            if self._hwArtefactsCtrl.selectedArtefactID is not None:
                tx.setSelectedArtefactID(self._hwArtefactsCtrl.selectedArtefactID)
            currentProgress = self._hwArtefactsCtrl.getCurrentArtefactProgress()
            maxProgress = self._hwArtefactsCtrl.getMaxArtefactsProgress()
            tx.setIsCompleted(currentProgress >= maxProgress)
            tx.setProgress(maxProgress - currentProgress)
            self.__bonusCache = {}
            for artefact in self._hwArtefactsCtrl.artefactsSorted():
                artefactVM = RewardPathItemViewModel()
                artefactVM.setId(artefact.artefactID)
                artefactVM.setIndex(self._hwArtefactsCtrl.getIndex(artefact.artefactID))
                artefactVM.setState(getArtefactState(artefact.artefactID))
                artefactVM.getTypes().clear()
                for type in artefact.artefactTypes:
                    artefactVM.getTypes().addString(type)

                artefactVM.getRewards().clear()
                isRewardNeedHighlight = artefact.artefactID in availableCertInArtefacts
                self.__bonusCache.update(fillRewards(artefact, artefactVM.getRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen, rewardsHighlight=['cerfToken'] if isRewardNeedHighlight else []))
                artefactVM.setIsClaimVisible(isRewardNeedHighlight)
                artefacts.addViewModel(artefactVM)

            artefacts.invalidate()
        return

    def __fillGiftVehicle(self):
        with self.viewModel.transaction() as tx:
            vehGift = tx.mainGiftVehicle
            fillGiftVehicleModel(vehGift)

    def __onPreview(self):
        vehicle = self._hwArtefactsCtrl.getMainGiftVehicle()
        if vehicle is not None:
            showVehicleHubOverview(vehicle.intCD)
        return

    def __onClose(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def __getArtefactsIDsWithReceivedCert(self):
        artefactsList = set()
        countCerts = self._hwTwitchConCtrl.getCertificateCount()
        for artefact in reversed(self._hwArtefactsCtrl.artefactsSorted()):
            if self._hwArtefactsCtrl.isArtefactOpened(artefact.artefactID) and self._hwArtefactsCtrl.isArtefactHasTwitchConCertificate(artefact.artefactID) and countCerts > 0:
                artefactsList.add(artefact.artefactID)
                countCerts -= 1
            if countCerts <= 0:
                break

        return artefactsList


class RewardPathWindow(WindowImpl):

    def __init__(self, layer, *args, **kwargs):
        super(RewardPathWindow, self).__init__(content=RewardPathView(*args, **kwargs), wndFlags=WindowFlags.WINDOW, layer=layer)
