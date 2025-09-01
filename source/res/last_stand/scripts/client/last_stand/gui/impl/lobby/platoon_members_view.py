# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/platoon_members_view.py
from adisp import adisp_process
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, BonusState
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from last_stand.gui.ls_gui_constants import PREBATTLE_ACTION_NAME, DifficultyLevel, QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from last_stand.gui.impl.gen.view_models.views.lobby.difficulty_dropdown_item_model import DifficultyDropdownItemModel
from last_stand.gui.impl.gen.view_models.views.lobby.ext_members_window_model import ExtMembersWindowModel, PrebattleTypes
from last_stand.gui.shared.event_dispatcher import isViewLoaded, closeViewsByID
from last_stand.gui.impl.lobby.ls_helpers.platoon_helpers import getPlatoonSlotsData
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand_common.last_stand_constants import UNIT_LS_EXTRA_DATA_KEY, CURRENT_QUEUE_TYPE_KEY, UNIT_DIFFICULTY_LEVELS_KEY
from helpers import i18n, dependency

class ExtMembersView(SquadMembersView, IGlobalListener):
    _prebattleType = PrebattleTypes.LASTSTAND
    _layoutID = R.views.last_stand.lobby.MembersWindow()
    _difficultyCtrl = dependency.descriptor(IDifficultyLevelController)
    _DROPDOWN_ORDER = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]

    def __init__(self, prbType):
        super(ExtMembersView, self).__init__(prbType)
        self.viewModel.setShouldShowFindPlayersButton(False)

    def getPrebattleType(self):
        return PREBATTLE_ACTION_NAME.LAST_STAND

    @property
    def _viewModelClass(self):
        return ExtMembersWindowModel

    @property
    def _slotModelClass(self):
        return SlotModel

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onFindPlayers(self):
        pass

    def _onLoading(self, *args, **kwargs):
        super(ExtMembersView, self)._onLoading(*args, **kwargs)
        layoutID = R.views.last_stand.mono.lobby.battle_result_view()
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        if not entity.isCommander() and unit and isViewLoaded(layoutID=layoutID):
            closeViewsByID([layoutID])

    def _addListeners(self):
        super(ExtMembersView, self)._addListeners()
        self.viewModel.eventDifficulty.onChange += self.__changeDifficulty
        self._difficultyCtrl.onChangeDifficultyLevel += self.__selectedLevel
        self._difficultyCtrl.onChangeDifficultyLevelStatus += self.__updateLevelStatus
        self.startGlobalListening()

    def _removeListeners(self):
        super(ExtMembersView, self)._removeListeners()
        self.viewModel.eventDifficulty.onChange -= self.__changeDifficulty
        self._difficultyCtrl.onChangeDifficultyLevel -= self.__selectedLevel
        self._difficultyCtrl.onChangeDifficultyLevelStatus -= self.__updateLevelStatus
        self.stopGlobalListening()

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.last_stand_platoon.members.header.last_stand()))))
        return title

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.last_stand_platoon.members.header.tooltip.last_stand.header())
        tooltipBody = backport.text(R.strings.last_stand_platoon.members.header.tooltip.last_stand.body())
        return (tooltipHeader, tooltipBody)

    def _setBonusInformation(self, bonusState):
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(False)
            model.setShowNoBonusPlaceholder(True)
            model.noBonusPlaceholder.setText(R.invalid())
            model.noBonusPlaceholder.setIcon(R.images.last_stand.gui.maps.icons.battleTypes.c_40x40.last_stand_squad())
            self._currentBonusState = bonusState

    def _getBonusState(self):
        return BonusState.NO_BONUS

    def _createHeaderInfoTooltip(self):
        tooltip = R.strings.platoon.members.header.noBonusPlaceholder.tooltip
        header = backport.text(tooltip.header())
        body = backport.text(tooltip.body())
        return self._createSimpleTooltipContent(header=header, body=body)

    def _updateMembers(self):
        super(ExtMembersView, self)._updateMembers()
        self.__updateDropdownState()

    def _getActionButtonStateInfo(self):
        result = self._platoonCtrl.getPrbEntity().canPlayerDoAction()
        actionButtonStateVO = SquadActionButtonStateVO(self._platoonCtrl.getPrbEntity())
        isEnabled = actionButtonStateVO['isEnabled']
        onlyReadinessText = actionButtonStateVO.isReadinessTooltip()
        if result.restriction == UNIT_RESTRICTION.VEHICLE_NOT_VALID:
            simpleState = backport.text(R.strings.last_stand_platoon.platoon.simpleState.lockVehicle())
            toolTipData = ''
        elif result.restriction == UNIT_RESTRICTION.UNIT_WRONG_DATA:
            simpleState = backport.text(R.strings.last_stand_platoon.platoon.simpleState.notAvailableLevel())
            toolTipData = ''
        elif result.restriction == UNIT_RESTRICTION.MODE_NOT_AVAILABLE:
            simpleState = backport.text(R.strings.last_stand_platoon.platoon.simpleState.difficultyDisabled())
            toolTipData = ''
        else:
            simpleState = actionButtonStateVO.getSimpleState()
            toolTipData = i18n.makeString(actionButtonStateVO['toolTipData'] + '/body')
        return (isEnabled,
         onlyReadinessText,
         simpleState,
         toolTipData)

    def _getPlatoonSlotsData(self):
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        if not unit:
            return
        queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
        slots, squadSize = getPlatoonSlotsData(self._platoonCtrl.getPrbEntity(), queueType)
        slots.sort(key=self.__playerTimeJoin)
        return slots[:squadSize]

    def _updateCommandersDifficultyLevel(self):
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        if unit:
            queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
            with self.viewModel.transaction() as model:
                model.setSelectedDifficulty(QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType].value)

    def _initWindowModeSpecificData(self, model):
        super(ExtMembersView, self)._initWindowModeSpecificData(model)
        self.__initDifficultyDropdown(model)
        self._updateCommandersDifficultyLevel()

    def __initDifficultyDropdown(self, model):
        items = model.eventDifficulty.getItems()
        items.clear()
        for levelInfo in self.__getOrderedDropdownLevelsList():
            level = DifficultyDropdownItemModel()
            level.setId(levelInfo.level.value)
            level.setLabel(backport.text(R.strings.last_stand_platoon.platoon.difficulty.dyn('level_{0}'.format(levelInfo.level.value))()))
            if levelInfo.isUnlock:
                level.setShowWarningIcon(not self.__isAvailableLevelForPlayers(levelInfo))
            else:
                level.setIsDisabled(True)
            items.addViewModel(level)

        items.invalidate()
        self.__selectedLevel(self._difficultyCtrl.getSelectedLevel())

    def __getOrderedDropdownLevelsList(self):
        return sorted(self._difficultyCtrl.items.itervalues(), key=lambda item: self._DROPDOWN_ORDER.index(item.level))

    def __changeDifficulty(self, args):
        level = args.get('selectedIds')
        if level:
            self._difficultyCtrl.selectLevel(DifficultyLevel(int(level)))

    def __selectedLevel(self, level):
        model = self.viewModel.eventDifficulty.getSelected()
        model.clear()
        model.addNumber(level.value)
        model.invalidate()

    def __updateLevelStatus(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__initDifficultyDropdown(model)

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        if entity.isCommander() and unit:
            queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
            self._difficultyCtrl.selectLevel(QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType])

    def onUnitExtraChanged(self, extras):
        self._updateCommandersDifficultyLevel()
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        if unit and not unit.isInArena():
            queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
            level = QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType].value
            self.__addPlayerDifficultyLevelNotification('changedDifficultyLevel', entity.getPlayerInfo(), level)
            for player in entity.getPlayers().itervalues():
                if not player.isReady and queueType not in player.extraData.get(UNIT_LS_EXTRA_DATA_KEY, {}).get(UNIT_DIFFICULTY_LEVELS_KEY, []):
                    self.__addPlayerDifficultyLevelNotification('notReadyDifficultyLevel', player)

    def onUnitPlayerInfoChanged(self, pInfo):
        with self.viewModel.transaction() as model:
            self.__initDifficultyDropdown(model)

    def onUnitPlayerAdded(self, pInfo):
        with self.viewModel.transaction() as model:
            self.__initDifficultyDropdown(model)

    def onUnitPlayerRemoved(self, pInfo):
        with self.viewModel.transaction() as model:
            self.__initDifficultyDropdown(model)

    @adisp_process
    def _onSwitchReady(self):
        result = yield self._platoonCtrl.togglePlayerReadyAction(skipAmmocheck=True)
        if result:
            with self.viewModel.transaction() as model:
                model.btnSwitchReady.setIsEnabled(False)

    def __isAvailableLevelForPlayers(self, levelInfo):
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        for player in unit.getPlayers().itervalues():
            queueTypes = player.get('extraData', {}).get(UNIT_LS_EXTRA_DATA_KEY, {}).get(UNIT_DIFFICULTY_LEVELS_KEY, [])
            if levelInfo.queueType not in queueTypes:
                return False

        return True

    def __addPlayerDifficultyLevelNotification(self, key, pInfo, level=1):
        platoonCtrl = self._platoonCtrl
        channelCtrl = platoonCtrl.getChannelController()
        if channelCtrl:
            level = backport.text(R.strings.last_stand_lobby.difficult.dyn('level_{0}'.format(level))())
            text = backport.text(R.strings.last_stand_system_messages.unit.notification.dyn(key)(), userName=pInfo.getFullName(), level=level)
            channelCtrl.addMessage(text)

    def __updateDropdownState(self):
        with self.viewModel.transaction() as model:
            model.setSelectionDisabled(self._platoonCtrl.isInQueue())

    @staticmethod
    def __playerTimeJoin(slot):
        player = slot['player'] or {}
        roleIndex = -slot['role'] if not player.get('isOffline') else 0
        return (not player, roleIndex, player.get('timeJoin', 0))
