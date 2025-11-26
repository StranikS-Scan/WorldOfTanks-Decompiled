# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/auto_open_view.py
from constants import LOOTBOX_TOKEN_PREFIX
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.auto_open_view_model import AutoOpenViewModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl, WindowImpl
from gui.lootbox_system.base.bonuses_helpers import REWARDS_GROUP_NAME_RES, RewardsGroup, getGoodiesFilter, getItemsFilter, getTankmenFilter, getVehiclesFilter, isBattleBooster, isCrewBook, noCompensation, isOptionalDevice, packBonusGroups
from gui.lootbox_system.base.common import LOOTBOX_COMPENSATION_TOKEN_PREFIX
from gui.lootbox_system.base.views_loaders import showItemPreview
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache

class AutoOpenView(ViewImpl):
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, ctx):
        settings = ViewSettings(R.views.mono.lootbox.auto_open(), model=AutoOpenViewModel())
        super(AutoOpenView, self).__init__(settings)
        self.__eventName = ctx.get('eventName')
        self.__rewards = self.__filterRewards(ctx.get('rewards'))
        self.__boxes = ctx.get('boxes')
        self.__tooltips = {}

    @property
    def viewModel(self):
        return super(AutoOpenView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(AutoOpenView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(AutoOpenView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setEventName(self.__eventName)
            tx.setBoxesQuantity(sum(self.__boxes.values()))
        self.__updateRewards()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onPreview, self.__showPreview))

    def __updateRewards(self):
        with self.getViewModel().transaction() as tx:
            packBonusGroups(bonuses=self.__rewards, groupModels=tx.getRewardRows(), groupsLayout=self.__getGroupsLayout(), tooltipsData=self.__tooltips, packer=None, eventName=self.__eventName)
        return

    @classmethod
    def __getGroupsLayout(cls):
        layout = (RewardsGroup(name=REWARDS_GROUP_NAME_RES.vehicles(), bonusTypes=('vehicles',), bonuses={}, filterFuncs=(getVehiclesFilter((noCompensation,)),)),
         RewardsGroup(name=REWARDS_GROUP_NAME_RES.customizations(), bonusTypes=('customizations',), bonuses={}, filterFuncs=None),
         RewardsGroup(name=REWARDS_GROUP_NAME_RES.crewBooksAndCrew(), bonusTypes=('items', 'goodies', 'tokens', 'crewSkins'), bonuses={}, filterFuncs=(getItemsFilter((isCrewBook,)), getGoodiesFilter((cls.__goodiesCache.getRecertificationForm, cls.__goodiesCache.getMentoringLicense)), getTankmenFilter)),
         RewardsGroup(name=REWARDS_GROUP_NAME_RES.optionalDevicesAndBattleBoosters(), bonusTypes=('items', 'goodies'), bonuses={}, filterFuncs=(getItemsFilter((isOptionalDevice, isBattleBooster)), getGoodiesFilter((cls.__goodiesCache.getDemountKit,)))),
         RewardsGroup(name=REWARDS_GROUP_NAME_RES.other(), bonusTypes=(), bonuses={}, filterFuncs=None))
        return layout

    def __showPreview(self, ctx):
        showItemPreview(str(ctx.get('bonusType')), int(ctx.get('bonusId')), int(ctx.get('styleID')))

    def __onClose(self):
        from gui.Scaleform.lobby_entry import getLobbyStateMachine
        lsm = getLobbyStateMachine()
        lsm.getStateFromView(self).goBack()

    def __filterRewards(self, rewards):
        for tokenName in rewards.get('tokens', {}).keys():
            if tokenName.startswith((LOOTBOX_TOKEN_PREFIX, LOOTBOX_COMPENSATION_TOKEN_PREFIX)):
                rewards['tokens'].pop(tokenName, None)

        if not rewards.get('tokens'):
            rewards.pop('tokens', None)
        return rewards


class AutoOpenWindow(WindowImpl):

    def __init__(self, layer, ctx=None, *args, **kwargs):
        super(AutoOpenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=AutoOpenView(ctx), layer=layer)
