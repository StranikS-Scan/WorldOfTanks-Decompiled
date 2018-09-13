# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/BattleTypeSelectPopover.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from constants import PREBATTLE_TYPE, ACCOUNT_ATTR, QUEUE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import GUI_SETTINGS, game_control
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.meta.BattleTypeSelectPopoverMeta import BattleTypeSelectPopoverMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from gui.shared.fortifications import isSortieEnabled, isFortificationEnabled
from gui.shared.server_events.EventsCache import g_eventsCache
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from web_stubs import i18n
from gui.shared.utils.requesters import StatsRequester
from gui.prb_control import areSpecBattlesHidden
from gui.Scaleform.framework import AppRef, ViewTypes
from gui.shared import EVENT_BUS_SCOPE, events
from gui.prb_control.context import PrebattleAction

class BattleTypeSelectPopover(BattleTypeSelectPopoverMeta, SmartPopOverView, View, AppRef, GlobalListener):

    def __init__(self, ctx):
        super(BattleTypeSelectPopover, self).__init__()
        self.__actionsLockedInViews = {VIEW_ALIAS.BATTLE_QUEUE, VIEW_ALIAS.LOBBY_TRAININGS, VIEW_ALIAS.LOBBY_TRAINING_ROOM}
        self.__isActionsLocked = False
        self.__currentLockedView = None
        return

    def _populate(self):
        isViewAvailable = self.app.containerManager.isViewAvailable(ViewTypes.LOBBY_SUB)
        if isViewAvailable:
            view = self.app.containerManager.getView(ViewTypes.LOBBY_SUB)
            self.__currentLockedView = view.settings.alias
        elif self.app.loaderManager.isViewLoading(VIEW_ALIAS.LOBBY_HANGAR):
            self.__currentLockedView = VIEW_ALIAS.LOBBY_HANGAR
        super(BattleTypeSelectPopover, self)._populate()
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        g_currentVehicle.onChanged += self.onVehicleChange
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdate, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventsCache.onSyncCompleted += self.onEventsCacheResync
        self.update()

    def onVehicleChange(self):
        self.update()

    def selectFight(self, actionName):
        if actionName == PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE:
            LOG_DEBUG('Disabling random battle start on list item click')
            return
        else:
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher is not None:
                dispatcher.doAction(PrebattleAction(actionName))
            else:
                LOG_ERROR('Prebattle dispatcher is not defined')
            return

    @process
    def update(self):
        accountAttrs = yield StatsRequester().getAccountAttrs()
        prbDispatcher = g_prbLoader.getDispatcher()
        if not prbDispatcher:
            return
        playerInfo = prbDispatcher.getPlayerInfo()
        isCreator = playerInfo.isCreator
        funcState = prbDispatcher.getFunctionalState()
        hasModalEntity = funcState.hasModalEntity
        inPrebattle = funcState.isInPrebattle()
        inUnit = funcState.isInUnit(PREBATTLE_TYPE.UNIT)
        inSortie = funcState.isInUnit(PREBATTLE_TYPE.SORTIE)
        inPreQueue = funcState.isInPreQueue()
        isTraining = funcState.isInPrebattle(PREBATTLE_TYPE.TRAINING)
        isInRoaming = game_control.g_instance.roaming.isInRoaming()
        hasHistoricalBattles = bool(g_eventsCache.getHistoricalBattles())
        disabled = False
        if self.__isActionsLocked:
            disabled = True
        else:
            canDo, restriction = prbDispatcher.canPlayerDoAction()
            if not canDo:
                disabled = True
        itemDisabled = disabled
        if not inPrebattle:
            itemDisabled = inPreQueue or self.__currentLockedView == VIEW_ALIAS.LOBBY_TRAININGS
        fightTypes = list()
        if self.__currentLockedView == VIEW_ALIAS.BATTLE_QUEUE:
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_STANDART, PREBATTLE_ACTION_NAME.LEAVE_RANDOM_QUEUE, True, TOOLTIPS.BATTLETYPES_STANDART, MENU.HEADERBUTTONS_BATTLE_TYPES_STANDARTLEAVE_DESCR, PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE, True))
        else:
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_STANDART, PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE, itemDisabled or hasModalEntity, TOOLTIPS.BATTLETYPES_STANDART, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_STANDART_DESCR), PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE, False))
        isHistoricalNewUnit = not selectorUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.HISTORICAL)
        if funcState.isInPreQueue(QUEUE_TYPE.HISTORICAL):
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_HISTORICALBATTLESLEAVE, PREBATTLE_ACTION_NAME.PREQUEUE_LEAVE, self.__currentLockedView == VIEW_ALIAS.BATTLE_QUEUE, TOOLTIPS.BATTLETYPES_LEAVEHISTORICAL, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_HISTORICALBATTLESLEAVE_DESCR), PREBATTLE_ACTION_NAME.HISTORICAL, True, isHistoricalNewUnit))
        else:
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_HISTORICALBATTLES, PREBATTLE_ACTION_NAME.HISTORICAL, itemDisabled or hasModalEntity or isInRoaming or not hasHistoricalBattles, TOOLTIPS.BATTLETYPES_HISTORICAL, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_HISTORICALBATTLES_DESCR), PREBATTLE_ACTION_NAME.HISTORICAL, False, isHistoricalNewUnit))
        if funcState.isInPrebattle(PREBATTLE_TYPE.SQUAD):
            fightTypes.append(self.__formBattleTypeSelectorData('#menu:headerButtons/battle/types/squadLeave%s' % ('Owner' if isCreator else ''), PREBATTLE_ACTION_NAME.PREBATTLE_LEAVE, self.__currentLockedView == VIEW_ALIAS.BATTLE_QUEUE, TOOLTIPS.BATTLETYPES_SQUADLEAVE, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUADLEAVE_DESCR), PREBATTLE_ACTION_NAME.SQUAD, True))
        else:
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD, PREBATTLE_ACTION_NAME.SQUAD, itemDisabled or hasModalEntity, TOOLTIPS.BATTLETYPES_SQUAD, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SQUAD_DESCR), PREBATTLE_ACTION_NAME.SQUAD, False))
        is7x7NewUnit = not selectorUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.UNIT)
        if inUnit:
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_UNITLEAVE, PREBATTLE_ACTION_NAME.UNIT_LEAVE, False, TOOLTIPS.BATTLETYPES_LEAVEUNIT, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_LEAVEUNIT_DESCR), PREBATTLE_ACTION_NAME.UNIT, True, is7x7NewUnit))
        else:
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_UNIT, PREBATTLE_ACTION_NAME.UNIT, itemDisabled or inPrebattle or inSortie or not accountAttrs & ACCOUNT_ATTR.RANDOM_BATTLES, TOOLTIPS.BATTLETYPES_UNIT, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_UNIT_DESCR), PREBATTLE_ACTION_NAME.UNIT, False, is7x7NewUnit))
        if funcState.isInPrebattle(PREBATTLE_TYPE.COMPANY):
            fightTypes.append(self.__formBattleTypeSelectorData('#menu:headerButtons/battle/types/companyLeave%s' % ('Owner' if isCreator else ''), PREBATTLE_ACTION_NAME.PREBATTLE_LEAVE, self.__currentLockedView == VIEW_ALIAS.BATTLE_QUEUE, TOOLTIPS.BATTLETYPES_LEAVECOMPANY, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_LEAVECOMPANY_DESCR), PREBATTLE_ACTION_NAME.COMPANY_LIST, True))
        else:
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_COMPANY, PREBATTLE_ACTION_NAME.COMPANY_LIST, itemDisabled or hasModalEntity, TOOLTIPS.BATTLETYPES_COMPANY, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_COMPANY_DESCR), PREBATTLE_ACTION_NAME.COMPANY_LIST, False))
        if isFortificationEnabled():
            sortie = not selectorUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.SORTIE)
            if inSortie:
                fightTypes.append(self.__formBattleTypeSelectorData(label_=MENU.HEADERBUTTONS_BATTLE_TYPES_FORTLEAVE, data_=PREBATTLE_ACTION_NAME.SORTIE_LEAVE, disabled_=False, tooltip_=TOOLTIPS.BATTLETYPES_LEAVEFORTIFICATION, descr_=MENU.HEADERBUTTONS_BATTLE_TYPES_LEAVEFORT_DESCR, icon_=PREBATTLE_ACTION_NAME.SORTIE, active_=True, isNewUnit_=sortie))
            else:
                fightTypes.append(self.__formBattleTypeSelectorData(label_=MENU.HEADERBUTTONS_BATTLE_TYPES_FORT, data_=PREBATTLE_ACTION_NAME.SORTIE, disabled_=not isSortieEnabled() or itemDisabled or isInRoaming or inPrebattle or inUnit, tooltip_=TOOLTIPS.BATTLETYPES_FORTIFICATION, descr_='', icon_=PREBATTLE_ACTION_NAME.SORTIE, active_=False, isNewUnit_=sortie))
        if GUI_SETTINGS.specPrebatlesVisible:
            if funcState.isInSpecialPrebattle():
                fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_SPECLEAVE, PREBATTLE_ACTION_NAME.PREBATTLE_LEAVE, False, TOOLTIPS.BATTLETYPES_LEAVESPEC, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_LEAVESPEC_DESCR), PREBATTLE_ACTION_NAME.SPEC_BATTLE_LIST, True))
            else:
                fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_SPEC, PREBATTLE_ACTION_NAME.SPEC_BATTLE_LIST, itemDisabled or hasModalEntity or areSpecBattlesHidden(), TOOLTIPS.BATTLETYPES_SPEC, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_SPEC_DESCR), PREBATTLE_ACTION_NAME.SPEC_BATTLE_LIST, False))
        LOG_DEBUG('!!!!!!!!!!!!!!!!!!!!!!', isTraining, self.__currentLockedView, VIEW_ALIAS.LOBBY_TRAININGS)
        if isTraining:
            fightTypes.append(self.__formBattleTypeSelectorData('#menu:headerButtons/battle/types/trainingLeave%s' % ('Owner' if isCreator else ''), PREBATTLE_ACTION_NAME.PREBATTLE_LEAVE, False, TOOLTIPS.BATTLETYPES_LEAVETRAINING, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_LEAVETRAINING_DESCR), PREBATTLE_ACTION_NAME.TRAINING_LIST, True))
        elif self.__currentLockedView == VIEW_ALIAS.LOBBY_TRAININGS:
            fightTypes.append(self.__formBattleTypeSelectorData('#menu:headerButtons/battle/types/trainingLeave', PREBATTLE_ACTION_NAME.LEAVE_TRAINING_LIST, False, TOOLTIPS.BATTLETYPES_LEAVETRAINING, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_LEAVETRAINING_DESCR), PREBATTLE_ACTION_NAME.TRAINING_LIST, True))
        else:
            fightTypes.append(self.__formBattleTypeSelectorData(MENU.HEADERBUTTONS_BATTLE_TYPES_TRAINING, PREBATTLE_ACTION_NAME.TRAINING_LIST, disabled or hasModalEntity, TOOLTIPS.BATTLETYPES_TRAINING, i18n.makeString(MENU.HEADERBUTTONS_BATTLE_TYPES_TRAINING_DESCR), PREBATTLE_ACTION_NAME.TRAINING_LIST, False))
        self.as_updateS(fightTypes)

    def __formBattleTypeSelectorData(self, label_, data_, disabled_, tooltip_, descr_, icon_, active_, isNewUnit_ = False):
        return {'label': label_,
         'data': data_,
         'disabled': disabled_,
         'tooltip': tooltip_,
         'description': i18n.makeString(descr_),
         'icon': icon_,
         'active': active_,
         'isNew': isNewUnit_}

    def __onViewAddedToContainer(self, _, pyEntity):
        settings = pyEntity.settings
        if settings.type is ViewTypes.LOBBY_SUB:
            alias = settings.alias
            if alias == VIEW_ALIAS.BATTLE_LOADING:
                return
            if alias in self.__actionsLockedInViews:
                self.__isActionsLocked = True
                self.__currentLockedView = alias
            else:
                self.__isActionsLocked = False
                self.__currentLockedView = None
            self.update()
        return

    def onEventsCacheResync(self, *args):
        self.update()

    def _dispose(self):
        self.__currentLockedView = None
        g_eventsCache.onSyncCompleted -= self.onEventsCacheResync
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        g_currentVehicle.onChanged -= self.onVehicleChange
        super(BattleTypeSelectPopover, self)._dispose()
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdate, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __handleFightButtonUpdate(self, event):
        self.update()

    def onPreQueueSettingsChanged(self, diff):
        self.update()
