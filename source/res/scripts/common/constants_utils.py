# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/constants_utils.py
import types
from UnitBase import CMD_NAMES, ROSTER_TYPE, PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER, PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER_EXT, ROSTER_TYPE_TO_CLASS, UNIT_MGR_FLAGS_TO_PREBATTLE_TYPE, UNIT_MGR_FLAGS_TO_UNIT_MGR_ENTITY_NAME, UNIT_MGR_FLAGS_TO_INVITATION_TYPE, UNIT_MGR_FLAGS_TO_QUEUE_TYPE, QUEUE_TYPE_BY_UNIT_MGR_ROSTER, UNIT_ERROR, VEHICLE_TAGS_GROUP_BY_UNIT_MGR_FLAGS
from chat_shared import SYS_MESSAGE_TYPE
from constants import ARENA_GUI_TYPE, ARENA_GUI_TYPE_LABEL, ARENA_BONUS_TYPE, ARENA_BONUS_TYPE_NAMES, ARENA_BONUS_TYPE_IDS, ARENA_BONUS_MASK, QUEUE_TYPE, QUEUE_TYPE_NAMES, PREBATTLE_TYPE, PREBATTLE_TYPE_NAMES, INVITATION_TYPE, BATTLE_MODE_VEHICLE_TAGS, SEASON_TYPE_BY_NAME, SEASON_NAME_BY_TYPE, QUEUE_TYPE_IDS
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from debug_utils import LOG_DEBUG
from soft_exception import SoftException

class ConstInjectorMeta(type):

    def __new__(mcs, clsname, bases, attrs):
        attrs['_extra_attrs'] = tuple((attr for attr in attrs if attr[0] != '_'))
        return super(ConstInjectorMeta, mcs).__new__(mcs, clsname, bases, attrs)


class ConstInjector(object):
    __metaclass__ = ConstInjectorMeta
    _extra_attrs = ()
    _const_type = (int, long)

    @classmethod
    def inject(cls, personality=None):
        origin = cls.__bases__[0]
        originValues = {originValue for originAttr, originValue in origin.__dict__.iteritems() if originAttr[0] != '_' and cls._isEligible(originValue)}
        for attr in cls._extra_attrs:
            value = getattr(cls, attr)
            msg = "{cls}: origin {origin} already has attr '{attr}' with value '{value}'"
            if hasattr(origin, attr) and cls._isEligible(value):
                raise SoftException(msg.format(cls=cls, origin=origin, attr=attr, value=getattr(origin, attr)))
            if value in originValues:
                raise SoftException(msg.format(cls=cls, origin=origin, attr=attr, value=value))
            setattr(origin, attr, value)

        LOG_DEBUG('{extraAttrs} was injected to {origin}. Personality: {personality}'.format(extraAttrs=cls.getExtraAttrs(), origin=origin, personality=personality))

    @classmethod
    def getExtraAttrs(cls):
        return {attr:getattr(cls, attr) for attr in cls._extra_attrs if cls._isEligible(getattr(cls, attr))}

    @classmethod
    def _isEligible(cls, value):
        return isinstance(value, cls._const_type)


def addArenaGuiTypesFromExtension(extArenaGuiType, personality):
    extraAttrs = extArenaGuiType.getExtraAttrs()
    extraValues = tuple(extraAttrs.itervalues())
    extArenaGuiType.inject(personality)
    ARENA_GUI_TYPE.RANGE += extraValues
    ARENA_GUI_TYPE.VOIP_SUPPORTED += extraValues
    ARENA_GUI_TYPE.BATTLE_CHAT_SETTING_SUPPORTED += extraValues
    ARENA_GUI_TYPE_LABEL.LABELS.update({value:attr.lower() for attr, value in extraAttrs.iteritems()})


