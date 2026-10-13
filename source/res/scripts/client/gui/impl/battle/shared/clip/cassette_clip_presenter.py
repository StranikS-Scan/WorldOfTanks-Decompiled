# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/shared/clip/cassette_clip_presenter.py
from __future__ import absolute_import, division
import logging
import math
import typing
from gui.battle_control.battle_constants import SHELL_SET_RESULT, SHELL_QUANTITY_UNKNOWN
from gui.impl.gen.view_models.views.battle.shared.clip.cassette_clip_model import CassetteClipModel, ClipState
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController, _GunSettings
_logger = logging.getLogger(__name__)

class CassetteClipPresenter(ViewComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CassetteClipPresenter, self).__init__(model=CassetteClipModel)
        self.__clipCapacity = 1
        self.__burstSize = 1

    @property
    def viewModel(self):
        return super(CassetteClipPresenter, self).getViewModel()

    def _initialize(self):
        super(CassetteClipPresenter, self)._initialize()
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('CassetteClipPresenter._initialize: AmmoController is not available')
            return
        else:
            gunSettings = ammoCtrl.getGunSettings()
            if gunSettings is not None:
                self.__applyGunSettings(gunSettings)
            quantity, quantityInClip = ammoCtrl.getCurrentShells()
            if (quantity, quantityInClip) != (SHELL_QUANTITY_UNKNOWN, SHELL_QUANTITY_UNKNOWN):
                state = self.__computeClipState(quantityInClip)
                self.__applyAmmoStock(quantityInClip, state, clipReloaded=False)
            return

    def _getEvents(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('CassetteClipPresenter._getEvents: AmmoController is not available')
            return ()
        else:
            return ((ammoCtrl.onGunSettingsSet, self.__onGunSettingsSet),
             (ammoCtrl.onShellsUpdated, self.__onShellsUpdated),
             (ammoCtrl.onCurrentShellChanged, self.__onCurrentShellChanged),
             (ammoCtrl.onCurrentShellReset, self.__onCurrentShellReset))

    def __onGunSettingsSet(self, gunSettings):
        self.__applyGunSettings(gunSettings)

    def __onShellsUpdated(self, intCD, quantity, quantityInClip, result):
        if not result & SHELL_SET_RESULT.CURRENT:
            return
        state = self.__computeClipState(quantityInClip)
        clipReloaded = bool(result & SHELL_SET_RESULT.CASSETTE_RELOAD)
        self.__applyAmmoStock(quantityInClip, state, clipReloaded)

    def __onCurrentShellChanged(self, _):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            return
        else:
            _, quantityInClip = ammoCtrl.getCurrentShells()
            state = self.__computeClipState(quantityInClip)
            self.__applyAmmoStock(quantityInClip, state, clipReloaded=False)
            return

    def __onCurrentShellReset(self):
        self.__applyAmmoStock(0, ClipState.NORMAL, clipReloaded=False)

    def __applyGunSettings(self, gunSettings):
        self.__clipCapacity = gunSettings.clip.size
        self.__burstSize = gunSettings.burst.size
        with self.viewModel as model:
            model.setClipCapacity(self.__clipCapacity)
            model.setBurst(self.__burstSize)

    def __computeClipState(self, quantityInClip):
        if quantityInClip == SHELL_QUANTITY_UNKNOWN:
            return ClipState.NONE
        burstSize = self.__burstSize
        clipCapacity = self.__clipCapacity
        if burstSize > 1:
            total = int(math.ceil(clipCapacity / float(burstSize)))
            current = int(math.ceil(quantityInClip / float(burstSize)))
        else:
            total = clipCapacity
            current = quantityInClip
        criticalCount = 1
        return ClipState.CRITICAL if current <= criticalCount and total > 2 else ClipState.NORMAL

    def __applyAmmoStock(self, quantityInClip, clipState, clipReloaded):
        with self.viewModel as model:
            model.setQuantityInClip(quantityInClip)
            model.setClipState(clipState)
            model.setClipReloaded(clipReloaded)
