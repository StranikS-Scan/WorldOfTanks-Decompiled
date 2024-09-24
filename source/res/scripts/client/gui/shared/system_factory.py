# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/system_factory.py
from collections import defaultdict
BATTLE_REPO = 1
EQUIPMENT_ITEMS = 2
SCALEFORM_COMMON_PACKAGES = 3
SCALEFORM_LOBBY_PACKAGES = 4
SCALEFORM_BATTLE_PACKAGES = 5
LOBBY_TOOLTIP_BUILDERS = 6
BATTLE_TOOLTIP_BUILDERS = 7
GAME_CONTROLLERS = 8
QUEUE = 9
QUEUE_ENTRY_POINT = 10
UNIT_ENTITY = 11
UNIT_ENTRY_POINT = 12
UNIT_ENTITY_BY_TYPE = 13
UNIT_ENTRY_POINT_BY_TYPE = 14
PBR_STORAGE = 15
PRB_INVITE_HTML_FORMATTER = 16
NOTIFICATIONS_LISTENERS = 17
NOTIFICATIONS_ACTIONS_HANDLERS = 18
MESSENGER_CLIENT_FORMATTERS = 19
TOKEN_QUEST_SUBFORMATTERS = 20
MODE_SELECTOR_ITEM = 21
MODE_SELECTOR_TOOLTIP = 22
BANNER_ENTRY_POINT_VALIDATOR = 23
BATTLE_QUEUE_PROVIDER = 24
BATTLE_TIPS_CRITERIA = 25
ARENA_DESCRIPTION = 26
ARENA_SQUAD_FINDER = 27
INGAME_HELP_PAGES_BUILDERS = 28
QUEST_BUILDERS = 29
AWARD_CONTROLLER_HANDLERS = 30
CAN_SELECT_PRB_ENTITY = 31
BATTLE_RESULT_STATS_CONTROLLER = 32
SEASON_PROVIDER_HANDLER = 33
MESSENGER_SERVER_FORMATTERS = 34
CAROUSEL_EVENTS_ENTRIES = 35
BANNER_ENTRY_POINT_LUI_RULE = 36
LIMITED_UI_TOKENS = 37
PRB_MODE_NAME_KWARGS = 38
QUEUE_MODE_NAME_KWARGS = 39
BONUS_TYPE_MODE_NAME_KWARGS = 40
PRB_CONDITION_ICON = 41
HANGAR_PRESETS_READERS = 42
HANGAR_PRESETS_PROCESSORS = 43
AMMUNITION_PANEL_VIEW = 44
VEHICLE_VIEW_STATE = 45
DYN_OBJ_CACHE = 46
SHARED_REPO = 47
CONTEXT_MENU_COMMANDS = 48
CONTEXT_MENU_OPTION_BUILDER = 49
ADVANCED_CHAT_COMPONENT = 50
BATTLE_CHANEL_CONTROLLER = 51
HIT_DIRECTION_CONTROLLER = 52
CUSTOMIZATION_HANGAR_AVAILABLE = 53
OPTIMIZED_VIEWS = 54
REPLAY_MODE_TAG = 55
QUEST_FLAGS = 56
BATTLE_RESULTS_STATS_SORTING = 57
LOOTBOX_AUTOOPEN_SUBFORMATTERS = 58
EQUIPMENT_TRIGGERS = 59

class _CollectEventsManager(object):

    def __init__(self):
        self.__handlers = defaultdict(list)

    def addListener(self, eventID, callback):
        self.__handlers[eventID].append(callback)

    def handleEvent(self, eventID, ctx):
        for callback in self.__handlers[eventID]:
            callback(ctx)

        return ctx

    @property
    def handlers(self):
        return self.__handlers


__collectEM = _CollectEventsManager()

def registerScaleformBattlePackages(guiType, packages):

    def onCollect(ctx):
        ctx['packages'].extend(packages)

    __collectEM.addListener((SCALEFORM_BATTLE_PACKAGES, guiType), onCollect)


