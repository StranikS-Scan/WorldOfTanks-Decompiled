# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/__init__.py


def registerComp7Lobby():
    from comp7_common.comp7_constants import ARENA_GUI_TYPE, PREBATTLE_TYPE, Configs
    from comp7_common_const import COMP7_OFFER_PREFIX
    from comp7.gui.comp7_constants import SELECTOR_BATTLE_TYPES
    from comp7.gui.selectable_reward.constants import Features
    from comp7.gui.server_events.bonuses import comp7TokensFactory
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.daily_quest_widget import Comp7QuestWidgetComponent
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import Comp7TournamentQuestFlagsGetter
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags import Comp7QuestsFlag
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_constants import QuestFlagTypes
    from comp7.gui.Scaleform.daapi.view.lobby.rally.action_button_state_vo import unitRestrictionsGetter
    from comp7.gui.game_control.award_controller import Comp7QuestRewardHandler, Comp7InvoiceRewardHandler, Comp7PunishWindowHandler
    from comp7.gui.hangar_presets.hangar_presets_getters import Comp7PresetsGetter
    from comp7.notification.actions_handlers import Comp7OpenPunishmentWindowHandler
    from comp7.notification.listeners import Comp7OfferTokenListener
    from comp7.web.web_client_api import Comp7WebApi, Comp7OpenWindowWebApi
    from constants import ARENA_BONUS_TYPE, ARENA_BONUS_TYPE_IDS, EVENT_TYPE, QUEUE_TYPE
    from gui.event_boards.event_boards_items import EventSettings
    from gui.game_control.GameSessionController import GameSessionController
    from gui.game_control.platoon_controller import PlatoonController
    from gui.graphics_optimization_controller.utils import OptimizationSetting
    from gui.hangar_presets.hangar_presets_getters import SpecBattlePresetsGetter
    from gui.Scaleform.daapi.view.lobby.hangar.daily_quest_widget import DailyQuestWidget
    from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
    from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import _EXT_FIGHT_BUTTON_TOOLTIP_GETTERS
    from gui.Scaleform.daapi.view.lobby.store.browser.web_handlers import _SHOP_HANDLERS
    from gui.Scaleform.daapi.view.lobby.rally.action_button_state_vo import _EXT_INVALID_UNIT_MESSAGE_GETTERS
    from gui.Scaleform.daapi.view.lobby.trainings.TrainingSettingsWindow import CONFIG_KEYS_FOR_UPDATE
    from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
    from gui.Scaleform.daapi.view.lobby.formatters.tooltips import _MODENAME_TO_PO_FILE
    from gui.selectable_reward.constants import FEATURE_TO_PREFIX
    from gui.server_events.bonuses import _BONUSES
    from gui.shared.system_factory import registerAwardControllerHandlers, registerNotificationsListeners, registerOptimizedViews, registerQuestFlag
    from gui.impl.lobby.crew.widget.crew_widget import CrewWidget
    from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_model import SlotSizeMode
    from messenger.formatters.service_channel import AchievementFormatter
    from notification.actions_handlers import _AVAILABLE_HANDLERS, _OpenPunishmentWindowHandler
    from web.web_client_api.ui import OpenWindowWebApi
    registerAwardControllerHandlers((Comp7QuestRewardHandler, Comp7InvoiceRewardHandler, Comp7PunishWindowHandler))
    registerNotificationsListeners((Comp7OfferTokenListener,))
    registerOptimizedViews({HANGAR_ALIASES.COMP7_TANK_CAROUSEL: OptimizationSetting()})
    registerQuestFlag(QuestFlagTypes.COMP7, Comp7QuestsFlag)
    SpecBattlePresetsGetter._GUI_TYPE_TO_SETTINGS.update({ARENA_GUI_TYPE.TOURNAMENT_COMP7: SpecBattlePresetsGetter._SpecGuiSettings(ARENA_BONUS_TYPE.TOURNAMENT_COMP7, Comp7PresetsGetter.getBattleModifiers, Comp7TournamentQuestFlagsGetter, DefaultLobbyHeaderHelper)})
    _EXT_FIGHT_BUTTON_TOOLTIP_GETTERS.append(_fightButtonTooltipGetter)
    _EXT_INVALID_UNIT_MESSAGE_GETTERS.append(unitRestrictionsGetter)
    _AVAILABLE_HANDLERS.remove(_OpenPunishmentWindowHandler)
    _AVAILABLE_HANDLERS.append(Comp7OpenPunishmentWindowHandler)
    _MODENAME_TO_PO_FILE.update({SELECTOR_BATTLE_TYPES.COMP7: 'comp7_ext'})
    FEATURE_TO_PREFIX.update({Features.COMP7: COMP7_OFFER_PREFIX})
    _BONUSES['tokens'].update({'default': comp7TokensFactory,
     EVENT_TYPE.BATTLE_QUEST: comp7TokensFactory,
     EVENT_TYPE.TOKEN_QUEST: comp7TokensFactory,
     EVENT_TYPE.PERSONAL_QUEST: comp7TokensFactory,
     EVENT_TYPE.ELEN_QUEST: comp7TokensFactory})
    EventSettings._CUSTOM_UI_BATTLE_TYPES.append(ARENA_BONUS_TYPE.COMP7)
    PlatoonController.SQUAD_SIZE_SELECT_PREBATTLE_TYPES.append(PREBATTLE_TYPE.COMP7)
    _SHOP_HANDLERS.remove(OpenWindowWebApi)
    _SHOP_HANDLERS.extend((Comp7WebApi, Comp7OpenWindowWebApi))
    GameSessionController._QUEUE_TYPE_TO_CONFIG_TIME_KEY.update({QUEUE_TYPE.COMP7: ARENA_BONUS_TYPE_IDS[ARENA_BONUS_TYPE.COMP7]})
    CrewWidget.PREBATTLE_TYPE_TO_SLOT_MODE.update({QUEUE_TYPE.COMP7: SlotSizeMode.COMPACT})
    DailyQuestWidget.COMPONENT_TYPES.append(Comp7QuestWidgetComponent)
    CONFIG_KEYS_FOR_UPDATE.add(Configs.COMP7_CONFIG.value)
    AchievementFormatter._HIDDEN_ACHIEVES.update({'comp7_4_yearly_iron',
     'comp7_4_yearly_bronze',
     'comp7_4_yearly_silver',
     'comp7_4_yearly_gold',
     'comp7_4_yearly_champion',
     'comp7_4_yearly_legend'})


def _fightButtonTooltipGetter(pValidation):
    from CurrentVehicle import g_currentVehicle
    from comp7.gui.Scaleform.daapi.view.lobby.header.helpers.fight_btn_tooltips import getComp7BattlesOnlyVehicleTooltipData
    return getComp7BattlesOnlyVehicleTooltipData(pValidation) if g_currentVehicle.isOnlyForComp7Battles() and (g_currentVehicle.isUnsuitableToQueue() or g_currentVehicle.isDisabledInRent()) else None