def addArenaBonusTypesFromExtension(extArenaBonusType, personality):
    extraAttrs = extArenaBonusType.getExtraAttrs()
    extraValues = tuple(extraAttrs.itervalues())
    extArenaBonusType.inject(personality)
    ARENA_BONUS_TYPE.RANGE += extraValues
    ARENA_BONUS_TYPE_NAMES.update(extraAttrs)
    ARENA_BONUS_TYPE_IDS.update({value:attr for attr, value in extraAttrs.iteritems()})
    ARENA_BONUS_MASK.reInit()


def addQueueTypesFromExtension(extQueueType, personality):
    extraAttrs = extQueueType.getExtraAttrs()
    extraValues = tuple(extraAttrs.itervalues())
    extQueueType.inject(personality)
    QUEUE_TYPE.ALL += extraValues
    QUEUE_TYPE_NAMES.update({value:attr for attr, value in extraAttrs.iteritems()})
    QUEUE_TYPE_IDS.update({attr.lower():value for attr, value in extraAttrs.iteritems()})
    QUEUE_TYPE.BASE_ON_DEQUEUE += extraValues


def addPrebattleTypesFromExtension(extPrebattleType, personality):
    extraAttrs = extPrebattleType.getExtraAttrs()
    extraValues = tuple(extraAttrs.itervalues())
    extPrebattleType.inject(personality)
    PREBATTLE_TYPE.RANGE += extraValues
    PREBATTLE_TYPE.SQUAD_PREBATTLES += extraValues
    PREBATTLE_TYPE.UNIT_MGR_PREBATTLES += extraValues
    PREBATTLE_TYPE.CREATE_FROM_CLIENT += extraValues
    PREBATTLE_TYPE.CREATE_EX_FROM_SERVER += extraValues
    PREBATTLE_TYPE.JOIN_EX += extraValues
    PREBATTLE_TYPE_NAMES.update({value:attr for attr, value in extraAttrs.iteritems()})


def addBattleEventTypesFromExtension(extBattleEventType, personality):
    extraAttrs = extBattleEventType.getExtraAttrs()
    extBattleEventType.inject(personality)
    BATTLE_EVENT_TYPE.ALL |= frozenset(extraAttrs.itervalues())


def addRosterTypes(extRosterType, personality):
    extraAttrs = extRosterType.getExtraAttrs()
    extRosterType.inject(personality)
    for value in extraAttrs.itervalues():
        ROSTER_TYPE._MASK |= value


def addInvitationTypes(extInvitationType, personality):
    extraAttrs = extInvitationType.getExtraAttrs()
    extInvitationType.inject(personality)
    INVITATION_TYPE.RANGE += tuple(extraAttrs.itervalues())


def addClientUnitCmd(extClientUnitCmd, personality):
    extraAttrs = extClientUnitCmd.getExtraAttrs()
    extClientUnitCmd.inject(personality)
    CMD_NAMES.update({value:attr for attr, value in extraAttrs.iteritems()})


def addPrbTypeByUnitMgrRoster(prbType, unitMgrFlag, personality):
    if prbType in PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER:
        raise SoftException('PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER already has prbType:{prbType}. Personality: {p}'.format(prbType=prbType, p=personality))
    PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER.update({prbType: unitMgrFlag})
    msg = 'prbType:{prbType} was added to PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER. Personality: {p}'.format(prbType=prbType, p=personality)
    LOG_DEBUG(msg)


def addQueueTypeByUnitMgrRoster(queueType, rosterType, personality):
    if queueType in QUEUE_TYPE_BY_UNIT_MGR_ROSTER:
        raise SoftException('QUEUE_TYPE_BY_UNIT_MGR_ROSTER already has queueType:{queueType}. Personality: {p}'.format(queueType=queueType, p=personality))
    QUEUE_TYPE_BY_UNIT_MGR_ROSTER.update({queueType: rosterType})
    msg = 'queueType:{queueType} was added to QUEUE_TYPE_BY_UNIT_MGR_ROSTER. Personality: {p}'.format(queueType=queueType, p=personality)
    LOG_DEBUG(msg)