def collectScaleformBattlePackages(guiType):
    return __collectEM.handleEvent((SCALEFORM_BATTLE_PACKAGES, guiType), {'packages': []})['packages']


def registerScaleformLobbyPackages(packages):

    def onCollect(ctx):
        ctx['packages'].extend(packages)

    __collectEM.addListener(SCALEFORM_LOBBY_PACKAGES, onCollect)


def collectScaleformLobbyPackages():
    return __collectEM.handleEvent(SCALEFORM_LOBBY_PACKAGES, {'packages': []})['packages']


def registerBattleTooltipsBuilders(builders):

    def onCollect(ctx):
        ctx['builders'].extend(builders)

    __collectEM.addListener(BATTLE_TOOLTIP_BUILDERS, onCollect)


def collectBattleTooltipsBuilders():
    return __collectEM.handleEvent(BATTLE_TOOLTIP_BUILDERS, {'builders': []})['builders']


def registerLobbyTooltipsBuilders(builders):

    def onCollect(ctx):
        ctx['builders'].extend(builders)

    __collectEM.addListener(LOBBY_TOOLTIP_BUILDERS, onCollect)


def collectLobbyTooltipsBuilders():
    return __collectEM.handleEvent(LOBBY_TOOLTIP_BUILDERS, {'builders': []})['builders']


def registerEquipmentItem(equipmentName, itemCls, replayItemCls):

    def onCollect(ctx):
        descriptor, quantity, stage, timeRemaining, totalTime = ctx['args']
        cls = replayItemCls if ctx['isReplay'] else itemCls
        ctx['item'] = cls(descriptor, quantity, stage, timeRemaining, totalTime, descriptor.tags)

    __collectEM.addListener((EQUIPMENT_ITEMS, equipmentName), onCollect)


def collectEquipmentItem(equipmentName, isReplay, args):
    return __collectEM.handleEvent((EQUIPMENT_ITEMS, equipmentName), {'args': args,
     'isReplay': isReplay}).get('item', None)


def registerEquipmentTrigger(equipmentPrefix, itemCls, replayItemCls):

    def onCollect(ctx):
        if not ctx['equipmentName'].startswith(equipmentPrefix):
            return
        cls = replayItemCls if ctx['isReplay'] else itemCls
        ctx['item'] = cls

    __collectEM.addListener(EQUIPMENT_TRIGGERS, onCollect)


def collectEquipmentTrigger(equipmentName, isReplay):
    return __collectEM.handleEvent(EQUIPMENT_TRIGGERS, {'equipmentName': equipmentName,
     'isReplay': isReplay}).get('item', None)


def registerGameControllers(controllersList):

    def onCollect(ctx):
        configurator = ctx['configurator']
        for iface, controllerCls, replace in controllersList:
            configurator(iface, controllerCls(), replace)

    __collectEM.addListener(GAME_CONTROLLERS, onCollect)


def collectGameControllers(configurator):
    __collectEM.handleEvent(GAME_CONTROLLERS, ctx={'configurator': configurator})


def registerBattleControllerRepo(guiType, repoCls):

    def onCollect(ctx):
        ctx['repo'] = repoCls.create(ctx['setup']) if repoCls else None
        return

    __collectEM.addListener((BATTLE_REPO, guiType), onCollect)


def collectBattleControllerRepo(guiType, setup):
    ctx = __collectEM.handleEvent((BATTLE_REPO, guiType), ctx={'setup': setup})
    return (ctx.get('repo'), 'repo' in ctx)


def registerSharedControllerRepo(guiType, repoCls):

    def onCollect(ctx):
        ctx['repo'] = repoCls.create(ctx['setup']) if repoCls else None
        return

    __collectEM.addListener((SHARED_REPO, guiType), onCollect)


def collectSharedControllerRepo(guiType, setup):
    ctx = __collectEM.handleEvent((SHARED_REPO, guiType), ctx={'setup': setup})
    return (ctx.get('repo'), 'repo' in ctx)


