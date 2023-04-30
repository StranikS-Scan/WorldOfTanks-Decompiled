# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_header_view.py
import logging
import typing
from typing import NamedTuple
from CurrentVehicle import g_currentVehicle
from constants import RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import ViewFlags, ViewSettings, ViewEvent, View
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.backport.backport_pop_over import BackportPopOverContent, createPopOverData
from gui.impl.gen import R
from gui.impl.gen_utils import DynAccessor
from gui.impl.gen.view_models.views.lobby.crew.crew_header_model import CrewHeaderModel
from gui.impl.gen.view_models.views.lobby.crew.idle_crew_bonus import IdleCrewBonusEnum
from gui.impl.lobby.crew.accelerate_training_tooltip_view import AccelerateTrainingTooltipView
from gui.impl.lobby.crew.crew_header_tooltip_view import CrewHeaderTooltipView
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Vehicle import Vehicle, getIconResourceName
from gui.shared.gui_items.processors.vehicle import VehicleTmenXPAccelerator
from gui.shared.utils import decorators
from helpers import dependency, int2roman
from renewable_subscription_common.passive_xp import isTagsSetOk, CrewValidator, CrewSlotValidationResult
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Union, Dict, Callable
_logger = logging.getLogger(__name__)
BuildedMessage = NamedTuple('BuildedMessage', [('text', str), ('icon', DynAccessor)])

class CrewHeaderView(ViewImpl):
    __slots__ = ('_serverSettings', '_crewValidationResults', '_tooltipModelFactories')
    itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.crew.CrewHeader())
        settings.flags = ViewFlags.COMPONENT
        settings.model = CrewHeaderModel()
        super(CrewHeaderView, self).__init__(settings)
        self._serverSettings = self._lobbyContext.getServerSettings()
        self._crewValidationResults = []
        self._tooltipModelFactories = {R.views.lobby.crew.AccelerateTrainingTooltipView(): AccelerateTrainingTooltipView,
         R.views.lobby.crew.CrewHeaderTooltipView(): CrewHeaderTooltipView}

    def _initialize(self, *args, **kwargs):
        super(CrewHeaderView, self)._initialize(*args, **kwargs)
        self._wotPlusCtrl.onDataChanged += self._onWotPlusDataChanged
        self.viewModel.onAccelerateCrewTrainingToggle += self._onAccelerateCrewTrainingToggle
        self.viewModel.onCrewOperationsClick += self._onCrewOperationsClick
        self.viewModel.onIdleCrewBonusToggle += self._onIdleCrewBonusToggle
        self._lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        g_currentVehicle.onChanged += self._onCurrentVehicleChanged

    def _finalize(self):
        self._wotPlusCtrl.onDataChanged -= self._onWotPlusDataChanged
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
                tx.setIsAccelerateCrewTrainingActive(False)
                tx.setIsAccelerateCrewTrainingAvailable(False)
                tx.setIdleCrewBonus(IdleCrewBonusEnum.DISABLED)
                return
            tx.setIsAccelerateCrewTrainingActive(vehicle.isXPToTman)
            tx.setIsAccelerateCrewTrainingAvailable(vehicle.isElite)
            tx.setIdleCrewBonus(self._getIdleCrewState())
        return

    def _getIdleCrewState(self):
        if not self._lobbyContext.getServerSettings().isRenewableSubPassiveCrewXPEnabled():
            return IdleCrewBonusEnum.INVISIBLE
        if not self._wotPlusCtrl.isEnabled():
            return IdleCrewBonusEnum.DISABLED
        vehicle = g_currentVehicle.item
        if not isTagsSetOk(vehicle.tags):
            return IdleCrewBonusEnum.INCOMPATIBLEWITHCURRENTVEHICLE
        if self._wotPlusCtrl.hasVehicleCrewIdleXP(vehicle.invID):
            return IdleCrewBonusEnum.ACTIVEONCURRENTVEHICLE
        return IdleCrewBonusEnum.ACTIVEONANOTHERVEHICLE if self._wotPlusCtrl.getVehicleIDWithIdleXP() else IdleCrewBonusEnum.ENABLED

    def _onCurrentVehicleChanged(self):
        self._updateCrewValidationResults()
        self._updateModel()

    @wg_async
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
                yield wg_await(showAccelerateCrewTrainingDialog(toggleCallback))
            return

    @decorators.adisp_process('updateTankmen')
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

    @wg_async
    def _onIdleCrewBonusToggle(self):
        wasActive = self.viewModel.getIdleCrewBonus() == IdleCrewBonusEnum.ACTIVEONCURRENTVEHICLE
        toBeActive = not wasActive
        _logger.debug('[CrewHeaderView] _onIdleCrewBonusToggle, from=%s, to=%s', wasActive, toBeActive)
        currentVehicle = g_currentVehicle.item

        def callback():
            self.viewModel.setIdleCrewBonus(self._getIdleCrewState())

        def toggleCallback():
            vehId = currentVehicle.invID if toBeActive else None
            self._wotPlusCtrl.selectIdleCrewXPVehicle(vehId, callback, callback)
            return

        dialogMessage = self._buildConfirmationMessage()
        if not dialogMessage or not toBeActive:
            toggleCallback()
        else:
            from gui.shared.event_dispatcher import showIdleCrewBonusDialog
            yield wg_await(showIdleCrewBonusDialog(dialogMessage, toggleCallback))

    def _buildConfirmationMessage(self):
        previousVehicleId = self._wotPlusCtrl.getVehicleIDWithIdleXP()
        previousVehicle = self.itemsCache.items.getVehicle(previousVehicleId) if previousVehicleId else None
        stringRoot = R.strings.dialogs.idleCrewBonus
        message = None
        if previousVehicle:
            vehicleName = '{} {}'.format(int2roman(previousVehicle.level), previousVehicle.userName)
            removeTypeString = backport.text(stringRoot.message.removeType())
            removeNameString = backport.text(stringRoot.message.removeName(), vehicleName=vehicleName)
            finalString = '{} {}'.format(removeTypeString, removeNameString)
            message = BuildedMessage(text=finalString, icon=R.images.gui.maps.icons.vehicleTypes.dyn(getIconResourceName(previousVehicle.type)))
        return message

    def _onWotPlusDataChanged(self, itemDiff):
        if 'isEnabled' in itemDiff:
            self._updateModel()

    def _onServerSettingsChange(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self._updateModel()

    def createPopOverContent(self, event):
        return BackportPopOverContent(createPopOverData(VIEW_ALIAS.CREW_OPERATIONS_POPOVER))

    def createToolTipContent(self, event, contentID):
        if contentID not in self._tooltipModelFactories:
            _logger.error('Crew header view tried creating invalid tooltip with contentID %d', contentID)
            return None
        else:
            return self._tooltipModelFactories[contentID](self.viewModel.getIdleCrewBonus())