def addPrbTypeByUnitMgrRosterExt(prbType, unitMgrFlag, personality):
    if prbType in PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER_EXT:
        raise SoftException('PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER_EXT already has prbType:{prbType}. Personality: {p}'.format(prbType=prbType, p=personality))
    PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER_EXT.update({prbType: unitMgrFlag})
    msg = 'prbType:{prbType} was added to PREBATTLE_TYPE_BY_UNIT_MGR_ROSTER_EXT. Personality: {p}'.format(prbType=prbType, p=personality)
    LOG_DEBUG(msg)


def addRosterTypeToClass(rosterType, rosterClass, personality):
    if rosterType in ROSTER_TYPE_TO_CLASS:
        raise SoftException('ROSTER_TYPE_TO_CLASS already has rosterType:{rosterType}. Personality: {p}'.format(rosterType=rosterType, p=personality))
    ROSTER_TYPE_TO_CLASS.update({rosterType: rosterClass})
    msg = 'rosterType:{rosterType} was added to ROSTER_TYPE_TO_CLASS. Personality: {p}'.format(rosterType=rosterType, p=personality)
    LOG_DEBUG(msg)


def addUnitMgrFlagToPrbType(prbType, unitMgrFlag, personality):
    if unitMgrFlag in UNIT_MGR_FLAGS_TO_PREBATTLE_TYPE:
        raise SoftException('UNIT_MGR_FLAGS_TO_PREBATTLE_TYPE already has unitMgrFlag:{unitMgrFlag}. Personality: {p}'.format(unitMgrFlag=unitMgrFlag, p=personality))
    UNIT_MGR_FLAGS_TO_PREBATTLE_TYPE.update({unitMgrFlag: prbType})
    msg = 'unitMgrFlag:{unitMgrFlag} was added to UNIT_MGR_FLAGS_TO_PREBATTLE_TYPE. Personality: {p}'.format(unitMgrFlag=unitMgrFlag, p=personality)
    LOG_DEBUG(msg)


def addUnitMgrFlagsToUnitMgrEntityName(unitMgrFlag, entityName, personality):
    if unitMgrFlag in UNIT_MGR_FLAGS_TO_UNIT_MGR_ENTITY_NAME:
        raise SoftException('UNIT_MGR_FLAGS_TO_UNIT_MGR_ENTITY_NAME already has unitMgrFlag:{unitMgrFlag}. Personality: {p}'.format(unitMgrFlag=unitMgrFlag, p=personality))
    UNIT_MGR_FLAGS_TO_UNIT_MGR_ENTITY_NAME.update({unitMgrFlag: entityName})
    msg = 'unitMgrFlag:{flag}->{name} was added to UNIT_MGR_FLAGS_TO_UNIT_MGR_ENTITY_NAME. Personality: {p}'.format(flag=unitMgrFlag, name=entityName, p=personality)
    LOG_DEBUG(msg)


def addUnitMgrFlagToInvitationType(unitMgrFlag, invType, personality):
    if unitMgrFlag in UNIT_MGR_FLAGS_TO_INVITATION_TYPE:
        raise SoftException('UNIT_MGR_FLAGS_TO_INVITATION_TYPE already has unitMgrFlag:{unitMgrFlag}. Personality: {p}'.format(unitMgrFlag=unitMgrFlag, p=personality))
    UNIT_MGR_FLAGS_TO_INVITATION_TYPE.update({unitMgrFlag: invType})
    msg = 'unitMgrFlag:{flag}->{invType} was added to UNIT_MGR_FLAGS_TO_INVITATION_TYPE. Personality: {p}'.format(flag=unitMgrFlag, invType=invType, p=personality)
    LOG_DEBUG(msg)