def registerQueueEntity(queueType, queueCls):

    def onCollect(ctx):
        ctx['queue'] = queueCls()

    __collectEM.addListener((QUEUE, queueType), onCollect)


def collectQueueEntity(queueType):
    return __collectEM.handleEvent((QUEUE, queueType), ctx={}).get('queue')


def registerEntryPoint(actionName, entryPointCls):

    def onCollect(ctx):
        ctx['entry'] = entryPointCls()

    __collectEM.addListener((QUEUE_ENTRY_POINT, actionName), onCollect)


def collectEntryPoint(queueType):
    return __collectEM.handleEvent((QUEUE_ENTRY_POINT, queueType), ctx={}).get('entry')


def registerUnitEntity(pbrType, entityCls):

    def onCollect(ctx):
        ctx['entity'] = entityCls()

    __collectEM.addListener((UNIT_ENTITY, pbrType), onCollect)


def collectUnitEntity(pbrType):
    return __collectEM.handleEvent((UNIT_ENTITY, pbrType), ctx={}).get('entity')


def registerUnitEntryPoint(actionName, entryPointCls):

    def onCollect(ctx):
        ctx['entry'] = entryPointCls()

    __collectEM.addListener((UNIT_ENTRY_POINT, actionName), onCollect)


def collectUnitEntryPoint(queueType):
    return __collectEM.handleEvent((UNIT_ENTRY_POINT, queueType), ctx={}).get('entry')


def registerUnitEntryPointByType(pbrType, entryPointCls):

    def onCollect(ctx):
        ctx['entry'] = entryPointCls()

    __collectEM.addListener((UNIT_ENTRY_POINT_BY_TYPE, pbrType), onCollect)


def collectUnitEntryPointByType(pbrType):
    return __collectEM.handleEvent((UNIT_ENTRY_POINT_BY_TYPE, pbrType), ctx={}).get('entry')


def registerLegacyEntity(pbrType, entityCls):

    def onCollect(ctx):
        ctx['entity'] = entityCls

    __collectEM.addListener((UNIT_ENTITY, pbrType), onCollect)


def collectLegacyEntity(pbrType):
    return __collectEM.handleEvent((UNIT_ENTITY, pbrType), ctx={}).get('entity')


def registerLegacyEntryPoint(actionName, entryPointCls):

    def onCollect(ctx):
        ctx['entry'] = entryPointCls()

    __collectEM.addListener((UNIT_ENTRY_POINT, actionName), onCollect)


def collectLegacyEntryPoint(queueType):
    return __collectEM.handleEvent((UNIT_ENTRY_POINT, queueType), ctx={}).get('entry')


def registerLegacyEntryPointByType(pbrType, entryPointCls):

    def onCollect(ctx):
        ctx['entry'] = entryPointCls()

    __collectEM.addListener((UNIT_ENTRY_POINT_BY_TYPE, pbrType), onCollect)


def collectLegacyEntryPointByType(pbrType):
    return __collectEM.handleEvent((UNIT_ENTRY_POINT_BY_TYPE, pbrType), ctx={}).get('entry')


def registerPrbStorage(name, storage):

    def onCollect(ctx):
        ctx['storage'] = storage

    __collectEM.addListener((PBR_STORAGE, name), onCollect)


def collectPrbStorage(name):
    return __collectEM.handleEvent((PBR_STORAGE, name), ctx={}).get('storage')


def collectAllStorages():
    storages = []
    for eventID, handlers in __collectEM.handlers.iteritems():
        if isinstance(eventID, tuple) and eventID[0] == PBR_STORAGE:
            for handler in handlers:
                ctx = {}
                handler(ctx)
                storages.append(ctx['storage'])

    return storages


def registerArenaDescrs(guiType, arenaDescrClass):

    def onCollect(ctx):
        ctx['arena_descr_class'] = arenaDescrClass

    __collectEM.addListener((ARENA_DESCRIPTION, guiType), onCollect)


def collectArenaDescrs(guiType):
    return __collectEM.handleEvent((ARENA_DESCRIPTION, guiType), ctx={}).get('arena_descr_class')


