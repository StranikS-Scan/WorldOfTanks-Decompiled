# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/reward_selection_view.py
from __future__ import absolute_import
import json
from adisp import adisp_process
from frameworks.wulf import WindowFlags, ViewSettings
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.recruit_helper import getRecruitInfo
from halloween.gui.impl.gen.view_models.views.lobby.reward_selection_view_model import RewardSelectionViewModel, GenderEnum
from halloween.gui.impl.gen.view_models.views.lobby.reward_view_model import RewardViewModel
from halloween.gui.impl.lobby.base_view import BaseView
from halloween.gui.impl.lobby.hw_helpers import getImgName, HalloweenBonusesAwardsComposer
from halloween.gui.impl.lobby.hw_helpers.bonuses_formatters import getHWTwitchAwardFormatter
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_twitch_con_controller import IHalloweenTwitchConController
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.impl import IGuiLoader
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class RewardSelectionView(BaseView):
    _MAX_BONUSES_IN_VIEW = 1
    _guiLoader = dependency.descriptor(IGuiLoader)
    _hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwTwitchCtrl = dependency.descriptor(IHalloweenTwitchConController)

    def __init__(self):
        settings = ViewSettings(R.views.halloween.mono.lobby.reward_selection(), model=RewardSelectionViewModel())
        super(RewardSelectionView, self).__init__(settings)
        self.__bonusCache = {}
        self.__idGen = SequenceIDGenerator()

    @property
    def viewModel(self):
        return super(RewardSelectionView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(RewardSelectionView, self).createToolTip(event)

    def _getEvents(self):
        return [(self.viewModel.onClose, self.__onClose),
         (self.viewModel.onClaim, self.__onClaim),
         (self._hwTwitchCtrl.onCertificateCountUpdated, self.__fillViewModel),
         (self._hwTwitchCtrl.onLimitsUpdated, self.__fillViewModel),
         (self._hwTwitchCtrl.onTwitchConSettingsUpdated, self.__fillViewModel)]

    def __onClose(self):
        self.destroyWindow()

    def __onClaim(self, args):
        if args is None:
            return
        else:
            selectedItems = json.loads(args.get('selectedItems', '[]'))
            dictResult = {}
            for item in selectedItems:
                dictResult[item] = dictResult.get(item, 0) + 1

            self.__processSelection(list(dictResult.items()))
            self.destroyWindow()
            return

    def _onLoading(self, *args, **kwargs):
        super(RewardSelectionView, self)._onLoading()
        self.__fillViewModel()

    def __fillViewModel(self):
        with self.viewModel.transaction() as model:
            recruitInfo = [ getRecruitInfo(t) for c in self._hwTwitchCtrl.commanders() for r in c.bonuses for t in r.getTokens() ]
            gender = GenderEnum.MALE if any((info and not info.isFemale() for info in recruitInfo)) else GenderEnum.FEMALE
            rewards = model.getRewards()
            rewards.clear()
            model.setMaxCertificates(self._hwTwitchCtrl.getCertificateCount())
            model.setGender(gender)
            for commander in self._hwTwitchCtrl.commanders():
                remainLimit = self._hwTwitchCtrl.getRemainLimits(commander.commanderID)
                if remainLimit == 0:
                    continue
                reward = RewardViewModel()
                reward.setId(commander.commanderID)
                formatter = HalloweenBonusesAwardsComposer(self._MAX_BONUSES_IN_VIEW, getHWTwitchAwardFormatter())
                bonusRewards = formatter.getFormattedBonuses(commander.bonuses, AWARDS_SIZES.BIG)
                for bonus in bonusRewards:
                    tooltipId = '{}'.format(next(self.__idGen))
                    self.__bonusCache[tooltipId] = bonus
                    reward.setName(bonus.userName)
                    reward.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
                    reward.setTooltipId(tooltipId)

                reward.setMaxCount(remainLimit)
                rewards.addViewModel(reward)

            rewards.invalidate()

    @adisp_process
    def __processSelection(self, data):
        yield self._hwTwitchCtrl.exchangeCommander(data)


class RewardSelectionWindow(LobbyNotificationWindow):

    def __init__(self, layoutID, parent=None):
        super(RewardSelectionWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=RewardSelectionView(), parent=parent)
        self._args = (layoutID,)

    def isParamsEqual(self, *args):
        return self._args == args
