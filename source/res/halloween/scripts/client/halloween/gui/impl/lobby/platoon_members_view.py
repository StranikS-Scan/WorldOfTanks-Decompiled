# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/platoon_members_view.py
from __future__ import absolute_import
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.platoon.view.platoon_members_view import SquadMembersView, BonusState
from gui.impl.gen.view_models.views.lobby.platoon.slot_model import SlotModel
from gui.impl.lobby.platoon.view.subview.platoon_chat_subview import ChatSubview
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_action_button_state_vo import SquadActionButtonStateVO
from halloween.gui.halloween_gui_constants import PREBATTLE_ACTION_NAME, DifficultyLevel, QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from halloween.gui.impl.gen.view_models.views.lobby.difficulty_dropdown_item_model import DifficultyDropdownItemModel
from halloween.gui.impl.gen.view_models.views.lobby.hw_members_window_model import HwMembersWindowModel, PrebattleTypes
from halloween.gui.impl.lobby.hw_helpers.platoon_helpers import getPlatoonSlotsData
from halloween.gui.shared.event_dispatcher import closeViewsByID, isViewLoaded
from halloween.skeletons.difficulty_level_controller import IDifficultyLevelController
from halloween_common.halloween_constants import UNIT_HALLOWEEN_EXTRA_DATA_KEY, CURRENT_QUEUE_TYPE_KEY, UNIT_DIFFICULTY_LEVELS_KEY
from helpers import i18n, dependency

