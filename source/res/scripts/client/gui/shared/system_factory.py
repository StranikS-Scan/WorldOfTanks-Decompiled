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
MOD_SELECTOR_ITEM = 19
ENTRY_POINT_VALIDATOR = 20

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
     'isReplay': isReplay}).get('item')


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


def registerPrbInviteHtmlFormatter(prbType, formatterCls):

    def onCollect(ctx):
        ctx['formatter'] = formatterCls()

    __collectEM.addListener((PRB_INVITE_HTML_FORMATTER, prbType), onCollect)


def registerPrbInvitesHtmlFormatter(prbTypes, formatterCls):
    for prbType in prbTypes:
        registerPrbInviteHtmlFormatter(prbType, formatterCls)


def collectPrbInviteHtmlFormatter(prbType):
    return __collectEM.handleEvent((PRB_INVITE_HTML_FORMATTER, prbType), ctx={}).get('formatter')


def registerModSelectorItem(prbActionName, itemCls):

    def onCollect(ctx):
        ctx['item'] = itemCls

    __collectEM.addListener((MOD_SELECTOR_ITEM, prbActionName), onCollect)


def collectModSelectorItem(prbActionName):
    return __collectEM.handleEvent((MOD_SELECTOR_ITEM, prbActionName), ctx={}).get('item')


def registerEntryPointValidator(alias, validator):

    def onCollect(ctx):
        ctx['validator'] = validator

    __collectEM.addListener((ENTRY_POINT_VALIDATOR, alias), onCollect)


def collectEntryPointValidator(alias):
    return __collectEM.handleEvent((ENTRY_POINT_VALIDATOR, alias), ctx={}).get('validator')
