# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/platoon/view/platoon_members_view.py
import logging
from itertools import izip
import typing
from shared_utils import findFirst
from comp7.gui.comp7_constants import SELECTOR_BATTLE_TYPES
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared
from comp7.gui.impl.lobby.comp7_helpers.comp7_model_helpers import getSeasonNameEnum
from comp7.gui.impl.lobby.meta_view.meta_view_helper import setRankItemData
from comp7.gui.impl.lobby.tooltips.division_tooltip import DivisionTooltip
from comp7.gui.impl.lobby.tooltips.fifth_rank_tooltip import FifthRankTooltip
from comp7.gui.impl.lobby.tooltips.general_rank_tooltip import GeneralRankTooltip
from comp7.gui.impl.lobby.tooltips.rank_compatibility_tooltip import RankCompatibilityTooltip
from comp7.gui.impl.lobby.tooltips.sixth_rank_tooltip import SixthRankTooltip
from comp7_common.comp7_constants import CLIENT_UNIT_CMD
from gui.impl import backport
from gui.impl.gen import R
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.progression_item_base_model import ProgressionItemBaseModel
from comp7.gui.impl.gen.view_models.views.lobby.platoon.comp7_slot_model import Comp7SlotModel
from comp7.gui.impl.gen.view_models.views.lobby.platoon.comp7_window_model import Comp7WindowModel
from gui.impl.gen.view_models.views.lobby.platoon.dropdown_item import DropdownItem
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import PrebattleTypes
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import ErrorType
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.platoon.platoon_helpers import getPlatoonBonusState
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, _LayoutStyle
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from gui.impl.lobby.premacc.squad_bonus_tooltip_content import SquadBonusTooltipContent
from gui.prb_control import prb_getters, prbEntityProperty
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
    from comp7_ranks_common import Comp7Division
_logger = logging.getLogger(__name__)