def registerSquadFinder(guiType, squadFinderClass, rosterClass):

    def onCollect(ctx):
        ctx['squad_finder_data'] = (squadFinderClass, rosterClass)

    __collectEM.addListener((ARENA_SQUAD_FINDER, guiType), onCollect)


def collectSquadFinder(guiType):
    return __collectEM.handleEvent((ARENA_SQUAD_FINDER, guiType), ctx={}).get('squad_finder_data', (None, None))


def registerNotificationsListeners(listenerClasses):

    def onCollect(ctx):
        ctx['listeners'].extend((listenerCls() for listenerCls in listenerClasses))

    __collectEM.addListener(NOTIFICATIONS_LISTENERS, onCollect)


def collectAllNotificationsListeners():
    ctx = {'listeners': []}
    for handler in __collectEM.handlers[NOTIFICATIONS_LISTENERS]:
        handler(ctx)

    return ctx['listeners']


def registerNotificationsActionsHandlers(handlersClasses):

    def onCollect(ctx):
        ctx['handlers'].extend(handlersClasses)

    __collectEM.addListener(NOTIFICATIONS_ACTIONS_HANDLERS, onCollect)


def collectAllNotificationsActionsHandlers():
    ctx = {'handlers': []}
    for handler in __collectEM.handlers[NOTIFICATIONS_ACTIONS_HANDLERS]:
        handler(ctx)

    return ctx['handlers']


def registerMessengerClientFormatter(msgType, formatter):

    def onCollect(ctx):
        ctx['formatter'] = formatter

    __collectEM.addListener((MESSENGER_CLIENT_FORMATTERS, msgType), onCollect)


def collectMessengerClientFormatter(msgType):
    return __collectEM.handleEvent((MESSENGER_CLIENT_FORMATTERS, msgType), ctx={}).get('formatter')


def registerMessengerServerFormatter(msgType, formatter):

    def onCollect(ctx):
        ctx['formatter'] = formatter

    __collectEM.addListener((MESSENGER_SERVER_FORMATTERS, msgType), onCollect)


def collectMessengerServerFormatter(msgType):
    return __collectEM.handleEvent((MESSENGER_SERVER_FORMATTERS, msgType), ctx={}).get('formatter')


def registerTokenQuestsSubFormatter(formatter):

    def onCollect(ctx):
        ctx['formatters'].append(formatter)

    __collectEM.addListener(TOKEN_QUEST_SUBFORMATTERS, onCollect)


def registerTokenQuestsSubFormatters(formatters):

    def onCollect(ctx):
        ctx['formatters'].extend(formatters)

    __collectEM.addListener(TOKEN_QUEST_SUBFORMATTERS, onCollect)


def collectTokenQuestsSubFormatters():
    return __collectEM.handleEvent(TOKEN_QUEST_SUBFORMATTERS, ctx={'formatters': []}).get('formatters')


def registerLootBoxAutoOpenSubFormatter(formatter):

    def onCollect(ctx):
        ctx['formatters'].append(formatter)

    __collectEM.addListener(LOOTBOX_AUTOOPEN_SUBFORMATTERS, onCollect)


def registerLootBoxAutoOpenSubFormatters(formatters):

    def onCollect(ctx):
        ctx['formatters'].extend(formatters)

    __collectEM.addListener(LOOTBOX_AUTOOPEN_SUBFORMATTERS, onCollect)


def collectLootBoxAutoOpenSubFormatters():
    return __collectEM.handleEvent(LOOTBOX_AUTOOPEN_SUBFORMATTERS, ctx={'formatters': []}).get('formatters')


def registerPrbInviteHtmlFormatter(prbType, formatterCls):

    def onCollect(ctx):
        ctx['formatter'] = formatterCls()

    __collectEM.addListener((PRB_INVITE_HTML_FORMATTER, prbType), onCollect)


def registerPrbInvitesHtmlFormatter(prbTypes, formatterCls):
    for prbType in prbTypes:
        registerPrbInviteHtmlFormatter(prbType, formatterCls)


