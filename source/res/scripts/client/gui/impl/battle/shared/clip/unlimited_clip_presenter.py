# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/shared/clip/unlimited_clip_presenter.py
from __future__ import absolute_import
import logging
import typing
from gui.impl.gen.view_models.views.battle.shared.clip.unlimited_clip_model import UnlimitedClipModel
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.ammo_ctrl import _GunSettings
_logger = logging.getLogger(__name__)

class UnlimitedClipPresenter(ViewComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(UnlimitedClipPresenter, self).__init__(model=UnlimitedClipModel)

    @property
    def viewModel(self):
        return super(UnlimitedClipPresenter, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(UnlimitedClipPresenter, self)._initialize(*args, **kwargs)
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('UnlimitedClipPresenter: AmmoController is not available')
            return
        else:
            gunSettings = ammoCtrl.getGunSettings()
            if gunSettings is not None:
                self.__applyGunSettings(gunSettings)
            return

    def _getEvents(self):
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is None:
            _logger.warning('UnlimitedClipPresenter: AmmoController is not available')
            return ()
        else:
            return ((ammoCtrl.onGunSettingsSet, self.__onGunSettingsSet),)

    def __onGunSettingsSet(self, gunSettings):
        self.__applyGunSettings(gunSettings)

    def __applyGunSettings(self, gunSettings):
        with self.viewModel as model:
            model.setIsUnlimitedClip(gunSettings.isUnlimitedClip)