class Comp7MembersView(SquadMembersView):
    _comp7Controller = dependency.descriptor(IComp7Controller)
    _prebattleType = PrebattleTypes.COMP7
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    _layoutID = R.views.comp7.lobby.MembersWindow()

    def __init__(self, prbType):
        super(Comp7MembersView, self).__init__(prbType)
        self.__unitMgr = prb_getters.getClientUnitMgr()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.premacc.tooltips.SquadBonusTooltip():
            return SquadBonusTooltipContent(battleType=SELECTOR_BATTLE_TYPES.COMP7, bonusState=getPlatoonBonusState(True))
        if contentID == R.views.comp7.lobby.tooltips.GeneralRankTooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        if contentID == R.views.comp7.lobby.tooltips.FifthRankTooltip():
            return FifthRankTooltip()
        if contentID == R.views.comp7.lobby.tooltips.SixthRankTooltip():
            return SixthRankTooltip()
        if contentID == R.views.comp7.lobby.tooltips.RankCompatibilityTooltip():
            squadSize = self.__unitMgr.unit.getSquadSize()
            rankRangeRestriction = self._comp7Controller.getPlatoonRankRestriction(squadSize)
            return RankCompatibilityTooltip(squadSize, rankRangeRestriction)
        if contentID == R.views.comp7.lobby.tooltips.DivisionTooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'division': Division(event.getArgument('division')),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return DivisionTooltip(params=params)
        return super(Comp7MembersView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def _viewModelClass(self):
        return Comp7WindowModel

    @property
    def _slotModelClass(self):
        return Comp7SlotModel

    def _onLoading(self, *args, **kwargs):
        super(Comp7MembersView, self)._onLoading(*args, **kwargs)
        rankRange = 2 * self._comp7Controller.getPlatoonMaxRankRestriction() + 1
        self.viewModel.getRankLimits().reserve(rankRange)

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _setModeSlotSpecificData(self, slotData, slotModel):
        playerData = slotData.get('player', {})
        queueInfo = playerData.get('extraData', {}).get('comp7EnqueueData', {})
        rank = queueInfo.get('rank', 0)
        rating = queueInfo.get('rating', 0)
        isOnline = bool(queueInfo.get('isOnline', 0))
        division = self.__getDivision(rank, rating)
        if division is None:
            _logger.error("Failed to get player's division. dbID: %d; rank: %d; rating: %d", playerData.get('dbID'), rank, rating)
            return
        else:
            slotModel.rankData.setRank(comp7_shared.getRankEnumValue(division))
            slotModel.rankData.setDivision(comp7_shared.getDivisionEnumValue(division))
            slotModel.rankData.setScore(rating)
            slotModel.rankData.setFrom(division.range.begin)
            slotModel.rankData.setTo(division.range.end + 1)
            slotModel.setErrorType(ErrorType.NONE if isOnline else ErrorType.MODEOFFLINE)
            return

    def _initWindowModeSpecificData(self, model):
        model.setTopPercentage(self._comp7Controller.leaderboard.getEliteRankPercent())
        model.setSeasonName(getSeasonNameEnum())
        model.header.memberCountDropdown.setMultiple(False)
        memberCountVariants = model.header.memberCountDropdown.getItems()
        for squadSize in self._comp7Controller.getModeSettings().squadSizes:
            memberCount = DropdownItem()
            memberCount.setId(str(squadSize))
            memberCount.setLabel(str(squadSize))
            memberCountVariants.addViewModel(memberCount)

    def __updateRankTips(self, model):
        ranksConfig = self._comp7Controller.getRanksConfig()
        maxPlayerRank = Rank.FIRST.value
        for slot in self._getPlatoonSlotsData():
            player = slot.get('player')
            if player is None:
                continue
            rank = player.get('extraData', {}).get('comp7EnqueueData', {}).get('rank', Rank.FIRST.value)
            maxPlayerRank = min(maxPlayerRank, rank)

        setRankItemData(model.topPlayer, maxPlayerRank, ranksConfig)
        rankLimits = model.getRankLimits()
        rankDelta = self._comp7Controller.getPlatoonRankRestriction()
        startRankRange = max(maxPlayerRank - rankDelta, Rank.SIXTH.value)
        stopRankRange = min(maxPlayerRank + rankDelta, Rank.FIRST.value)
        newSize = stopRankRange - startRankRange + 1
        for _ in xrange(len(rankLimits), newSize):
            rankLimits.addViewModel(ProgressionItemBaseModel())

        if newSize < len(rankLimits):
            rankLimits.removeValues(range(newSize, len(rankLimits)))
        for progressionItemBasemodel, rank in izip(rankLimits, xrange(stopRankRange, startRankRange - 1, -1)):
            setRankItemData(progressionItemBasemodel, rank, ranksConfig)

        rankLimits.invalidate()
        return

    def _updateHeader(self):
        super(Comp7MembersView, self)._updateHeader()
        with self.viewModel.transaction() as model:
            self.__updateDropDown(model)
            self.__updateRankTips(model)

    def _getPlatoonSlotsData(self):
        slots = super(Comp7MembersView, self)._getPlatoonSlotsData()
        slots.sort(key=self.__playerTimeJoin)
        return slots

    def _getLayoutStyle(self):
        return _LayoutStyle.VERTICAL

    def _hasFreeSlot(self):
        return len(self.__unitMgr.unit.getPlayers()) < self.__unitMgr.unit.getSquadSize() if self.__unitMgr is not None and self.__unitMgr.unit is not None else False

    def _addListeners(self):
        super(Comp7MembersView, self)._addListeners()
        self.viewModel.header.memberCountDropdown.onChange += self.__onMemberCountDropdown

    def _removeListeners(self):
        super(Comp7MembersView, self)._removeListeners()
        self.viewModel.header.memberCountDropdown.onChange -= self.__onMemberCountDropdown

    @args2params(int)
    def __onMemberCountDropdown(self, selectedIds):
        if selectedIds:
            self.__unitMgr.doUnitCmd(CLIENT_UNIT_CMD.SET_SQUAD_SIZE, selectedIds)

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

    def __getDropDownTooltipText(self):
        return backport.text(R.strings.platoon.members.header.tooltip.comp7.dropdown())

    def __getDropDownItemTooltipText(self):
        return backport.text(R.strings.platoon.members.header.tooltip.comp7.dropdown.item())

    @classmethod
    def __getDivision(cls, rank, rating):
        ranksConfig = cls._comp7Controller.getRanksConfig()
        division = findFirst(lambda d: rating in d.range, ranksConfig.divisionsByRank.get(rank, ()))
        return division

    @staticmethod
    def __playerTimeJoin(slot):
        player = slot['player'] or {}
        roleIndex = -slot['role'] if not player.get('isOffline') else 0
        return (not player, roleIndex, player.get('timeJoin', 0))