def collectPrbInviteHtmlFormatter(prbType):
    return __collectEM.handleEvent((PRB_INVITE_HTML_FORMATTER, prbType), ctx={}).get('formatter')


def registerModeNameKwargsGetterByPrb(prbType, prbModeNameKwargsKwargsGetter):

    def onCollect(ctx):
        ctx['prbModeNameKwargsGetter'] = prbModeNameKwargsKwargsGetter

    __collectEM.addListener((PRB_MODE_NAME_KWARGS, prbType), onCollect)


def collectModeNameKwargsByPrbType(prbType):
    getter = __collectEM.handleEvent((PRB_MODE_NAME_KWARGS, prbType), ctx={}).get('prbModeNameKwargsGetter')
    return getter() if getter is not None else {}


def registerModeNameKwargsGetterByQueue(queueType, queueModeNameKwargsKwargsGetter):

    def onCollect(ctx):
        ctx['queueModeNameKwargsGetter'] = queueModeNameKwargsKwargsGetter

    __collectEM.addListener((QUEUE_MODE_NAME_KWARGS, queueType), onCollect)


def collectModeNameKwargsByQueueType(queueType):
    getter = __collectEM.handleEvent((QUEUE_MODE_NAME_KWARGS, queueType), ctx={}).get('queueModeNameKwargsGetter')
    return getter() if getter is not None else {}


def registerModeNameKwargsGetterByBonusType(bonusType, prbModeNameKwargsKwargsGetter):

    def onCollect(ctx):
        ctx['bonusModeNameKwargsGetter'] = prbModeNameKwargsKwargsGetter

    __collectEM.addListener((BONUS_TYPE_MODE_NAME_KWARGS, bonusType), onCollect)


def collectModeNameKwargsByBonusType(bonusType):
    getter = __collectEM.handleEvent((BONUS_TYPE_MODE_NAME_KWARGS, bonusType), ctx={}).get('bonusModeNameKwargsGetter')
    return getter() if getter is not None else {}


def registerPrebattleConditionIconGetter(bonusType, prebattleConditionIconGetter):

    def onCollect(ctx):
        ctx['prbConditionIconGetter'] = prebattleConditionIconGetter

    __collectEM.addListener((PRB_CONDITION_ICON, bonusType), onCollect)


def collectPrebattleConditionIcon(bonusType):
    getter = __collectEM.handleEvent((PRB_CONDITION_ICON, bonusType), ctx={}).get('prbConditionIconGetter')
    return getter() if getter is not None else None


def registerModeSelectorItem(prbActionName, itemCls):

    def onCollect(ctx):
        ctx['item'] = itemCls

    __collectEM.addListener((MODE_SELECTOR_ITEM, prbActionName), onCollect)


def collectModeSelectorItem(prbActionName):
    return __collectEM.handleEvent((MODE_SELECTOR_ITEM, prbActionName), ctx={}).get('item')


def registerModeSelectorTooltips(simpleTooltipIds, contentTooltipsMap):

    def onCollect(ctx):
        ctx['modeSelectorTooltips']['simpleTooltipIds'].extend(simpleTooltipIds)
        ctx['modeSelectorTooltips']['contentTooltipsMap'].update(contentTooltipsMap)

    __collectEM.addListener(MODE_SELECTOR_TOOLTIP, onCollect)


def collectModeSelectorTooltips():
    return __collectEM.handleEvent(MODE_SELECTOR_TOOLTIP, ctx={'modeSelectorTooltips': {'simpleTooltipIds': [],
                              'contentTooltipsMap': {}}}).get('modeSelectorTooltips')


def registerBannerEntryPointValidator(alias, validator):

    def onCollect(ctx):
        ctx['validator'] = validator

    __collectEM.addListener((BANNER_ENTRY_POINT_VALIDATOR, alias), onCollect)


def collectBannerEntryPointValidator(alias):
    return __collectEM.handleEvent((BANNER_ENTRY_POINT_VALIDATOR, alias), ctx={}).get('validator')


