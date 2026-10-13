# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/shared/clip/auto_loader_clip_presenter.py
from __future__ import absolute_import
import logging
import typing
from gui.battle_control.battle_constants import SHELL_QUANTITY_UNKNOWN, SHELL_SET_RESULT
from gui.battle_control.controllers.consumables.ammo_ctrl import AutoReloadingBoostStates
from gui.impl.gen.view_models.views.battle.shared.clip.auto_loader_clip_model import AutoLoaderClipModel, BoostState
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from helpers.time_utils import secondsToMS
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.battle_control.controllers.consumables.ammo_ctrl import IGunReloadingSnapshot, _GunSettings
_logger = logging.getLogger(__name__)
_BOOST_STATE_MAP = {AutoReloadingBoostStates.UNAVAILABLE: BoostState.UNAVAILABLE,
 AutoReloadingBoostStates.INAPPLICABLE: BoostState.INAPPLICABLE,
 AutoReloadingBoostStates.WAITING_FOR_START: BoostState.WAITINGFORSTART,
 AutoReloadingBoostStates.CHARGING: BoostState.CHARGING,
 AutoReloadingBoostStates.CHARGED: BoostState.CHARGED}

class AutoLoaderClipPresenter(ViewComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AutoLoaderClipPresenter, self).__init__(model=AutoLoaderClipModel)
        self.__clipCapacity = 1
        self.__shellsInClip = 0

    @property
    def viewModel(self):
        return super(AutoLoaderClipPresenter, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(AutoLoaderClipPresenter, self)._initialize(*args, **kwargs)
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('AutoLoaderClipPresenter: AmmoController is not available')
            return
        else:
            gunSettings = ammoCtrl.getGunSettings()
            if gunSettings is not None:
                self.__applyGunSettings(gunSettings)
            quantity, quantityInClip = ammoCtrl.getCurrentShells()
            if (quantity, quantityInClip) != (SHELL_QUANTITY_UNKNOWN, SHELL_QUANTITY_UNKNOWN):
                self.__shellsInClip = quantityInClip
                self.__applyQuantity(quantityInClip)
            self.__applyShellLoading(ammoCtrl.getGunReloadingState())
            self.__applyAutoload(ammoCtrl.getPartiallyReloadingClipState(), stunned=False)
            return

    def _getEvents(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('AutoLoaderClipPresenter: AmmoController is not available')
            return ()
        else:
            return ((ammoCtrl.onGunSettingsSet, self.__onGunSettingsSet),
             (ammoCtrl.onShellsUpdated, self.__onShellsUpdated),
             (ammoCtrl.onCurrentShellChanged, self.__onCurrentShellChanged),
             (ammoCtrl.onCurrentShellReset, self.__onCurrentShellReset),
             (ammoCtrl.onGunReloadTimeSet, self.__onGunReloadTimeSet),
             (ammoCtrl.onShellsCleared, self.__onShellsCleared),
             (ammoCtrl.onGunAutoReloadTimeSet, self.__onGunAutoReloadTimeSet),
             (ammoCtrl.onGunAutoReloadBoostUpdated, self.__onBoostUpdated))

    def __onGunSettingsSet(self, gunSettings):
        self.__applyGunSettings(gunSettings)

    def __onShellsUpdated(self, intCD, quantity, quantityInClip, result):
        if not result & SHELL_SET_RESULT.CURRENT:
            return
        self.__shellsInClip = quantityInClip
        self.__applyQuantity(quantityInClip)

    def __onCurrentShellChanged(self, intCD):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            return
        else:
            _, quantityInClip = ammoCtrl.getCurrentShells()
            self.__shellsInClip = quantityInClip
            self.__applyQuantity(quantityInClip)
            return

    def __onCurrentShellReset(self):
        self.__shellsInClip = 0
        self.__applyQuantity(0)

    def __onGunReloadTimeSet(self, _, state, skipAutoLoader):
        if skipAutoLoader:
            return
        self.__applyShellLoading(state)

    def __onShellsCleared(self, state):
        self.__applyShellLoading(state)

    def __onGunAutoReloadTimeSet(self, timeState, _, stunned):
        self.__applyAutoload(timeState, stunned)

    def __onBoostUpdated(self, state, stateDuration, stateTotalTime, _):
        self.__applyBoost(state, stateDuration, stateTotalTime)

    def __applyGunSettings(self, gunSettings):
        self.__clipCapacity = gunSettings.clip.size
        with self.viewModel as model:
            model.setClipCapacity(self.__clipCapacity)

    def __applyQuantity(self, quantityInClip):
        if quantityInClip == SHELL_QUANTITY_UNKNOWN:
            return
        with self.viewModel as model:
            model.setQuantityInClip(quantityInClip)
            model.setIsTimerRed(quantityInClip == 0)

    def __applyShellLoading(self, snapshot):
        if snapshot is None:
            return
        else:
            actualValue = snapshot.getActualValue()
            baseValue = snapshot.getBaseValue()
            with self.viewModel as model:
                model.setShellLoadingTimeLeft(secondsToMS(actualValue))
                model.setShellLoadingBaseDuration(secondsToMS(baseValue))
            return

    def __applyAutoload(self, snapshot, stunned):
        if snapshot is None:
            return
        else:
            actualValue = snapshot.getActualValue()
            baseValue = snapshot.getBaseValue()
            isCritical = bool(stunned)
            with self.viewModel as model:
                model.setAutoloadTimeLeft(secondsToMS(actualValue))
                model.setAutoloadBaseDuration(secondsToMS(baseValue))
                model.setIsAutoloadCritical(isCritical)
                model.setIsAutoloadTimerOn(True)
                model.setIsTimerRed(self.__shellsInClip == 0)
            return

    def __applyBoost(self, state, stateDuration, stateTotalTime):
        boostState = _BOOST_STATE_MAP.get(state, BoostState.UNAVAILABLE)
        isApplicable = state not in AutoReloadingBoostStates.NOT_ACTIVE
        with self.viewModel as model:
            model.setBoostState(boostState)
            model.setBoostTimeLeft(secondsToMS(stateDuration, 0.0))
            model.setBoostTotalTime(secondsToMS(stateTotalTime, 0.0))
            model.setIsBoostApplicable(isApplicable)
