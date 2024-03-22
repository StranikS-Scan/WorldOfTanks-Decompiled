# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/utils/common.py
import typing
from constants import EMAIL_CONFIRMATION_QUEST_ID
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.gen import R
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData, getDefaultBonusPacker
from gui.shared.money import Currency
from helpers import dependency
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.account_completion.add_credentials_model import AddCredentialsModel
    from gui.impl.gen.view_models.views.lobby.account_completion.common.base_wgnp_overlay_view_model import BaseWgnpOverlayViewModel
    from gui.impl.gen.view_models.views.lobby.account_completion.steam_email_confirm_rewards_view_model import SteamEmailConfirmRewardsViewModel
    from gui.impl.gen.view_models.views.lobby.account_completion.tooltips.hangar_tooltip_model import HangarTooltipModel
    from gui.impl.backport import TooltipData
    from gui.server_events.event_items import TokenQuest
    from typing import Optional, List, Dict, Union
_BONUSES_ORDER = ('vehicles',
 'premium',
 Currency.CRYSTAL,
 Currency.GOLD,
 'freeXP',
 'freeXPFactor',
 Currency.CREDITS,
 'creditsFactor',
 'tankmen',
 'items',
 'slots',
 'berths',
 'dossier',
 'customizations',
 'tokens',
 'goodies',
 Currency.EVENT_COIN)
RESTRICTED_REQUEST_MIN_TIME = 5
DISABLE_BUTTON_TIME = 90

def _keyBonusesOrder(bonus):
    return _BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _BONUSES_ORDER else len(_BONUSES_ORDER)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getEmailConfirmationQuest(eventsCache=None):
    quests = eventsCache.getHiddenQuests(filterFunc=lambda quest: quest.getID() == EMAIL_CONFIRMATION_QUEST_ID)
    return None if not quests else first(quests.values())


def getSteamEmailConfirmBonuses(rewards=None):
    if rewards:
        bonuses = _createSteamEmailConfirmBonuses(rewards)
    else:
        bonuses = _getSteamEmailConfirmBonusesFromQuest()
    return sorted(bonuses, key=_keyBonusesOrder)


def fillRewards(model, rewards=None, tooltipItems=None):
    bonuses = getSteamEmailConfirmBonuses(rewards)
    bonusesListModel = model.getBonuses()
    bonusesListModel.clear()
    packMissionsBonusModelAndTooltipData(bonuses=bonuses, packer=getDefaultBonusPacker(), model=bonusesListModel, tooltipData=tooltipItems)
    bonusesListModel.invalidate()


def showAccountAlreadyHasEmail(viewModel):
    with viewModel.transaction() as model:
        model.setIsTitleOnly(True)
        model.setTitle(R.strings.dialogs.accountCompletion.emailOverlay.alreadyConfirmed.title())
        model.setSubTitle(R.strings.dialogs.accountCompletion.emailOverlay.alreadyConfirmed.subTitle())


def openMenu():
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)


def _createSteamEmailConfirmBonuses(rewards):
    bonuses = []
    for key, value in rewards.items():
        bonus = getNonQuestBonuses(key, value)
        if bonus:
            bonuses.extend(bonus)

    return bonuses


def _getSteamEmailConfirmBonusesFromQuest():
    emailConfirmationQuest = getEmailConfirmationQuest()
    return [] if emailConfirmationQuest is None else emailConfirmationQuest.getBonuses()
