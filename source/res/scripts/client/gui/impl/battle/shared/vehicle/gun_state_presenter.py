# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/shared/vehicle/gun_state_presenter.py
from __future__ import absolute_import
import logging
import typing
import BigWorld
from gui.battle_control.battle_constants import SHELL_SET_RESULT
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.shared.gun_state_model import GunStateModel, GunType, ReloadStatus, ReloadType
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from helpers.time_utils import secondsToMS
from items.vehicle_mechanics_types import VehicleMechanicKeys
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import IGunReloadingSnapshot, _GunSettings
_logger = logging.getLogger(__name__)
_RELOAD_ALIAS_BY_TYPE = {ReloadType.AUTOLOADERCLIP: R.aliases.battle.shared.clip.auto_loader(),
 ReloadType.EXTRASHOTCLIP: R.aliases.battle.shared.clip.extra_shot(),
 ReloadType.CONTROLLABLERELOAD: R.aliases.battle.shared.clip.controllable_reload(),
 ReloadType.UNLIMITEDCLIP: R.aliases.battle.shared.clip.unlimited(),
 ReloadType.SHELLCALIBRATIONCLIP: R.aliases.battle.shared.clip.shell_calibration(),
 ReloadType.CASSETTECLIP: R.aliases.battle.shared.clip.cassette()}

