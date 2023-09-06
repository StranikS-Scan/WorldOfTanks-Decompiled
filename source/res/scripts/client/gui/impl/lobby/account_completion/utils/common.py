# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/utils/common.py
import typing
from enum import Enum
from constants import EMAIL_CONFIRMATION_QUEST_ID
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData, getDefaultBonusPacker
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.account_completion.add_credentials_model import AddCredentialsModel
    from gui.impl.gen.view_models.views.lobby.account_completion.common.base_wgnp_overlay_view_model import BaseWgnpOverlayViewModel
    from gui.impl.backport import TooltipData
    from typing import Dict
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
SUPPORT_URL = 'accountCompletionSupportURL'

class AccountCompletionType(str, Enum):
    UNDEFINED = 'undefined'
    SOI = 'soi'
    DOI = 'doi'


def _keyBonusesOrder(bonus):
    return _BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _BONUSES_ORDER else len(_BONUSES_ORDER)


def getBonuses():
    eventsCache = dependency.instance(IEventsCache)
    quest = eventsCache.getHiddenQuests().get(EMAIL_CONFIRMATION_QUEST_ID)
    return quest.getBonuses() if quest is not None else []


def fillRewards(model, bonuses=None, tooltipItems=None):
    bonuses = bonuses or getBonuses()
    bonuses.sort(key=_keyBonusesOrder)
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