def registerBannerEntryPointLUIRule(alias, ruleID):

    def onCollect(ctx):
        ctx['ruleID'] = ruleID

    __collectEM.addListener((BANNER_ENTRY_POINT_LUI_RULE, alias), onCollect)


def collectBannerEntryPointLUIRule(alias):
    return __collectEM.handleEvent((BANNER_ENTRY_POINT_LUI_RULE, alias), ctx={}).get('ruleID')


def registerCarouselEventEntryPoint(viewID, viewClass):

    def onCollect(ctx):
        ctx['carouselEventEntries'][viewID] = viewClass

    __collectEM.addListener(CAROUSEL_EVENTS_ENTRIES, onCollect)


def collectCarouselEventEntryPoints():
    return __collectEM.handleEvent(CAROUSEL_EVENTS_ENTRIES, {'carouselEventEntries': {}})['carouselEventEntries']


def registerBattleQueueProvider(queueType, providerCls):

    def onCollect(ctx):
        ctx['providerCls'] = providerCls

    __collectEM.addListener((BATTLE_QUEUE_PROVIDER, queueType), onCollect)


def collectBattleQueueProvider(queueType):
    return __collectEM.handleEvent((BATTLE_QUEUE_PROVIDER, queueType), ctx={}).get('providerCls')


def registerBattleTipCriteria(guiType, criteriaCls):

    def onCollect(ctx):
        ctx['criteriaCls'] = criteriaCls

    __collectEM.addListener((BATTLE_TIPS_CRITERIA, guiType), onCollect)


def registerBattleTipsCriteria(guiTypes, criteriaCls):
    for guiType in guiTypes:
        registerBattleTipCriteria(guiType, criteriaCls)


def collectBattleTipsCriteria(guiType):
    return __collectEM.handleEvent((BATTLE_TIPS_CRITERIA, guiType), ctx={}).get('criteriaCls')


def registerIngameHelpPagesBuilder(builder):

    def onCollect(ctx):
        ctx['builders'].append(builder)

    __collectEM.addListener(INGAME_HELP_PAGES_BUILDERS, onCollect)


def registerIngameHelpPagesBuilders(builders):

    def onCollect(ctx):
        ctx['builders'].extend(builders)

    __collectEM.addListener(INGAME_HELP_PAGES_BUILDERS, onCollect)


def collectIngameHelpPagesBuilders():
    return __collectEM.handleEvent(INGAME_HELP_PAGES_BUILDERS, {'builders': []})['builders']


def registerQuestBuilder(questBuilder):

    def onCollect(ctx):
        ctx['questBuilders'].append(questBuilder)

    __collectEM.addListener(QUEST_BUILDERS, onCollect)


def registerQuestBuilders(questBuilders):

    def onCollect(ctx):
        ctx['questBuilders'].extend(questBuilders)

    __collectEM.addListener(QUEST_BUILDERS, onCollect)


def collectQuestBuilders():
    return __collectEM.handleEvent(QUEST_BUILDERS, {'questBuilders': []})['questBuilders']


def registerAwardControllerHandler(handler):

    def onCollect(ctx):
        ctx['handlers'].append(handler)

    __collectEM.addListener(AWARD_CONTROLLER_HANDLERS, onCollect)


def registerAwardControllerHandlers(handlers):

    def onCollect(ctx):
        ctx['handlers'].extend(handlers)

    __collectEM.addListener(AWARD_CONTROLLER_HANDLERS, onCollect)


def collectAwardControllerHandlers():
    return __collectEM.handleEvent(AWARD_CONTROLLER_HANDLERS, {'handlers': []})['handlers']


def registerCanSelectPrbEntity(queueType, itemFun):

    def onCollect(ctx):
        ctx['itemFun'] = itemFun

    __collectEM.addListener((CAN_SELECT_PRB_ENTITY, queueType), onCollect)


