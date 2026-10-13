# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/shared/clip/extra_shot_clip_presenter.py
from __future__ import absolute_import
import logging
import typing
from gui.battle_control.battle_constants import SHELL_QUANTITY_UNKNOWN, SHELL_SET_RESULT
from gui.impl.gen.view_models.views.battle.shared.clip.extra_shot_clip_model import ClipState, ExtraShotClipModel
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import _GunSettings
_logger = logging.getLogger(__name__)

class ExtraShotClipPresenter(ViewComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ExtraShotClipPresenter, self).__init__(model=ExtraShotClipModel)
        self.__clipCapacity = 1

    @property
    def viewModel(self):
        return super(ExtraShotClipPresenter, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ExtraShotClipPresenter, self)._initialize(*args, **kwargs)
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('ExtraShotClipPresenter: AmmoController is not available')
            return
        else:
            gunSettings = ammoCtrl.getGunSettings()
            if gunSettings is not None:
                self.__applyGunSettings(gunSettings)
            _, quantityInClip = ammoCtrl.getCurrentShells()
            if quantityInClip != SHELL_QUANTITY_UNKNOWN:
                clipState = self.__computeClipState(quantityInClip)
                self.__applyAmmoStock(quantityInClip, clipState)
            return

    def _getEvents(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('ExtraShotClipPresenter: AmmoController is not available')
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
        clipState = self.__computeClipState(quantityInClip)
        self.__applyAmmoStock(quantityInClip, clipState)

    def __onCurrentShellChanged(self, intCD):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            return
        else:
            _, quantityInClip = ammoCtrl.getCurrentShells()
            clipState = self.__computeClipState(quantityInClip)
            self.__applyAmmoStock(quantityInClip, clipState)
            return

    def __onCurrentShellReset(self):
        self.__applyAmmoStock(0, ClipState.NORMAL)

    def __applyGunSettings(self, gunSettings):
        self.__clipCapacity = gunSettings.clip.size
        with self.viewModel as model:
            model.setClipCapacity(self.__clipCapacity)

    def __computeClipState(self, quantityInClip):
        return ClipState.NONE if quantityInClip == SHELL_QUANTITY_UNKNOWN else ClipState.NORMAL

    def __applyAmmoStock(self, quantityInClip, clipState):
        with self.viewModel as model:
            model.setQuantityInClip(quantityInClip)
            model.setClipState(clipState)
