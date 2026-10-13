# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/shared/clip/controllable_reload_presenter.py
from __future__ import absolute_import
import logging
import typing
from constants import STATIONARY_RELOAD_STATE
from gui.battle_control.battle_constants import SHELL_QUANTITY_UNKNOWN, SHELL_SET_RESULT
from gui.impl.gen.view_models.views.battle.shared.clip.controllable_reload_model import ClipState, ControllableReloadModel
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from helpers.time_utils import secondsToMS
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import IGunReloadingSnapshot, _GunSettings
_logger = logging.getLogger(__name__)

class ControllableReloadPresenter(ViewComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ControllableReloadPresenter, self).__init__(model=ControllableReloadModel)
        self.__clipCapacity = 1

    @property
    def viewModel(self):
        return super(ControllableReloadPresenter, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ControllableReloadPresenter, self)._initialize(*args, **kwargs)
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('ControllableReloadPresenter: AmmoController is not available')
            return
        else:
            gunSettings = ammoCtrl.getGunSettings()
            if gunSettings is not None:
                self.__applyGunSettings(gunSettings)
            quantity, quantityInClip = ammoCtrl.getCurrentShells()
            if (quantity, quantityInClip) != (SHELL_QUANTITY_UNKNOWN, SHELL_QUANTITY_UNKNOWN):
                self.__applyQuantity(quantityInClip)
            stationaryState = ammoCtrl.getStationaryReloadState()
            self.__applyControllableReloadFlag(stationaryState)
            autoReloadState = ammoCtrl.getPartiallyReloadingClipState()
            if autoReloadState is not None:
                self.__applyAutoload(autoReloadState, stationaryState, isSlowed=False)
            return

    def _getEvents(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('ControllableReloadPresenter: AmmoController is not available')
            return ()
        else:
            return ((ammoCtrl.onGunSettingsSet, self.__onGunSettingsSet),
             (ammoCtrl.onShellsUpdated, self.__onShellsUpdated),
             (ammoCtrl.onCurrentShellChanged, self.__onCurrentShellChanged),
             (ammoCtrl.onCurrentShellReset, self.__onCurrentShellReset),
             (ammoCtrl.onGunAutoReloadTimeSet, self.__onGunAutoReloadTimeSet))

    def __onGunSettingsSet(self, gunSettings):
        self.__applyGunSettings(gunSettings)

    def __onShellsUpdated(self, _, __, quantityInClip, result):
        if not result & SHELL_SET_RESULT.CURRENT:
            return
        self.__applyQuantity(quantityInClip)

    def __onCurrentShellChanged(self, _):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            return
        else:
            _, quantityInClip = ammoCtrl.getCurrentShells()
            self.__applyQuantity(quantityInClip)
            return

    def __onCurrentShellReset(self):
        self.__applyQuantity(0)

    def __onGunAutoReloadTimeSet(self, timeState, stationaryState, isSlowed):
        self.__applyControllableReloadFlag(stationaryState)
        self.__applyAutoload(timeState, stationaryState, isSlowed)

    def __applyGunSettings(self, gunSettings):
        self.__clipCapacity = gunSettings.clip.size
        with self.viewModel as model:
            model.setClipCapacity(self.__clipCapacity)

    def __computeClipState(self, quantityInClip):
        if quantityInClip == SHELL_QUANTITY_UNKNOWN:
            return ClipState.NONE
        criticalCount = 1
        return ClipState.CRITICAL if quantityInClip <= criticalCount and self.__clipCapacity > 2 else ClipState.NORMAL

    def __applyQuantity(self, quantityInClip):
        if quantityInClip == SHELL_QUANTITY_UNKNOWN:
            return
        clipState = self.__computeClipState(quantityInClip)
        with self.viewModel as model:
            model.setQuantityInClip(quantityInClip)
            model.setClipState(clipState)

    def __applyControllableReloadFlag(self, stationaryState):
        isInControllableReload = stationaryState is not None and stationaryState != STATIONARY_RELOAD_STATE.IDLE
        with self.viewModel as model:
            model.setIsInControllableReload(isInControllableReload)
        return

    def __applyAutoload(self, snapshot, stationaryState, isSlowed):
        if snapshot is None:
            return
        else:
            actualValue = snapshot.getActualValue()
            baseValue = snapshot.getBaseValue()
            isCritical = bool(isSlowed)
            isTimerOn = stationaryState == STATIONARY_RELOAD_STATE.RELOADING and actualValue > 0.0
            with self.viewModel as model:
                model.setAutoloadTimeLeft(secondsToMS(actualValue))
                model.setAutoloadBaseDuration(secondsToMS(baseValue))
                model.setIsAutoloadCritical(isCritical)
                model.setIsAutoloadTimerOn(isTimerOn)
            return