def collectCanSelectPrbEntity(queueType):
    return __collectEM.handleEvent((CAN_SELECT_PRB_ENTITY, queueType), ctx={}).get('itemFun', lambda *args, **kwargs: False)


def registerBattleResultStatsCtrl(bonusType, itemCls):

    def onCollect(ctx):
        ctx['item'] = itemCls

    __collectEM.addListener((BATTLE_RESULT_STATS_CONTROLLER, bonusType), onCollect)


def collectBattleResultStatsCtrl(bonusType):
    return __collectEM.handleEvent((BATTLE_RESULT_STATS_CONTROLLER, bonusType), ctx={}).get('item', None)


def registerSeasonProviderHandler(seasonType, seasonControllerHandler):

    def onCollect(ctx):
        ctx[seasonType] = seasonControllerHandler

    __collectEM.addListener((SEASON_PROVIDER_HANDLER, seasonType), onCollect)


def collectSeasonProviderHandler(seasonType):
    return __collectEM.handleEvent((SEASON_PROVIDER_HANDLER, seasonType), ctx={}).get(seasonType, None)


def registerLimitedUIToken(tokenInfo):

    def onCollect(ctx):
        ctx['tokens'].append(tokenInfo)

    __collectEM.addListener(LIMITED_UI_TOKENS, onCollect)


def registerLimitedUITokens(tokensInfos):

    def onCollect(ctx):
        ctx['tokens'].extend(tokensInfos)

    __collectEM.addListener(LIMITED_UI_TOKENS, onCollect)


def collectLimitedUITokens():
    return __collectEM.handleEvent(LIMITED_UI_TOKENS, ctx={'tokens': []})['tokens']


def registerHangarPresetGetter(queueType, processor):

    def onCollect(ctx):
        ctx['presetsGetters'][queueType] = processor(ctx['config'])

    __collectEM.addListener(HANGAR_PRESETS_PROCESSORS, onCollect)


def collectHangarPresetsGetters(config):
    return __collectEM.handleEvent(HANGAR_PRESETS_PROCESSORS, {'presetsGetters': {},
     'config': config})['presetsGetters']


def registerHangarPresetsReader(reader):

    def onCollect(ctx):
        ctx['presetsReaders'].append(reader)

    __collectEM.addListener(HANGAR_PRESETS_READERS, onCollect)


def collectHangarPresetsReaders():
    return __collectEM.handleEvent(HANGAR_PRESETS_READERS, ctx={'presetsReaders': []})['presetsReaders']


def registerAmmunitionPanelView(viewCls):

    def onCollect(ctx):
        ctx[viewCls.__name__] = viewCls

    __collectEM.addListener((AMMUNITION_PANEL_VIEW, viewCls.__name__), onCollect)


def collectAmmunitionPanelView(viewAlias):
    return __collectEM.handleEvent((AMMUNITION_PANEL_VIEW, viewAlias), ctx={}).get(viewAlias, None)


def registerVehicleViewState(viewState):

    def onCollect(ctx):
        ctx['viewStates'].append(viewState)

    __collectEM.addListener(VEHICLE_VIEW_STATE, onCollect)


def collectVehicleViewStates():
    return __collectEM.handleEvent(VEHICLE_VIEW_STATE, ctx={'viewStates': []})['viewStates']


def registerDynObjCache(arenaGuiType, dynCache):

    def onCollect(ctx):
        ctx['dynCache'] = dynCache

    __collectEM.addListener((DYN_OBJ_CACHE, arenaGuiType), onCollect)


def collectDynObjCache(arenaGuiType):
    return __collectEM.handleEvent((DYN_OBJ_CACHE, arenaGuiType), ctx={}).get('dynCache')


def registerLobbyContexMenuHandler(optionID, commandHandler):

    def onCollect(ctx):
        ctx[optionID] = commandHandler

    __collectEM.addListener((CONTEXT_MENU_COMMANDS, optionID), onCollect)


def collectLobbyContexMenuHandler(optionID):
    return __collectEM.handleEvent((CONTEXT_MENU_COMMANDS, optionID), ctx={}).get(optionID, None)


