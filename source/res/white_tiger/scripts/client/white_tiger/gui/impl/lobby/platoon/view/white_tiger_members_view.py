# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/platoon/view/white_tiger_members_view.py
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from helpers import dependency
from skeletons.prebattle_vehicle import IPrebattleVehicle
from white_tiger.gui.gui_constants import WTPrebattleTypes

class WhiteTigerMembersView(SquadMembersView):
    _prebattleType = WTPrebattleTypes.WHITE_TIGER
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def _addListeners(self):
        super(WhiteTigerMembersView, self)._addListeners()
        self.__prebattleVehicle.onChanged += self._updateReadyButton

    def _removeListeners(self):
        super(WhiteTigerMembersView, self)._removeListeners()
        self.__prebattleVehicle.onChanged -= self._updateReadyButton

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.platoon.members.header.tooltip.white_tiger.header())
        tooltipBody = backport.text(R.strings.platoon.members.header.tooltip.white_tiger.body())
        return (tooltipHeader, tooltipBody)

    def _getNotReadyStatus(self):
        return R.strings.white_tiger.window.unit.message.vehicleNotSelected()

    def _setBonusInformation(self, bonusState):
        pass

    def _updateFindPlayersButton(self, *args):
        with self.viewModel.transaction() as model:
            model.setShouldShowFindPlayersButton(value=False)

    def _updateMembers(self):
        super(WhiteTigerMembersView, self)._updateMembers()
        with self.viewModel.transaction() as model:
            slotModelArray = model.getSlots()
            for slotModel in slotModelArray:
                slotModel.setIsEvent(True)
