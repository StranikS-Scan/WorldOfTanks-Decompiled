# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_setup/hangar.py
import logging
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.impl.lobby.tank_setup.ammunition_panel.hangar import HangarAmmunitionPanel
from gui.impl.lobby.tank_setup.ammunition_setup.base_hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.tank_setup.main_tank_setup.hangar import HangarMainTankSetupView
from gui.impl.lobby.tank_setup.optional_devices_assistant.hangar import OptionalDevicesAssistantView
from gui.impl.lobby.tank_setup.tank_setup_builder import HangarTankSetupBuilder, EpicBattleTankSetupBuilder
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
_logger = logging.getLogger(__name__)

class HangarAmmunitionSetupView(BaseHangarAmmunitionSetupView, IGlobalListener):
    __slots__ = ()
    _wotPlusController = dependency.descriptor(IWotPlusController)

    def _initialize(self, *args, **kwargs):
        super(HangarAmmunitionSetupView, self)._initialize(*args, **kwargs)
        self._wotPlusController.onEnabledStatusChanged += self.__onWotPlusDataChanged

    def _finalize(self):
        super(HangarAmmunitionSetupView, self)._finalize()
        self._wotPlusController.onEnabledStatusChanged -= self.__onWotPlusDataChanged

    def _createOptionalDevicesAssistantPanel(self):
        if not g_currentVehicle.isPresent():
            return
        if not self.prbEntity:
            return
        queueType = self.prbEntity.getQueueType()
        if self._lobbyContext.getServerSettings().isOptionalDevicesAssistantEnabled() and self._wotPlusController.isEnabled() and queueType in (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.COMP7):
            self._optionalDevicesAssistant = OptionalDevicesAssistantView(self.viewModel.optionalDevicesAssistant, queueType)
            self._optionalDevicesAssistant.onLoading()

    def _createMainTankSetup(self):
        return HangarMainTankSetupView(self.viewModel.tankSetup, self.__getTankSetupBuilder()(self._vehItem))

    def _createAmmunitionPanel(self):
        ctx = {'specializationClickable': True}
        return HangarAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem(), ctx=ctx)

    def __getTankSetupBuilder(self):
        return EpicBattleTankSetupBuilder if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC) else HangarTankSetupBuilder

    def __onWotPlusDataChanged(self, isEnabledVal):
        if isEnabledVal is not None:
            if isEnabledVal:
                if not self._optionalDevicesAssistant:
                    self._createOptionalDevicesAssistantPanel()
                    if self._optionalDevicesAssistant:
                        self._optionalDevicesAssistant.initialize()
                else:
                    _logger.warning('Optional device assistant widget has already been created!')
            elif self._optionalDevicesAssistant:
                self._optionalDevicesAssistant.showNoDataState()
                self._removeOptionalDevicesAssistantPanel()
        return