def addUnitMgrFlagToQueueType(unitMgrFlag, queueType, personality):
    if unitMgrFlag in UNIT_MGR_FLAGS_TO_QUEUE_TYPE:
        raise SoftException('UNIT_MGR_FLAGS_TO_QUEUE_TYPE already has unitMgrFlag:{unitMgrFlag}. Personality: {p}'.format(unitMgrFlag=unitMgrFlag, p=personality))
    UNIT_MGR_FLAGS_TO_QUEUE_TYPE.update({unitMgrFlag: queueType})
    msg = 'unitMgrFlag:{flag}->{queueType} was added to UNIT_MGR_FLAGS_TO_QUEUE_TYPE. Personality: {p}'.format(flag=unitMgrFlag, queueType=queueType, p=personality)
    LOG_DEBUG(msg)


def addInvitationTypeFromArenaBonusTypeMapping(arenaBonusType, invitationType, personality):
    if arenaBonusType in INVITATION_TYPE.INVITATION_TYPE_FROM_ARENA_BONUS_TYPE_MAPPING:
        raise SoftException('INVITATION_TYPE_FROM_ARENA_BONUS_TYPE_MAPPING already has ARENA_BONUS_TYPE:{arenaBonusType}. Personality: {p}'.format(arenaBonusType=arenaBonusType, p=personality))
    INVITATION_TYPE.INVITATION_TYPE_FROM_ARENA_BONUS_TYPE_MAPPING.update({arenaBonusType: invitationType})
    msg = 'ARENA_BONUS_TYPE:{arenaBonusType} was added to INVITATION_TYPE_FROM_ARENA_BONUS_TYPE_MAPPING. Personality: {p}'.format(arenaBonusType=arenaBonusType, p=personality)
    LOG_DEBUG(msg)


def addVehicleTags(unitMgrFlag, requiredTags, forbiddenTags, newTags, personality):
    BATTLE_MODE_VEHICLE_TAGS.update(newTags)
    if unitMgrFlag in VEHICLE_TAGS_GROUP_BY_UNIT_MGR_FLAGS:
        raise SoftException('VEHICLE_TAGS_GROUP_BY_UNIT_MGR_FLAGS already has unitMgrFlag:{unitMgrFlag}. Personality: {p}'.format(unitMgrFlag=unitMgrFlag, p=personality))
    VEHICLE_TAGS_GROUP_BY_UNIT_MGR_FLAGS.update({unitMgrFlag: (requiredTags, forbiddenTags)})
    msg = 'unitMgrFlag:{unitMgrFlag} was added to VEHICLE_TAGS_GROUP_BY_UNIT_MGR_FLAGS. Personality: {p}'.format(unitMgrFlag=unitMgrFlag, p=personality)
    LOG_DEBUG(msg)


def initCommonTypes(extConstants, personality):
    addArenaGuiTypesFromExtension(extConstants.ARENA_GUI_TYPE, personality)
    addArenaBonusTypesFromExtension(extConstants.ARENA_BONUS_TYPE, personality)
    addQueueTypesFromExtension(extConstants.QUEUE_TYPE, personality)
    addPrebattleTypesFromExtension(extConstants.PREBATTLE_TYPE, personality)


def initSquadCommonTypes(extConstants, personality):
    extConstants.UNIT_MGR_FLAGS.inject(personality)
    addRosterTypes(extConstants.ROSTER_TYPE, personality)
    addInvitationTypes(extConstants.INVITATION_TYPE, personality)
    addClientUnitCmd(extConstants.CLIENT_UNIT_CMD, personality)


