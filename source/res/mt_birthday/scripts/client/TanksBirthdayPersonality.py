# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/TanksBirthdayPersonality.py
from ExtensionsManager import g_extensionsManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import ExtBrowserWebHandlers
from gui.Scaleform.daapi.view.lobby.store.browser.web_handlers import ExtShopWebHandlers
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import EconomyWidgetHandler
from gui.gift_system.hubs import overrideGiftEventHub
from gui.impl.gen import R
from gui.server_events.awards_formatters import registerEntitlementWulfTooltipFormatter
from gui.shared.missions.packers.bonus import registerEntitlementBonusPackerHandler, unregisterEntitlementBonusPackerHandler
from gui.shared.system_factory import registerAwardControllerHandler, registerQuestBuilder, registerCurrencyBonusPacker
from gui_lootboxes.gui.impl.lobby.gui_lootboxes import RegisteredTooltips
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import registerHandler, unregisterHandler
from messenger.formatters.service_channel import EpicQuestAchievesFormatter
from web.web_client_api.reactive_comm import ReactiveCommunicationWebApi
from mt_birthday.gui.Scaleform import registerGiftSystemTooltipsBuilders, registerBirthdayScaleform
from mt_birthday.gui.Scaleform.daapi.view.tooltips.lobby_builders import BirthdayEconomyBonusTooltipContentWindowData, EconomyBonusContentTooltipBuilder
from mt_birthday.gui.birthday_bonus_packers import BirthdayEntitlementBonusUIPacker, BirthdayCurrencyBonusUIPacker
from mt_birthday.gui.birthday_helpers.birthday_model_helpers import entProcessor
from mt_birthday.gui.game_control import registerTanksBirthdayControllers
from mt_birthday.gui.game_control.awards_controller import BirthdayProgressionAndBadgeTokenQuestsHandler, BirthdayWelcomeTokenQuestsHandler, BirthdayChallengeTokenQuestsHandler
from mt_birthday.gui.impl.lobby.birthday.gui_lootbox_integration.unique_reward_handler import BirthdayUniqueRewardHandler
from mt_birthday.gui.impl.lobby.tooltips.golden_ticket_tooltip import GoldTicketTooltip
from mt_birthday.gui.impl.lobby.tooltips.post_stamp_tooltip import PostStampTooltip
from mt_birthday.web.web_client_api.gold_wagon.gold_wagon import GoldWagonWebApi
from mt_birthday.web.web_client_api.ticket_exchange.ticket_exchange import TicketExchangeWebApi
from mt_birthday.gui.gift_system.hubs.hub_core import GiftEventBirthdayHub
from mt_birthday.gui.gift_system.constants import GiftEventID
from mt_birthday.gui.Scaleform.daapi.view.lobby.hangar.economy_widget import BirthdayEconomyWidgetContent
from mt_birthday.birthday_constants import BIRTHDAY_STAMP_CODE, BIRTHDAY_GOLDEN_TICKET, ACCOUNT_DEFAULT_SETTINGS, BIRTHDAY_GOLDEN_TICKET_CURRENCY

def preInit():
    registerBirthdayScaleform()
    registerTanksBirthdayControllers()
    registerEntitlementWulfTooltipFormatter(BIRTHDAY_STAMP_CODE, TOOLTIPS_CONSTANTS.BIRTHDAY_GIFT_SYSTEM_POSTMARK)
    registerEntitlementWulfTooltipFormatter(BIRTHDAY_GOLDEN_TICKET, TOOLTIPS_CONSTANTS.BIRTHDAY_GOLDEN_TICKET)
    registerGiftSystemTooltipsBuilders()
    registerAwardControllerHandler(BirthdayProgressionAndBadgeTokenQuestsHandler)
    registerAwardControllerHandler(BirthdayWelcomeTokenQuestsHandler)
    registerAwardControllerHandler(BirthdayChallengeTokenQuestsHandler)
    registerHandler(BirthdayUniqueRewardHandler)
    registerCurrencyBonusPacker(BIRTHDAY_GOLDEN_TICKET_CURRENCY, BirthdayCurrencyBonusUIPacker)
    registerEntitlementBonusPackerHandler(BIRTHDAY_STAMP_CODE, BirthdayEntitlementBonusUIPacker)
    EconomyBonusContentTooltipBuilder.overrideTooltipType(BirthdayEconomyBonusTooltipContentWindowData)
    EconomyWidgetHandler.overrideWidgetContent(BirthdayEconomyWidgetContent)
    ExtShopWebHandlers.registerHandler(GoldWagonWebApi)
    ExtBrowserWebHandlers.registerHandler(GoldWagonWebApi)
    ExtBrowserWebHandlers.registerHandler(TicketExchangeWebApi)
    ExtBrowserWebHandlers.registerHandler(ReactiveCommunicationWebApi)
    from mt_birthday.birthday_messenger import registerCustomMessages, registerBirthdayTokenQuestsSubFormatters, registerBirthdayLootboxCashBackListener
    registerCustomMessages()
    registerBirthdayTokenQuestsSubFormatters()
    registerBirthdayLootboxCashBackListener()
    EpicQuestAchievesFormatter.registerHandler(entProcessor)
    from helpers.extension_components import registerExtensionClassComponent
    from gui.Scaleform.daapi.view.battle_results_window import BattleResultsWindow
    from mt_birthday.gui.Scaleform.daapi.view.battle_results_window_gifts import BattleResultsWindowGiftsComponent, GiftSystemTeamStatsLink
    from gui.battle_results.templates import RANDOM_TABS_BLOCK, STRONGHOLD_TABS_BLOCK
    registerExtensionClassComponent(BattleResultsWindow, BattleResultsWindowGiftsComponent)
    for block in (RANDOM_TABS_BLOCK, STRONGHOLD_TABS_BLOCK):
        teamStats = block.getComponent(1)
        teamStats.addNextComponent(GiftSystemTeamStatsLink('linkage'))
        teamStats.addNextComponent(GiftSystemTeamStatsLink('viewId'))

    from mt_birthday.gui.shared.event_items import BirthdayQuestGiverQuestBuilder
    registerQuestBuilder(BirthdayQuestGiverQuestBuilder, index=0)
    if IS_DEVELOPMENT:
        from gui.development.dev_web_client_api import ExtDevWebHandlers
        ExtDevWebHandlers.registerHandler(GoldWagonWebApi)
        ExtDevWebHandlers.registerHandler(TicketExchangeWebApi)


def init():
    LOG_DEBUG('init', __name__)
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)
    overrideGiftEventHub(GiftEventID.BIRTHDAY_2026, GiftEventBirthdayHub)
    from gui.server_events.bonuses import EntitlementBonus
    EntitlementBonus.extendFormattedAmount([BIRTHDAY_STAMP_CODE, BIRTHDAY_GOLDEN_TICKET])
    RegisteredTooltips.registerLootBoxSimpleTooltipHandler(R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip(), GoldTicketTooltip)
    if g_extensionsManager.isExtensionEnabled('FrontLine'):
        from gui.impl.lobby.frontline import RegisteredFrontlineTooltips
        RegisteredFrontlineTooltips.registerFrontlineSimpleTooltipHandler(R.views.mt_birthday.lobby.tooltips.PostStampTooltip(), PostStampTooltip)


def start():
    pass


def fini():
    unregisterHandler(BirthdayUniqueRewardHandler)
    unregisterEntitlementBonusPackerHandler(BIRTHDAY_STAMP_CODE)
    RegisteredTooltips.unregisterLootBoxTooltipHandler(R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip())