def registerLobbyContexMenuOptionBuilder(optionBuilder):

    def onCollect(ctx):
        ctx['cmOptionBuilders'].append(optionBuilder)

    __collectEM.addListener(CONTEXT_MENU_OPTION_BUILDER, onCollect)


def collectLobbyContexMenuOptionBuilders():
    return __collectEM.handleEvent(CONTEXT_MENU_OPTION_BUILDER, {'cmOptionBuilders': []})['cmOptionBuilders']


def registerAdvancedChatComponent(bonusType, component):

    def onCollect(ctx):
        ctx[bonusType] = component

    __collectEM.addListener((ADVANCED_CHAT_COMPONENT, bonusType), onCollect)


def collectAdvancedChatComponent(bonusType):
    return __collectEM.handleEvent((ADVANCED_CHAT_COMPONENT, bonusType), ctx={}).get(bonusType, None)


def registerBattleChanelController(guiType, battleChanelType, controller):

    def onCollect(ctx):
        ctx[guiType] = controller

    __collectEM.addListener((BATTLE_CHANEL_CONTROLLER, battleChanelType), onCollect)


def collectBattleChanelController(battleChanelType, guiType):
    return __collectEM.handleEvent((BATTLE_CHANEL_CONTROLLER, battleChanelType), ctx={}).get(guiType, None)


def registerHitDirectionController(guiType, hitDirectionType, hitDirectionPlayerType):

    def onCollect(ctx):
        ctx[guiType] = (hitDirectionType, hitDirectionPlayerType)

    __collectEM.addListener((HIT_DIRECTION_CONTROLLER, guiType), onCollect)


def collectHitDirectionController(guiType, defaultHitDirectionType, defaultHitDirectionPlayerType):
    defaultValue = (defaultHitDirectionType, defaultHitDirectionPlayerType)
    return __collectEM.handleEvent((HIT_DIRECTION_CONTROLLER, guiType), ctx={}).get(guiType, defaultValue)


def registerCustomizationHangarDecorator(handler):

    def onCollect(ctx):
        ctx['handlers'].append(handler)

    __collectEM.addListener(CUSTOMIZATION_HANGAR_AVAILABLE, onCollect)


def collectCustomizationHangarDecorator():
    return __collectEM.handleEvent(CUSTOMIZATION_HANGAR_AVAILABLE, {'handlers': []})['handlers']


def registerOptimizedViews(optimizedViewsSettings):

    def onCollect(ctx):
        ctx['optimizedViewsSettings'].update(optimizedViewsSettings)

    __collectEM.addListener(OPTIMIZED_VIEWS, onCollect)


def collectOptimizedViews():
    return __collectEM.handleEvent(OPTIMIZED_VIEWS, ctx={'optimizedViewsSettings': {}})['optimizedViewsSettings']


def registerReplayModeTag(guiType, replayModeTag):

    def onCollect(ctx):
        ctx['replayModeTag'] = replayModeTag

    __collectEM.addListener((REPLAY_MODE_TAG, guiType), onCollect)


def collectReplayModeTag(guiType):
    return __collectEM.handleEvent((REPLAY_MODE_TAG, guiType), ctx={}).get('replayModeTag', '')


def registerQuestFlag(questFlagType, flagCls):

    def onCollect(ctx):
        ctx['questFlags'][questFlagType] = flagCls

    __collectEM.addListener(QUEST_FLAGS, onCollect)


def collectQuestFlags():
    return __collectEM.handleEvent(QUEST_FLAGS, {'questFlags': {}})['questFlags']


def registerBattleResultsStatsSorting(bonusType, sortingKey):

    def onCollect(ctx):
        ctx['sortingKey'][bonusType] = sortingKey

    __collectEM.addListener(BATTLE_RESULTS_STATS_SORTING, onCollect)


def collectBattleResultsStatsSorting():
    return __collectEM.handleEvent(BATTLE_RESULTS_STATS_SORTING, {'sortingKey': {}})['sortingKey']