class AbstractBattleMode(object):
    _PREBATTLE_TYPE = None
    _QUEUE_TYPE = None
    _ARENA_BONUS_TYPE = None
    _ARENA_GUI_TYPE = None
    _BATTLE_MGR_NAME = None
    _UNIT_MGR_NAME = None
    _UNIT_MGR_FLAGS = None
    _ROSTER_TYPE = None
    _ROSTER_CLASS = None
    _GAME_PARAMS_KEY = None
    _REQUIRED_VEHICLE_TAGS = tuple()
    _FORBIDDEN_VEHICLE_TAGS = BATTLE_MODE_VEHICLE_TAGS
    _NEW_VEHICLES_TAGS = set()
    _BASE_CHAT_LOG_FLAGS = None
    _BASE_QUEUE_CONTROLLER_CLASS = None
    _INVITATION_TYPE = None
    _CLIENT_BATTLE_PAGE = None
    _CLIENT_PRB_ACTION_NAME = None
    _CLIENT_PRB_ACTION_NAME_SQUAD = None
    _CLIENT_BANNER_ENTRY_POINT_ALIAS = None
    _BATTLE_RESULTS_CONFIG = None
    _CLIENT_GAME_SEASON_TYPE = None
    _SEASON_TYPE_BY_NAME = None
    _SEASON_TYPE = None
    _SEASON_MANAGER_TYPE = None
    _SM_TYPE_BATTLE_RESULT = None
    _SM_TYPES = []

    def __init__(self, personality):
        self._personality = personality

    @property
    def _battleMgrConfig(self):
        return (self._BATTLE_MGR_NAME, 0.2, ('periphery', 'standalone'))

    @property
    def _client_prbEntityClass(self):
        return None

    @property
    def _client_canSelectPrbEntity(self):
        return lambda *args, **kwargs: True

    @property
    def _client_prbEntryPointClass(self):
        return None

    @property
    def _client_selectorColumn(self):
        return None

    @property
    def _client_selectorItemsCreator(self):
        return None

    @property
    def _client_modeSelectorItemsClass(self):
        return None

    @property
    def _client_bannerEntryPointValidatorMethod(self):
        return None

    @property
    def _client_prbSquadEntityClass(self):
        return None

    @property
    def _client_prbSquadEntryPointClass(self):
        return None

    @property
    def _client_selectorSquadItemsCreator(self):
        return None

    @property
    def _client_platoonViewClass(self):
        return None

    @property
    def _client_platoonWelcomeViewClass(self):
        return None

    @property
    def _client_platoonLayouts(self):
        return None

    @property
    def _client_gameControllers(self):
        return tuple()

    @property
    def _client_battleControllersRepository(self):
        return None

    @property
    def _client_providerBattleQueue(self):
        return None

    @property
    def _client_arenaDescrClass(self):
        return None

    @property
    def _client_squadFinderClass(self):
        return None

    @property
    def _client_battleResultsComposerClass(self):
        return None

    @property
    def _client_battleResultsReusables(self):
        return {}

    @property
    def _client_seasonControllerHandler(self):
        return lambda *args, **kwargs: None

    @property
    def _client_lobbyRequiredLibraries(self):
        return []

    @property
    def _client_battleRequiredLibraries(self):
        return []

    @property
    def _client_notificationActionHandlers(self):
        return []

    @property
    def _client_messengerClientFormatters(self):
        return {}

    @property
    def _client_messengerServerFormatters(self):
        return {}

    @property
    def _client_tokenQuestsSubFormatters(self):
        return []

    @property
    def _server_canCreateUnitMgr(self):
        return lambda *args, **kwargs: (UNIT_ERROR.OK, '')

    @property
    def _server_unitConnector(self):
        from unitmgr_helpers.connectors import SquadConnector
        return SquadConnector()

    @property
    def _server_unitChecker(self):
        return lambda *args, **kwargs: (True, '')

    @property
    def _server_invitationSquadExtraHandler(self):
        return None

    @property
    def _server_unitCmdHandlers(self):
        return []

    @property
    def _server_unitMethodRoles(self):
        return []

    def registerSquadTypes(self):
        addQueueTypeByUnitMgrRoster(self._QUEUE_TYPE, self._ROSTER_TYPE, self._personality)
        addUnitMgrFlagToQueueType(self._UNIT_MGR_FLAGS, self._QUEUE_TYPE, self._personality)
        addPrbTypeByUnitMgrRoster(self._PREBATTLE_TYPE, self._ROSTER_TYPE, self._personality)
        addPrbTypeByUnitMgrRosterExt(self._PREBATTLE_TYPE, self._ROSTER_TYPE, self._personality)
        addRosterTypeToClass(self._ROSTER_TYPE, self._ROSTER_CLASS, self._personality)
        addUnitMgrFlagToPrbType(self._PREBATTLE_TYPE, self._UNIT_MGR_FLAGS, self._personality)
        addUnitMgrFlagToInvitationType(self._UNIT_MGR_FLAGS, self._PREBATTLE_TYPE, self._personality)
        addInvitationTypeFromArenaBonusTypeMapping(self._ARENA_BONUS_TYPE, self._INVITATION_TYPE, self._personality)
        addUnitMgrFlagsToUnitMgrEntityName(self._UNIT_MGR_FLAGS, self._UNIT_MGR_NAME, self._personality)

    def registerBase(self):
        import server_constants_utils as scu
        scu.addQueueController(self._QUEUE_TYPE, self._BASE_QUEUE_CONTROLLER_CLASS, self._personality)
        scu.addBattleManagerNameByQueueType(self._QUEUE_TYPE, self._BATTLE_MGR_NAME, self._personality)
        scu.addSingletonsToStart(self._BATTLE_MGR_NAME, self._battleMgrConfig, self._personality)
        scu.addBattlesConfigToList(self._GAME_PARAMS_KEY, self._personality)
        scu.addPreBattleTypeToChatLogFlags(self._PREBATTLE_TYPE, self._BASE_CHAT_LOG_FLAGS, self._personality)

    def registerBaseUnit(self):
        import server_constants_utils as scu
        scu.addCanCreateUnitMgrHandler(self._ROSTER_TYPE, self._server_canCreateUnitMgr, self._personality)
        scu.addSquadConnector(self._UNIT_MGR_FLAGS, self._server_unitConnector, self._personality)
        scu.addUnitVehicleChecker(self._UNIT_MGR_FLAGS, self._server_unitChecker, self._personality)
        scu.addInvitationSquadExtraHandler(self._INVITATION_TYPE, self._server_invitationSquadExtraHandler, self._personality)
        if self._server_unitCmdHandlers:
            scu.addUnitCmdHandlers(self._server_unitCmdHandlers, self._personality)
        if self._server_unitMethodRoles:
            scu.addUnitMethodRoles(self._server_unitMethodRoles, self._personality)

    def registerClient(self):
        from gui.prb_control import prb_utils
        from gui.Scaleform.daapi.settings.views import addViewBattlePageAliasByArenaGUIType
        prb_utils.addArenaGUITypeByQueueType(self._QUEUE_TYPE, self._ARENA_GUI_TYPE, self._personality)
        prb_utils.addQueueTypeToPrbType(self._QUEUE_TYPE, self._PREBATTLE_TYPE, self._personality)
        prb_utils.addPrbTypeToQueueType(self._QUEUE_TYPE, self._PREBATTLE_TYPE, self._personality)
        prb_utils.addArenaDescrs(self._ARENA_GUI_TYPE, self._client_arenaDescrClass, self._personality)
        addViewBattlePageAliasByArenaGUIType(self._ARENA_GUI_TYPE, self._CLIENT_BATTLE_PAGE, self._personality)

    def registerClientSelector(self):
        from gui.prb_control import prb_utils
        prb_utils.addBattleItemToColumnSelector(self._CLIENT_PRB_ACTION_NAME, self._client_selectorColumn, self._personality)
        prb_utils.addBattleSelectorItem(self._CLIENT_PRB_ACTION_NAME, self._client_selectorItemsCreator, self._personality)
        prb_utils.addModeSelectorItem(self._CLIENT_PRB_ACTION_NAME, self._client_modeSelectorItemsClass, self._personality)
        prb_utils.addSupportedEntryByAction(self._CLIENT_PRB_ACTION_NAME, self._client_prbEntryPointClass, self._personality)
        prb_utils.addSupportedQueues(self._QUEUE_TYPE, self._client_prbEntityClass, self._client_canSelectPrbEntity, self._personality)

    def registerBannerEntryPointValidatorMethod(self):
        from gui.prb_control import prb_utils
        prb_utils.addBannerEntryPointValidatorMethod(self._CLIENT_BANNER_ENTRY_POINT_ALIAS, self._client_bannerEntryPointValidatorMethod, self._personality)

    def registerProviderBattleQueue(self):
        from gui.prb_control import prb_utils
        prb_utils.addProviderBattleQueueCls(self._QUEUE_TYPE, self._client_providerBattleQueue, self._personality)

    def registerClientPlatoon(self):
        from gui.impl.lobby.platoon import platoon_config
        platoon_config.addQueueTypeToPrbSquadActionName(self._QUEUE_TYPE, self._CLIENT_PRB_ACTION_NAME_SQUAD, self._personality)
        platoon_config.addPlatoonViewByPrbType(self._PREBATTLE_TYPE, self._client_platoonViewClass, self._personality)
        platoon_config.addPlatoonWelcomeViewByPrbType(self._PREBATTLE_TYPE, self._client_platoonWelcomeViewClass, self._personality)
        platoon_config.addPlatoonLayoutData(self._PREBATTLE_TYPE, self._client_platoonLayouts, self._personality)

    def registerClientSquadSelector(self):
        from gui.prb_control import prb_utils
        prb_utils.addSupportedUnitEntryByAction(self._CLIENT_PRB_ACTION_NAME_SQUAD, self._client_prbSquadEntryPointClass, self._personality)
        prb_utils.addSupportedUnitEntryByType(self._PREBATTLE_TYPE, self._client_prbSquadEntryPointClass, self._personality)
        prb_utils.addSupportedUnitByType(self._PREBATTLE_TYPE, self._client_prbSquadEntityClass, self._personality)
        prb_utils.addBattleSelectorSquadItem(self._CLIENT_PRB_ACTION_NAME_SQUAD, self._client_selectorSquadItemsCreator, self._personality)
        prb_utils.addSquadFinder(self._ARENA_GUI_TYPE, self._client_squadFinderClass, self._personality)
        prb_utils.addPrbClientCombinedIds(self._PREBATTLE_TYPE, PREBATTLE_TYPE.UNIT, self._personality)

    def registerGameControllers(self):
        from gui.shared.system_factory import registerGameControllers
        registerGameControllers(self._client_gameControllers)

    def registerBattleControllersRepository(self):
        from gui.shared.system_factory import registerBattleControllerRepo
        registerBattleControllerRepo(self._ARENA_GUI_TYPE, self._client_battleControllersRepository)

    def registerBattleResultsConfig(self):
        config = self._BATTLE_RESULTS_CONFIG
        if config is None:
            LOG_DEBUG('initBattleResultsConfigFromExtension: config is None')
            return
        else:
            from battle_results import battle_results_constants
            module = config.__name__
            battle_results_constants.PATH_TO_CONFIG.update({self._ARENA_BONUS_TYPE: module})
            return

    def registerClientBattleResultsComposer(self):
        from gui.shared.system_factory import registerBattleResultsComposer
        registerBattleResultsComposer(self._ARENA_BONUS_TYPE, self._client_battleResultsComposerClass)

    def registerClientBattleResultReusabled(self):
        from gui.battle_results.reusable import ReusableInfoFactory
        for key, infoCls in self._client_battleResultsReusables.iteritems():
            ReusableInfoFactory.addForBonusType(self._ARENA_BONUS_TYPE, key, infoCls)

    def registerVehicleTags(self):
        addVehicleTags(self._UNIT_MGR_FLAGS, self._REQUIRED_VEHICLE_TAGS, self._FORBIDDEN_VEHICLE_TAGS, self._NEW_VEHICLES_TAGS, self._personality)

    def registerClientSeasonType(self, extConstants):
        extConstants.GameSeasonType.inject(self._personality)
        from gui.shared.system_factory import registerSeasonProviderHandler
        registerSeasonProviderHandler(self._CLIENT_GAME_SEASON_TYPE, self._client_seasonControllerHandler)

    def registerBaseSeasonType(self, extConstants):
        extConstants.GameSeasonType.inject(self._personality)
        if self._SEASON_TYPE_BY_NAME is not None:
            SEASON_TYPE_BY_NAME.update({self._SEASON_TYPE_BY_NAME: self._SEASON_TYPE})
            SEASON_NAME_BY_TYPE.update({self._SEASON_TYPE: self._SEASON_TYPE_BY_NAME})
        return

    def registerBaseSeasonManager(self):
        if self._SEASON_MANAGER_TYPE is not None:
            import season_helpers
            season_helpers.SEASON_MANAGERS.append(season_helpers.SeasonManager(*self._SEASON_MANAGER_TYPE))
            season_helpers._SEASON_MANAGERS_BY_TYPE = {mgr.type:mgr for mgr in season_helpers.SEASON_MANAGERS}
        return

    def registerScaleformRequiredLibraries(self):
        if self._client_lobbyRequiredLibraries:
            from gui.Scaleform.required_libraries_config import addLobbyRequiredLibraries
            addLobbyRequiredLibraries(self._client_lobbyRequiredLibraries, __name__)
        if self._client_battleRequiredLibraries:
            from gui.Scaleform.required_libraries_config import addBattleRequiredLibraries
            addBattleRequiredLibraries(self._client_battleRequiredLibraries, __name__)

    def registerSystemMessagesTypes(self):
        SYS_MESSAGE_TYPE.inject(self._SM_TYPES)

    def registerBattleResultSysMsgType(self):
        from battle_results import ARENA_BONUS_TYPE_TO_SYS_MESSAGE_TYPE
        if self._ARENA_BONUS_TYPE in ARENA_BONUS_TYPE_TO_SYS_MESSAGE_TYPE:
            raise SoftException('ARENA_BONUS_TYPE_TO_SYS_MESSAGE_TYPE already has ARENA_BONUS_TYPE:{t}. Personality: {p}'.format(t=self._ARENA_BONUS_TYPE, p=self._personality))
        try:
            msgTypeIndex = SYS_MESSAGE_TYPE.__getattr__(self._SM_TYPE_BATTLE_RESULT).index()
        except AttributeError:
            raise SoftException('No index for {attr} found. Use registerSystemMessagesTypes before')

        ARENA_BONUS_TYPE_TO_SYS_MESSAGE_TYPE.update({self._ARENA_BONUS_TYPE: msgTypeIndex})
        msg = 'ARENA_BONUS_TYPE:{type}->{sysMsg} was added to UNIT_MGR_FLAGS_TO_QUEUE_TYPE. Personality: {p}'.format(type=self._ARENA_BONUS_TYPE, sysMsg=self._SM_TYPE_BATTLE_RESULT, p=self._personality)
        LOG_DEBUG(msg)

    def registerClientNotificationHandlers(self):
        from gui.shared.system_factory import registerNotificationsActionsHandlers
        registerNotificationsActionsHandlers(self._client_notificationActionHandlers)

    def registerMessengerClientFormatters(self, extGuiConstants):
        extGuiConstants.SCH_CLIENT_MSG_TYPE.inject(self._personality)
        from gui.shared.system_factory import registerMessengerClientFormatter
        for sysMsgType, formatter in self._client_messengerClientFormatters.iteritems():
            registerMessengerClientFormatter(sysMsgType, formatter)

    def registerMessengerServerFormatters(self):
        from gui.shared.system_factory import registerMessengerServerFormatter
        for sysMsgType, formatter in self._client_messengerServerFormatters.iteritems():
            registerMessengerServerFormatter(sysMsgType, formatter)

    def registerClientTokenQuestsSubFormatters(self):
        from gui.shared.system_factory import registerTokenQuestsSubFormatters
        registerTokenQuestsSubFormatters(self._client_tokenQuestsSubFormatters)
