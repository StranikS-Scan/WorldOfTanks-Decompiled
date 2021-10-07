# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_header_view.py
import logging
import string
import typing
import BigWorld
from CurrentVehicle import g_currentVehicle
from async import async, await
from constants import RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import ViewFlags, ViewSettings, ViewEvent, View
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.crew_header_model import CrewHeaderModel
from gui.impl.lobby.crew.accelerate_training_tooltip_view import AccelerateTrainingTooltipView
from gui.impl.lobby.crew.crew_header_tooltip_view import CrewHeaderTooltipView
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.processors.vehicle import VehicleTmenXPAccelerator
from gui.shared.utils import decorators
from helpers import dependency
from renewable_subscription_common.passive_xp import isTagsSetOk, CrewValidator, CrewSlotValidationResult
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from account_helpers.renewable_subscription import RenewableSubscription
    from typing import Union, Dict, Callable
_logger = logging.getLogger(__name__)

class CrewHeaderView(ViewImpl):
    __slots__ = ('_renewableSubInfo', '_serverSettings', '_crewValidationResults', '_tooltipModelFactories')
    itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.crew.CrewHeader())
        settings.flags = ViewFlags.COMPONENT
        settings.model = CrewHeaderModel()
        super(CrewHeaderView, self).__init__(settings)
        self._renewableSubInfo = BigWorld.player().renewableSubscription
        self._serverSettings = self._lobbyContext.getServerSettings()
        self._crewValidationResults = []
        self._tooltipModelFactories = {R.views.lobby.crew.AccelerateTrainingTooltipView(): AccelerateTrainingTooltipView,
         R.views.lobby.crew.CrewHeaderTooltipView(): CrewHeaderTooltipView}

    def _initialize(self, *args, **kwargs):
        super(CrewHeaderView, self)._initialize(*args, **kwargs)
        self._renewableSubInfo.onRenewableSubscriptionDataChanged += self._onRenewableSubscriptionDataChanged
        self.viewModel.onAccelerateCrewTrainingToggle += self._onAccelerateCrewTrainingToggle
        self.viewModel.onCrewOperationsClick += self._onCrewOperationsClick
        self.viewModel.onIdleCrewBonusToggle += self._onIdleCrewBonusToggle
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        g_currentVehicle.onChanged += self._onCurrentVehicleChanged

    def _finalize(self):
        self._renewableSubInfo.onRenewableSubscriptionDataChanged -= self._onRenewableSubscriptionDataChanged
        self.viewModel.onAccelerateCrewTrainingToggle -= self._onAccelerateCrewTrainingToggle
        self.viewModel.onCrewOperationsClick -= self._onCrewOperationsClick
        self.viewModel.onIdleCrewBonusToggle -= self._onIdleCrewBonusToggle
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        g_currentVehicle.onChanged -= self._onCurrentVehicleChanged
        super(CrewHeaderView, self)._finalize()

    def _onLoading(self, highlightedComponentId=-1, makeTopView=False):
        self._updateCrewValidationResults()
        self._updateModel()

    @property
    def viewModel(self):
        return super(CrewHeaderView, self).getViewModel()

    def _updateCrewValidationResults(self):
        vehicle = g_currentVehicle.item
        if vehicle is None:
            return
        else:
            tMen = (crew[1] for crew in vehicle.crew)
            validator = CrewValidator(g_currentVehicle.item.descriptor.type)
            self._crewValidationResults = validator.validateCrew([ (tMan.strCD if tMan else None) for tMan in tMen ])
            return

    def _updateModel(self):
        with self.viewModel.transaction() as tx:
            vehicle = g_currentVehicle.item
            if vehicle is None:
                _logger.info('No current vehicle')
                tx.setIsIdleCrewBonusAvailable(False)
                tx.setIsIdleCrewBonusActive(False)
                tx.setIsAccelerateCrewTrainingActive(False)
                tx.setIsAccelerateCrewTrainingAvailable(False)
                tx.setIsIdleCrewCompatible(False)
                return
            isCrewBonusAvailable = self._serverSettings.isRenewableSubPassiveCrewXPEnabled() and self._renewableSubInfo.isEnabled() and isTagsSetOk(vehicle.tags)
            tx.setIsIdleCrewBonusAvailable(isCrewBonusAvailable)
            tx.setIsIdleCrewBonusActive(self._renewableSubInfo.vehicleCrewHasIdleXP(vehicle.invID))
            tx.setIsAccelerateCrewTrainingActive(vehicle.isXPToTman)
            tx.setIsAccelerateCrewTrainingAvailable(vehicle.isElite)
            tx.setIsIdleCrewCompatible(self._isEveryCrewMemberValid() and self._isEveryCrewFull())
        return

    def _onCurrentVehicleChanged(self):
        self._updateCrewValidationResults()
        self._updateModel()

    @async
    def _onAccelerateCrewTrainingToggle(self):
        from gui.shared.event_dispatcher import showAccelerateCrewTrainingDialog
        vehicle = g_currentVehicle.item
        if vehicle is None:
            _logger.info('No current vehicle')
            return
        else:
            wasActive = vehicle.isXPToTman

            def toggleCallback():
                self._onAccelerateCrewTrainingConfirmed(vehicle, wasActive)

            if wasActive:
                toggleCallback()
            else:
                yield await(showAccelerateCrewTrainingDialog(toggleCallback))
            return

    @decorators.process('updateTankmen')
    def _onAccelerateCrewTrainingConfirmed(self, vehicle, wasActive):
        nowActive = not wasActive
        self.viewModel.setIsAccelerateCrewTrainingActive(nowActive)
        result = yield VehicleTmenXPAccelerator(vehicle, nowActive, False).request()
        if not result.success:
            self.viewModel.setIsAccelerateCrewTrainingActive(wasActive)
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def _onCrewOperationsClick(self):
        pass

    @async
    def _onIdleCrewBonusToggle(self):
        wasActive = self.viewModel.getIsIdleCrewBonusActive()
        toBeActive = not wasActive
        _logger.debug('[CrewHeaderView] _onIdleCrewBonusToggle, from=%s, to=%s', wasActive, toBeActive)
        currentVehicle = g_currentVehicle.item

        def errorCallback():
            self.viewModel.setIsIdleCrewBonusActive(wasActive)

        def toggleCallback():
            self.viewModel.setIsIdleCrewBonusActive(toBeActive)
            vehId = currentVehicle.invID if toBeActive else None
            self._renewableSubInfo.idleCrewXPSelectVehicle(vehId, errorCallback)
            return

        dialogMessage = self._buildConfirmationMessage()
        if not dialogMessage or not toBeActive:
            toggleCallback()
        else:
            from gui.shared.event_dispatcher import showIdleCrewBonusDialog
            yield await(showIdleCrewBonusDialog(dialogMessage, toggleCallback))

    def _buildConfirmationMessage(self):
        previousVehicleId = self._renewableSubInfo.getVehicleIDWithIdleXP()
        previousVehicle = self.itemsCache.items.getVehicle(previousVehicleId) if previousVehicleId else None
        stringRoot = R.strings.dialogs.idleCrewBonus
        dialogMessage = []
        if previousVehicle:
            vehicleName = previousVehicle.userName
            vehicleName = vehicleName.replace('(', '%((')
            vehicleName = vehicleName.replace(')', '))')
            dialogMessage.append(backport.text(stringRoot.message.remove()) % vehicleName)
        crewWarnings = []
        if not self._isEveryCrewFull():
            crewWarnings.append(backport.text(stringRoot.message.crewIncomplete()))
        if not self._isEveryCrewMemberValid():
            crewWarnings.append(backport.text(stringRoot.message.crewUnsuitable()))
        if crewWarnings:
            crewWarnings.insert(0, backport.text(stringRoot.message.crewWarning()))
            dialogMessage.append('\n'.join(crewWarnings))
        return '\n \n \n'.join(dialogMessage)

    def _onRenewableSubscriptionDataChanged(self, itemDiff):
        self._updateModel()

    def _onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self._updateModel()

    def _isEveryCrewMemberValid(self):
        for result in self._crewValidationResults:
            if not result.isEmpty and not result.tManValidRes.isValid:
                return False

        return True

    def _isEveryCrewFull(self):
        for result in self._crewValidationResults:
            if result.isEmpty:
                return False

        return True

    def _getWarningStr(self):
        warningStrings = []
        if not self._isEveryCrewMemberValid():
            warningStrings.append(backport.text(R.strings.tooltips.idle_crew_tooltip.warningUnsuitable()))
        if not self._isEveryCrewFull():
            warningStrings.append(backport.text(R.strings.tooltips.idle_crew_tooltip.warningIncomplete()))
        return string.join(warningStrings, sep='\n')

    def createPopOverContent(self, event):
        return BackportPopOverContent(createPopOverData(VIEW_ALIAS.CREW_OPERATIONS_POPOVER))

    def createToolTipContent(self, event, contentID):
        if contentID not in self._tooltipModelFactories:
            _logger.error('Crew header view tried creating invalid tooltip with contentID %d', contentID)
            return None
        else:
            return self._tooltipModelFactories[contentID](self.viewModel.getIsIdleCrewBonusActive(), self._getWarningStr())
