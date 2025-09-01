# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/platoon/view/platoon_members_view.py
from comp7_light.gui.impl.gen.view_models.views.lobby.platoon.comp7_light_slot_model import Comp7LightSlotModel
from comp7_light.gui.impl.gen.view_models.views.lobby.platoon.comp7_light_window_model import Comp7LightWindowModel
from comp7_light_constants import CLIENT_UNIT_CMD
from comp7_light.gui.comp7_light_constants import SELECTOR_BATTLE_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.platoon.dropdown_item import DropdownItem
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import PrebattleTypes
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import ErrorType
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.platoon.platoon_helpers import getPlatoonBonusState
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, _LayoutStyle
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.prb_control import prb_getters, prbEntityProperty
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController
from skeletons.gui.lobby_context import ILobbyContext

class Comp7LightMembersView(SquadMembersView):
    _layoutID = R.views.comp7_light.lobby.MembersWindow()
    _prebattleType = PrebattleTypes.COMP7LIGHT
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, prbType):
        super(Comp7LightMembersView, self).__init__(prbType)
        self.__unitMgr = prb_getters.getClientUnitMgr()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def createToolTipContent(self, event, contentID):
        return SquadBonusTooltipContent(battleType=SELECTOR_BATTLE_TYPES.COMP7_LIGHT, bonusState=getPlatoonBonusState(True)) if contentID == R.views.lobby.premacc.tooltips.SquadBonusTooltip() else super(Comp7LightMembersView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def _viewModelClass(self):
        return Comp7LightWindowModel

    @property
    def _slotModelClass(self):
        return Comp7LightSlotModel

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _getLayoutStyle(self):
        return _LayoutStyle.VERTICAL

    def _setModeSlotSpecificData(self, slotData, slotModel):
        playerData = slotData.get('player', {})
        queueInfo = playerData.get('extraData', {}).get('comp7LightEnqueueData', {})
        isOnline = bool(queueInfo.get('isOnline', True))
        slotModel.setErrorType(ErrorType.NONE if isOnline else ErrorType.MODEOFFLINE)

    def _initWindowModeSpecificData(self, model):
        model.header.memberCountDropdown.setMultiple(False)
        memberCountVariants = model.header.memberCountDropdown.getItems()
        for squadSize in self.__comp7LightController.getModeSettings().squadSizes:
            memberCount = DropdownItem()
            memberCount.setId(str(squadSize))
            memberCount.setLabel(str(squadSize))
            memberCountVariants.addViewModel(memberCount)

    def _updateHeader(self):
        super(Comp7LightMembersView, self)._updateHeader()
        with self.viewModel.transaction() as model:
            self.__updateDropDown(model)

    def _getWindowInfoTooltipHeaderAndBody(self):
        return (None, None)

    def _getPlatoonSlotsData(self):
        slots = super(Comp7LightMembersView, self)._getPlatoonSlotsData()
        slots.sort(key=self.__playerTimeJoin)
        return slots

    def _hasFreeSlot(self):
        return len(self.__unitMgr.unit.getPlayers()) < self.__unitMgr.unit.getSquadSize() if self.__unitMgr is not None and self.__unitMgr.unit is not None else False

    def _addListeners(self):
        super(Comp7LightMembersView, self)._addListeners()
        self.viewModel.header.memberCountDropdown.onChange += self.__onMemberCountDropdown
        if self.__unitMgr is not None and self.__unitMgr.unit is not None:
            self.__unitMgr.unit.onSquadSizeChanged += self.__updateEntityState
        return

    def _removeListeners(self):
        super(Comp7LightMembersView, self)._removeListeners()
        self.viewModel.header.memberCountDropdown.onChange -= self.__onMemberCountDropdown
        if self.__unitMgr is not None and self.__unitMgr.unit is not None:
            self.__unitMgr.unit.onSquadSizeChanged -= self.__updateEntityState
        return

    def __updateDropDown(self, model):
        self.__updateMemberCountDropdown(model)
        items = model.header.memberCountDropdown.getItems()
        actualSquadSize = self.__unitMgr.unit.getSquadSize()
        selected = model.header.memberCountDropdown.getSelected()
        selected.clear()
        selected.addString(str(actualSquadSize))
        selected.invalidate()
        playersCount = len(self.__unitMgr.unit.getPlayers())
        for item in items:
            self.__updateDropdownItem(item, playersCount)

    def __updateMemberCountDropdown(self, model):
        if not self._isCommander():
            model.header.memberCountDropdown.setIsDisabled(True)
            model.header.memberCountDropdown.setTooltipText(self.__getDropDownTooltipText())
        else:
            model.header.memberCountDropdown.setIsDisabled(False)
            model.header.memberCountDropdown.setTooltipText('')

    def __updateDropdownItem(self, item, playersCount):
        itemNumber = int(item.getLabel())
        if itemNumber < playersCount:
            item.setIsDisabled(True)
            item.meta.setTooltipText(self.__getDropDownItemTooltipText())
        else:
            item.setIsDisabled(False)
            item.meta.setTooltipText('')

    def __updateEntityState(self):
        g_eventDispatcher.updateUI()

    @args2params(int)
    def __onMemberCountDropdown(self, selectedIds):
        if not selectedIds:
            return
        self.__unitMgr.doUnitCmd(CLIENT_UNIT_CMD.SET_COMP7_LIGHT_SQUAD_SIZE, selectedIds)

    @staticmethod
    def __getDropDownTooltipText():
        return backport.text(R.strings.platoon.members.header.tooltip.comp7_light.dropdown())

    @staticmethod
    def __getDropDownItemTooltipText():
        return backport.text(R.strings.platoon.members.header.tooltip.comp7_light.dropdown.item())

    @staticmethod
    def __playerTimeJoin(slot):
        player = slot['player'] or {}
        roleIndex = -slot['role'] if not player.get('isOffline') else 0
        return (not player, roleIndex, player.get('timeJoin', 0))