class GunStatePresenter(ViewComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(GunStatePresenter, self).__init__(model=GunStateModel)
        self.__reloadingType = None
        return

    @property
    def viewModel(self):
        return super(GunStatePresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(GunStatePresenter, self)._onLoading(*args, **kwargs)
        ammo = self.__sessionProvider.shared.ammo
        if ammo is None:
            return
        else:
            gunSettings = ammo.getGunSettings()
            if gunSettings is None or gunSettings.vehicleID == 0:
                self.__resetModel()
                return
            self.__applyGunSettings(gunSettings)
            self.__applyReloadState(ammo.getGunReloadingState())
            if self.viewModel is None:
                return
            with self.viewModel as model:
                quantity, _ = ammo.getCurrentShells()
                if quantity >= 0:
                    model.setCurrentShellQuantity(quantity)
                model.setIsShotAvailable(ammo.isShootPossible())
            return

    def _getEvents(self):
        ammo = self.__sessionProvider.shared.ammo
        if ammo is None:
            return ()
        else:
            vehicleCtrl = self.__sessionProvider.shared.vehicleState
            return () if vehicleCtrl is None else ((ammo.onGunSettingsSet, self.__onGunSettingsSet),
             (ammo.onGunReloadTimeSet, self.__onGunReloadTimeSet),
             (ammo.onShellsUpdated, self.__onShellsUpdated),
             (ammo.onShellsCleared, self.__onShellsCleared),
             (ammo.onCurrentShellChanged, self.__onCurrentShellChanged),
             (vehicleCtrl.onPostMortemSwitched, self.__onSwitchToPostmortem))

    def _finalize(self):
        self.__reloadingType = None
        super(GunStatePresenter, self)._finalize()
        return

    def __onGunSettingsSet(self, gunSettings):
        if gunSettings is None or gunSettings.vehicleID == 0:
            self.__resetModel()
            return
        else:
            reloadingType = self.__resolveReloadingType(gunSettings)
            if self.__reloadingType is None:
                self.__reloadingType = reloadingType
                self.__setUpPresenter(reloadingType)
            elif reloadingType != self.__reloadingType:
                self.__disablePresenter(self.__reloadingType)
                self.__reloadingType = reloadingType
                if reloadingType != ReloadType.STANDARD:
                    self.__setUpPresenter(reloadingType)
            self.__applyGunSettings(gunSettings)
            return

    def __setUpPresenter(self, reloadingType):
        alias = _RELOAD_ALIAS_BY_TYPE.get(reloadingType)
        if alias is None:
            return
        elif reloadingType == ReloadType.SHELLCALIBRATIONCLIP and not self.__sessionProvider.arenaVisitor.extra.isGfHudMechanicEnabled(VehicleMechanicKeys.SHELL_CALIBRATION):
            return
        else:
            child = self.getChildByPosId(alias)
            if child is not None:
                child.setEnabled(True)
                return
            self._constructChild(alias, None)
            return

    def __disablePresenter(self, reloadingType):
        alias = _RELOAD_ALIAS_BY_TYPE.get(reloadingType)
        if alias is None:
            return
        else:
            child = self.getChildByPosId(alias)
            if child is None:
                return
            child.setEnabled(False)
            return

    def __onGunReloadTimeSet(self, _, state, __):
        self.__applyReloadState(state)
        ammo = self.__sessionProvider.shared.ammo
        if ammo is None:
            return
        else:
            with self.viewModel as model:
                model.setIsShotAvailable(ammo.isShootPossible())
            return

    def __onShellsUpdated(self, intCD, quantity, quantityInClip, result):
        ammo = self.__sessionProvider.shared.ammo
        if ammo is None:
            return
        else:
            with self.viewModel as model:
                if result & SHELL_SET_RESULT.CURRENT and quantity >= 0:
                    model.setCurrentShellQuantity(quantity)
                model.setIsShotAvailable(ammo.isShootPossible())
            return

    def __onShellsCleared(self, state):
        ammo = self.__sessionProvider.shared.ammo
        if ammo is None:
            return
        else:
            gunSettings = ammo.getGunSettings()
            if gunSettings is None or gunSettings.vehicleID == 0:
                self.__resetModel()
                return
            self.__applyReloadState(state)
            with self.viewModel as model:
                model.setIsShotAvailable(ammo.isShootPossible())
            return

    def __onCurrentShellChanged(self, intCD):
        ammo = self.__sessionProvider.shared.ammo
        if ammo is None:
            return
        else:
            quantity, _ = ammo.getCurrentShells()
            with self.viewModel as model:
                if quantity >= 0:
                    model.setCurrentShellQuantity(quantity)
                model.setIsShotAvailable(ammo.isShootPossible())
            return

    def __resetModel(self):
        if self.viewModel is None:
            return
        else:
            with self.viewModel as model:
                model.setGunType(GunType.SIMPLE)
                model.setReloadMechanicType(ReloadType.STANDARD)
                model.setReloadStatus(ReloadStatus.READY)
                model.setCurrentShellQuantity(-1)
                model.setIsShotAvailable(False)
                model.reloadTimer.setDuration(0.0)
                model.reloadTimer.setElapsed(0.0)
                model.reloadTimer.setStartTimestamp(0)
            return

    def __applyGunSettings(self, gunSettings):
        gunType = self.__resolveGunType(gunSettings)
        reloadMechanicType = self.__resolveReloadingType(gunSettings)
        with self.viewModel as model:
            model.setGunType(gunType)
            model.setReloadMechanicType(reloadMechanicType)

    def __applyReloadState(self, snapshot):
        if self.viewModel is None or snapshot is None:
            return
        else:
            actualValue = snapshot.getActualValue()
            if actualValue == -1:
                status = ReloadStatus.EMPTY
            elif snapshot.isReloadingFinished():
                status = ReloadStatus.READY
            else:
                status = ReloadStatus.RELOADING
            duration = snapshot.getBaseValue()
            elapsed = duration - actualValue if actualValue > 0 else 0.0
            with self.viewModel as model:
                model.setReloadStatus(status)
                model.reloadTimer.setDuration(secondsToMS(duration))
                model.reloadTimer.setElapsed(secondsToMS(elapsed))
                model.reloadTimer.setStartTimestamp(int(secondsToMS(BigWorld.time() - elapsed)))
            return

    def __onSwitchToPostmortem(self, _, __):
        if self.__reloadingType is not None:
            self.__disablePresenter(self.__reloadingType)
        return

    @staticmethod
    def __resolveGunType(gunSettings):
        if gunSettings.isDualGun:
            return GunType.DUALGUN
        if gunSettings.isControllableReload:
            return GunType.CONTROLLABLE
        return GunType.AUTORELOAD if gunSettings.hasAutoReload() else GunType.SIMPLE

    @staticmethod
    def __resolveReloadingType(gunSettings):
        if gunSettings.hasAutoReload():
            return ReloadType.AUTOLOADERCLIP
        if gunSettings.hasExtraShot():
            return ReloadType.EXTRASHOTCLIP
        if gunSettings.isControllableReload:
            return ReloadType.CONTROLLABLERELOAD
        if gunSettings.isUnlimitedClip:
            return ReloadType.UNLIMITEDCLIP
        if gunSettings.isShellCalibration:
            return ReloadType.SHELLCALIBRATIONCLIP
        return ReloadType.CASSETTECLIP if gunSettings.isCassetteClip else ReloadType.STANDARD
