# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/event_mission_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.server_events.awards_formatters import AWARDS_SIZES
from last_stand.gui.game_control.ls_artefacts_controller import compareBonusesByPriority
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.event_mission_tooltip_view_model import EventMissionTooltipViewModel
from last_stand.gui.impl.lobby.ls_helpers import getArtefactState
from last_stand.gui.impl.lobby.ls_helpers.bonuses_formatters import LSBonusesAwardsComposer, getImgName, getLSMetaAwardFormatter
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_artefacts_controller import Artefact

class EventMissionsTooltip(ViewImpl):
    __slots__ = ('__selectedArtefactID', '__isHangar')
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsCtrl = dependency.descriptor(ILSController)
    _MAX_BONUSES_IN_VIEW = 5

    def __init__(self, selectedArtefactID, isHangar):
        settings = ViewSettings(R.views.last_stand.mono.lobby.tooltips.mission_tooltip())
        settings.model = EventMissionTooltipViewModel()
        super(EventMissionsTooltip, self).__init__(settings)
        self.__selectedArtefactID = selectedArtefactID
        self.__isHangar = isHangar

    @property
    def viewModel(self):
        return super(EventMissionsTooltip, self).getViewModel()

    def _onLoading(self):
        super(EventMissionsTooltip, self)._onLoading()
        artefact = self.lsArtifactsCtrl.getArtefact(self.__selectedArtefactID)
        finalArtefact = self.lsArtifactsCtrl.getFinalArtefact()
        if artefact is None:
            return
        else:
            with self.viewModel.transaction() as tx:
                tx.setIsHangar(self.__isHangar)
                tx.setSkipPrice(artefact.skipPrice.amount)
                tx.setDecodePrice(artefact.decodePrice.amount)
                tx.setId(self.__selectedArtefactID)
                tx.setIndex(self.lsArtifactsCtrl.getIndex(artefact.artefactID))
                tx.setName(artefact.questConditions.name)
                tx.setDescription(artefact.questConditions.description.replace('\\n', '\n'))
                tx.setRegularArtefactCount(self.lsArtifactsCtrl.getMaxArtefactsProgress())
                tx.setEndDate(int(self.lsCtrl.getModeSettings().endDate))
                tx.setState(getArtefactState(self.__selectedArtefactID))
                tx.setIsKingReward(artefact.artefactID == finalArtefact.artefactID)
                rewardsVM = tx.getRewards()
                bonusRewards = artefact.bonusRewards
                formatter = LSBonusesAwardsComposer(self._MAX_BONUSES_IN_VIEW, getLSMetaAwardFormatter())
                sortedBonuses = sorted(bonusRewards, cmp=compareBonusesByPriority)
                bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
                for bonus in bonusRewards:
                    reward = BonusItemViewModel()
                    reward.setUserName(str(bonus.userName))
                    reward.setName(bonus.bonusName)
                    reward.setValue(str(bonus.label))
                    reward.setLabel(str(bonus.label))
                    reward.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
                    reward.setOverlayType(bonus.getOverlayType(AWARDS_SIZES.SMALL))
                    rewardsVM.addViewModel(reward)

            return