class HalloweenMembersView(SquadMembersView, IGlobalListener):
    _prebattleType = PrebattleTypes.HALLOWEEN
    _layoutID = R.views.halloween.lobby.MembersWindow()
    _difficultyCtrl = dependency.descriptor(IDifficultyLevelController)

    def __init__(self, prbType):
        super(HalloweenMembersView, self).__init__(prbType)
        self.viewModel.setShouldShowFindPlayersButton(False)

    def getPrebattleType(self):
        return PREBATTLE_ACTION_NAME.HALLOWEEN

    @property
    def _viewModelClass(self):
        return HwMembersWindowModel

    @property
    def _slotModelClass(self):
        return SlotModel

    def _addSubviews(self):
        self._addSubviewToLayout(ChatSubview())

    def _onLoading(self, *args, **kwargs):
        super(HalloweenMembersView, self)._onLoading(*args, **kwargs)
        layoutID = R.views.halloween.mono.lobby.battle_result()
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        if not entity.isCommander() and unit and isViewLoaded(layoutID=layoutID):
            closeViewsByID([layoutID])

    def _onFindPlayers(self):
        pass

    def _addListeners(self):
        super(HalloweenMembersView, self)._addListeners()
        self.viewModel.eventDifficulty.onChange += self.__changeDifficulty
        self._difficultyCtrl.onChangeDifficultyLevel += self.__selectedLevel
        self._difficultyCtrl.onChangeDifficultyLevelStatus += self.__updateLevelStatus
        self.startGlobalListening()

    def _removeListeners(self):
        super(HalloweenMembersView, self)._removeListeners()
        self.viewModel.eventDifficulty.onChange -= self.__changeDifficulty
        self._difficultyCtrl.onChangeDifficultyLevel -= self.__selectedLevel
        self._difficultyCtrl.onChangeDifficultyLevelStatus -= self.__updateLevelStatus
        self.stopGlobalListening()

    def _getTitle(self):
        title = ''.join((i18n.makeString(backport.text(R.strings.platoon.squad())), i18n.makeString(backport.text(R.strings.halloween_platoon.members.header.halloween()))))
        return title

    def _getWindowInfoTooltipHeaderAndBody(self):
        tooltipHeader = backport.text(R.strings.halloween_platoon.members.header.tooltip.halloween.header())
        tooltipBody = backport.text(R.strings.halloween_platoon.members.header.tooltip.halloween.body())
        return (tooltipHeader, tooltipBody)

    def _setBonusInformation(self, bonusState):
        with self.viewModel.header.transaction() as model:
            model.setShowInfoIcon(False)
            model.setShowNoBonusPlaceholder(True)
            model.noBonusPlaceholder.setText(R.invalid())
            model.noBonusPlaceholder.setIcon(R.images.halloween.gui.maps.icons.battleTypes.c_40x40.halloween_squad())
            self._currentBonusState = bonusState

    def _getBonusState(self):
        return BonusState.NO_BONUS

    def _createHeaderInfoTooltip(self):
        tooltip = R.strings.platoon.members.header.noBonusPlaceholder.tooltip
        header = backport.text(tooltip.header())
        body = backport.text(tooltip.body())
        return self._createSimpleTooltipContent(header=header, body=body)

    def _updateMembers(self):
        super(HalloweenMembersView, self)._updateMembers()
        self.__updateDropdownState()

    def _getActionButtonStateInfo(self):
        result = self._platoonCtrl.getPrbEntity().canPlayerDoAction()
        actionButtonStateVO = SquadActionButtonStateVO(self._platoonCtrl.getPrbEntity())
        isEnabled = actionButtonStateVO['isEnabled']
        onlyReadinessText = actionButtonStateVO.isReadinessTooltip()
        if result.restriction == UNIT_RESTRICTION.VEHICLE_NOT_VALID:
            simpleState = backport.text(R.strings.halloween_platoon.platoon.simpleState.lockVehicle())
            toolTipData = ''
        elif result.restriction == UNIT_RESTRICTION.UNIT_WRONG_DATA:
            simpleState = backport.text(R.strings.halloween_platoon.platoon.simpleState.notAvailableLevel())
            toolTipData = ''
        elif result.restriction == UNIT_RESTRICTION.MODE_NOT_AVAILABLE:
            simpleState = backport.text(R.strings.halloween_platoon.platoon.simpleState.difficultyDisabled())
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
        super(HalloweenMembersView, self)._initWindowModeSpecificData(model)
        self.__initDifficultyDropdown(model)
        self._updateCommandersDifficultyLevel()

    def __initDifficultyDropdown(self, model):
        items = model.eventDifficulty.getItems()
        items.clear()
        for levelInfo in self._difficultyCtrl.getLevelsInfo():
            level = DifficultyDropdownItemModel()
            level.setId(levelInfo.level.value)
            level.setLabel(backport.text(R.strings.halloween_platoon.platoon.difficulty.dyn('level_{0}'.format(levelInfo.level.value))()))
            if levelInfo.isUnlock:
                level.setShowWarningIcon(not self.__isAvailableLevelForPlayers(levelInfo))
            else:
                level.setIsDisabled(True)
            items.addViewModel(level)

        items.invalidate()
        self.__selectedLevel(self._difficultyCtrl.getSelectedLevel())

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

    def onUnitExtraChanged(self, extra):
        self._updateCommandersDifficultyLevel()
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        if unit and not unit.isInArena():
            queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
            level = QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType].value
            self.__addPlayerDifficultyLevelNotification('changedDifficultyLevel', entity.getPlayerInfo(), level)
            for player in entity.getPlayers().values():
                if not player.isReady and queueType not in player.extraData.get(UNIT_HALLOWEEN_EXTRA_DATA_KEY, {}).get(UNIT_DIFFICULTY_LEVELS_KEY, []):
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

    def __isAvailableLevelForPlayers(self, levelInfo):
        entity = self._platoonCtrl.getPrbEntity()
        _, unit = entity.getUnit()
        for player in unit.getPlayers().values():
            queueTypes = player.get('extraData', {}).get(UNIT_HALLOWEEN_EXTRA_DATA_KEY, {}).get(UNIT_DIFFICULTY_LEVELS_KEY, [])
            if levelInfo.queueType not in queueTypes:
                return False

        return True

    def __addPlayerDifficultyLevelNotification(self, key, pInfo, level=1):
        platoonCtrl = self._platoonCtrl
        channelCtrl = platoonCtrl.getChannelController()
        if channelCtrl:
            level = backport.text(R.strings.halloween_lobby.difficult.dyn('level_{0}'.format(level))())
            text = backport.text(R.strings.halloween_system_messages.unit.notification.dyn(key)(), userName=pInfo.getFullName(), level=level)
            channelCtrl.addMessage(text)

    def __updateDropdownState(self):
        with self.viewModel.transaction() as model:
            model.setSelectionDisabled(self._platoonCtrl.isInQueue())

    @staticmethod
    def __playerTimeJoin(slot):
        player = slot['player'] or {}
        roleIndex = -slot['role'] if not player.get('isOffline') else 0
        return (not player, roleIndex, player.get('timeJoin', 0))
