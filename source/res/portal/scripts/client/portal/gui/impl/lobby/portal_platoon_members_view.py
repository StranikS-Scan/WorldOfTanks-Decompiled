# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/portal_platoon_members_view.py
import typing
from adisp import adisp_process
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, BonusState
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from helpers import i18n, dependency
from portal.gui.impl.gen.view_models.views.lobby.portal_slot_model import PortalSlotModel
from portal.gui.impl.gen.view_models.views.lobby.portal_members_view_model import PortalMembersViewModel
from portal.gui.portal_gui_constants import PortalPrebattleTypes
from portal.skeletons.portal_event_controller import IPortalEventController
if typing.TYPE_CHECKING:
    from typing import Dict

class PortalMembersView(SquadMembersView):
    _layoutID = R.views.portal.lobby.MembersWindow()
    _prebattleType = PortalPrebattleTypes.PORTAL
    __portalController = dependency.descriptor(IPortalEventController)

    def __init__(self, prbType):
        super(PortalMembersView, self).__init__(prbType)
        self.viewModel.setShouldShowFindPlayersButton(False)

    @property
    def _viewModelClass(self):
        return PortalMembersViewModel

    @property
    def _slotModelClass(self):
        return PortalSlotModel

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.portal_platoon.members.header.event()))))
        return title

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.portal_platoon.members.header.tooltip.event.header())
        tooltipBody = backport.text(R.strings.portal_platoon.members.header.tooltip.event.body())
        return (tooltipHeader, tooltipBody)

    def _setBonusInformation(self, bonusState):
        with self.viewModel.header.transaction() as model:
            model.setShowNoBonusPlaceholder(True)
            model.noBonusPlaceholder.setIcon(R.images.portal.gui.maps.icons.battleTypes.c_40x40.portal_squad())
            self._currentBonusState = bonusState

    def _getBonusState(self):
        return BonusState.NO_BONUS

    def _createHeaderInfoTooltip(self):
        tooltip = R.strings.platoon.members.header.noBonusPlaceholder.tooltip
        header = backport.text(tooltip.header())
        body = backport.text(tooltip.body())
        return self._createSimpleTooltipContent(header=header, body=body)

    def _setVehicleData(self, slotData, slotModel):
        super(PortalMembersView, self)._setVehicleData(slotData, slotModel)
        vehicle = slotData.get('selectedVehicle', {})
        if vehicle:
            portalEnqueueData = self.__getSlotPortalEnqueueData(slotData)
            vehicleLevel = portalEnqueueData.get('vehicleLevel', 1)
            slotModel.player.vehicle.setTier(vehicleLevel)

    def _setModeSlotSpecificData(self, slotData, slotModel):
        portalEnqueueData = self.__getSlotPortalEnqueueData(slotData)
        maxBattleLevel = portalEnqueueData.get('playerMaxBattleLevel', 1)
        slotModel.setMaxComplexity(maxBattleLevel)

    def _updateButtons(self):
        super(PortalMembersView, self)._updateButtons()
        battleLevel = self.__portalController.battleLevel
        with self.viewModel.transaction() as model:
            model.setComplexity(battleLevel)

    def __getSlotPortalEnqueueData(self, slotData):
        playerData = slotData.get('player', {})
        extraData = playerData.get('extraData', {})
        return extraData.get('portalEnqueueData', {})

    @adisp_process
    def _onSwitchReady(self):
        result = yield self._platoonCtrl.togglePlayerReadyAction(checkAmmo=False)
        if result:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)
