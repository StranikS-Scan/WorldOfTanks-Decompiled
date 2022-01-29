# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_ny_model_helpers.py
import typing
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LUNAR_NY_PROGRESSION_TOKENS_VIEWED
from gui.shared.missions.packers.bonus import BonusUIPacker
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_bonuses_packers import getLunarNYBonusPackerMap, getLunarNYProgressionPackerMap
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.gen.view_models.views.lobby.lunar_ny.progression_level_model import ProgressionLevelModel
from items.components.lunar_ny_constants import CharmBonuses
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.lunar_ny.bonuses_model import BonusesModel
    from gui.impl.gen.view_models.views.lobby.lunar_ny.charm_model import CharmModel
    from lunar_ny.lunar_ny_charm import LunarNYCharm
    from lunar_ny.lunar_ny_constants import EnvelopeTypes
    from gui.impl.backport import TooltipData
    from gui.server_events.bonuses import SimpleBonus

def fillEnvelopesProgressionModel(model, config, sentEnvelopes, withBonuses=False, tooltipsData=None):
    model.setEnvelopesSent(sentEnvelopes)
    model.setLastViewedEnvelopesSent(AccountSettings.getSettings(LUNAR_NY_PROGRESSION_TOKENS_VIEWED))
    progressionLevel = model.getProgressionLevels()
    progressionLevel.clear()
    for level in config.getLevels():
        levelModel = ProgressionLevelModel()
        levelModel.setLevel(level.getLevel())
        minEnvelopes, maxEnvelopes = level.getEnvelopesRange()
        levelModel.setMinEnvelopes(minEnvelopes)
        levelModel.setMaxEnvelopes(-1 if maxEnvelopes == float('inf') else maxEnvelopes)
        if withBonuses:
            packBonusModelAndTooltipData(level.getBonuses(), levelModel.getRewards(), tooltipsData, uniquePackerMap=getLunarNYProgressionPackerMap())
        progressionLevel.addViewModel(levelModel)

    progressionLevel.invalidate()


def updateCharmModel(charm, model):
    model.setCharmID(charm.getID())
    model.setCount(charm.getCountInStorage())
    model.setCharmType(charm.getItemType())
    model.setIsNew(charm.getUnseenCount() > 0)
    updateCharmBonusesModel(charm.getBonuses(), model.bonuses)


def updateCharmBonusesModel(charmBonuses, bonusesModel):
    bonusesModel.setCredits(int(round(charmBonuses.get(CharmBonuses.CREDITS.value, 0) * 100)))
    bonusesModel.setCrewExperience(int(round(charmBonuses.get(CharmBonuses.TANKMEN_XP.value, 0) * 100)))
    bonusesModel.setFreeExperience(int(round(charmBonuses.get(CharmBonuses.FREE_XP.value, 0) * 100)))
    bonusesModel.setCombatExperience(int(round(charmBonuses.get(CharmBonuses.XP.value, 0) * 100)))


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, lunarNYController=ILunarNYController)
def getRewardsByEnvelopeType(envelopeType, lobbyContext=None, lunarNYController=None):
    lootboxID = lunarNYController.receivedEnvelopes.getLootBoxIDByEnvelopeType(envelopeType)
    lootboxConfig = lobbyContext.getServerSettings().getLootBoxConfig()
    configBonuses = []
    if lootboxID in lootboxConfig:
        configBonuses = lootboxConfig[lootboxID]['bonus']
    else:
        _logger.error('Unsupported lootboxID %s', lootboxID)
    return configBonuses


def packBonusModelAndTooltipData(bonuses, rewardModels, tooltipData=None, uniquePackerMap=None):
    bonusIndexTotal = len(tooltipData) if tooltipData is not None else 0
    packer = BonusUIPacker(getLunarNYBonusPackerMap() if uniquePackerMap is None else uniquePackerMap)
    rewardModels.clear()
    for bonus in bonuses:
        bonusList = packer.pack(bonus)
        bonusTooltipList = []
        tooltipContents = []
        if bonusList and tooltipData is not None:
            bonusTooltipList = packer.getToolTip(bonus)
            tooltipContents = packer.getContentId(bonus)
        for bonusIndex, item in enumerate(bonusList):
            rewardModels.addViewModel(item)
            if tooltipData is not None and bonusTooltipList:
                tooltipIdx = bonusIndexTotal
                packer.getPackers().get(bonus.getName()).packToolTip(item, tooltipIdx, tooltipContents[bonusIndex])
                tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                bonusIndexTotal += 1

    rewardModels.invalidate()
    return
