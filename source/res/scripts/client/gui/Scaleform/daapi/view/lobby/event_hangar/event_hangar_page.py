# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_hangar/event_hangar_page.py
import itertools
import BigWorld
import SoundGroups
from adisp import process
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items.Vehicle import getTypeSmallIconPath, getLevelIconPath, getContourIconPath
from gui.Scaleform.daapi.view.meta.EventHangarPageMeta import EventHangarPageMeta
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.shared import EVENT_BUS_SCOPE
from helpers import dependency, time_utils
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.event_hangar_sound_controller import IEventHangarSoundController
from skeletons.gui.game_event_controller import IGameEventController
from gui.Scaleform.locale.EVENT import EVENT
from gui.shared import events
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.lobby.event_hangar.vo_converters import makeAbbilityVO
from gui.prb_control import prbEntityProperty
from gui.shared.utils import getPlayerDatabaseID
from gui.prb_control.entities.listener import IGlobalListener
from skeletons.gui.game_control import IManualController
from gui.Scaleform.daapi.view.lobby.manual.event_manual_chapter_view import EVENT_CHAPTER_INDEX, EVENT_CHAPTER_SECTION
from gui.server_events.awards_formatters import getEventAwardFormatter, AWARDS_SIZES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from items import vehicles
_FIRST_FRONT_ID = 0
_SECOND_FRONT_ID = 1
_TEST_GENERAL_ID = 6
_ENERGY_UPDATE_TIME = 1.0
_MAX_PROGRESS_BAR_VALUE = 100

class EventHangarPage(LobbySelectableView, EventHangarPageMeta, IGlobalListener):
    gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    eventHangarSounds = dependency.descriptor(IEventHangarSoundController)
    manualController = dependency.descriptor(IManualController)
    __background_alpha__ = 0.0
    __HANGAR_UI_NEWS_IN_SOUND = 'ev_2019_secret_event_1_hangar_event_news_in'

    def __init__(self, *args, **kwargs):
        super(EventHangarPage, self).__init__(*args, **kwargs)
        self._energyCallbackID = None
        self.__linkedSetHintsShown = False
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onPrbEntitySwitching(self):
        self.stopPrbListening()

    def onPrbEntitySwitched(self):
        self.startPrbListening()
        if self.prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
            self._onGeneralsProgressChanged()

    def onEscapePress(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def closeView(self):
        self._leaveEvent()

    def onEventBannerClick(self):
        self._leaveEvent()

    def onGeneralSelected(self, generalId):
        self.gameEventController.setSelectedGeneralID(generalId)

    def onGeneralBuy(self, generalId):
        self.gameEventController.getGeneral(generalId).buy()

    def onEnergyBuy(self, generalId):
        self.gameEventController.getEnergy().buy()

    def onEventStoryBannerClick(self):
        pass

    def onGeneralProgressBannerClick(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EVENT_GENERAL_PROGRESS_PAGE), scope=EVENT_BUS_SCOPE.LOBBY)

    def onGeneralSpeedUpClick(self, generalId):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EVENT_GENERAL_PROGRESS_PAGE, ctx={'generalId': generalId}), scope=EVENT_BUS_SCOPE.LOBBY)

    def onEventNewsBannerClick(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EVENT_MANUAL_PAGE), scope=EVENT_BUS_SCOPE.LOBBY)
        SoundGroups.g_instance.playSound2D(self.__HANGAR_UI_NEWS_IN_SOUND)

    def onUnitVehiclesChanged(self, dbID, vInfos):
        self.onUnitPlayerInfoChanged(vInfos)

    def onUnitPlayerInfoChanged(self, pInfo):
        self._onGeneralsProgressChanged()

    def onUnitPlayerRemoved(self, pInfo):
        self._onGeneralsProgressChanged()

    def _populate(self):
        super(EventHangarPage, self)._populate()
        self.gameEventController.onProgressChanged += self._onGeneralsProgressChanged
        g_playerEvents.onGeneralLockChanged += self._onGeneralsProgressChanged
        energy = self.gameEventController.getEnergy()
        energy.onEnergyChanged += self._onEnergyChanged
        self._onEnergyChanged(energy.getCurrentCount())
        self.startPrbListening()
        self.startGlobalListening()
        self.gameEventController.onSelectedGeneralChanged += self._onSelectedGeneralChanged
        self._onGeneralsProgressChanged()
        data = self.manualController.getChapterUIData(EVENT_CHAPTER_INDEX, EVENT_CHAPTER_SECTION)
        manualPageMax = len(data['pages'])
        serverSettings = self.settingsCore.serverSettings
        newPages = len([ ind for ind in range(manualPageMax) if not serverSettings.isEventManualShowed(ind) ])
        self.as_setNewsCounterS(newPages)
        self.hangarSpace.setVehicleSelectable(True)
        self.addListener(events.LinkedSetEvent.HINTS_VIEW, self.__onLinkedSetHintsView, scope=EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, ctx={'lobbyType': 'event'}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onLinkedSetHintsView(self, event):
        self.__linkedSetHintsShown = event.ctx['shown']

    def _dispose(self):
        self.removeListener(events.LinkedSetEvent.HINTS_VIEW, self.__onLinkedSetHintsView, scope=EVENT_BUS_SCOPE.LOBBY)
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, ctx={'lobbyType': None}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.gameEventController.onProgressChanged -= self._onGeneralsProgressChanged
        g_playerEvents.onGeneralLockChanged -= self._onGeneralsProgressChanged
        self.stopPrbListening()
        self.stopGlobalListening()
        self.gameEventController.onSelectedGeneralChanged -= self._onSelectedGeneralChanged
        self.gameEventController.getEnergy().onEnergyChanged -= self._onEnergyChanged
        self._stopEnergyTimer()
        self.hangarSpace.setVehicleSelectable(False)
        super(EventHangarPage, self)._dispose()
        return

    def _onGeneralsProgressChanged(self):
        generals = [ self._makeGeneralVO(general) for general in itertools.chain(self._getGeneralsByFront(_FIRST_FRONT_ID), self._getGeneralsByFront(_SECOND_FRONT_ID)) ]
        self.as_setDataS({'selectedGeneralId': self.gameEventController.getSelectedGeneralID(),
         'energy': self.gameEventController.getEnergy().getCurrentCount(),
         'generals': generals,
         'fronts': [ self._getFrontVO(front) for front in self._getFronts() ],
         'tooltip': '',
         'specialArgs': [],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_ENERGY_INFO,
         'isSpecial': True})
        self._onSelectedGeneralChanged()

    def _getFronts(self):
        return sorted((front for front in self.gameEventController.getFronts().itervalues()), key=lambda f: f.getID())

    def _getFrontVO(self, front):
        lastItem = front.items[-1]
        awardFormatter = getEventAwardFormatter()
        bonuses = awardFormatter.format(lastItem.getBonuses())
        if not bonuses:
            return None
        else:
            bonus = bonuses[0]
            frontTotalProgress = front.getTotalProgress()
            frontCurrentProgress = min(front.getCurrentProgress(), frontTotalProgress)
            frontID = front.getID()
            return {'title': _ms(EVENT.getFrontWithProgress(frontID)),
             'rewardIcon': bonus.images[AWARDS_SIZES.SMALL],
             'requirements': '{} / {}'.format(frontCurrentProgress, frontTotalProgress),
             'marks': '{} / {}'.format(front.getFrontMarksCount(), front.getFrontMarksTotalCount()),
             'frontId': frontID,
             'done': lastItem.isCompleted(),
             'overlayType': bonus.overlayType[AWARDS_SIZES.SMALL],
             'tooltip': bonus.tooltip,
             'specialAlias': TOOLTIPS_CONSTANTS.EVENT_AWARD_MODULE,
             'specialArgs': bonus.specialArgs + [front.getID()],
             'isSpecial': bonus.isSpecial}

    def _getGeneralsByFront(self, frontID):
        return sorted((general for general in self.gameEventController.getGenerals().itervalues() if general.getFrontID() == frontID and general.getID() < _TEST_GENERAL_ID), key=lambda g: g.getID())

    def _makeGeneralVO(self, general):
        generalID = general.getID()
        currentLevel = general.getCurrentProgressLevel()
        progressItem = general.getNextProgressItem()
        totalGeneralProgress = progressItem.getMaxProgress() if progressItem is not None else 0
        currentGeneralProgress = progressItem.getCurrentProgress() if progressItem is not None else 0
        unitReady, unitGeneralID = self.__getUnitReady()
        requireFront = self.__getUnitRequireFront()
        isWrongFront = requireFront is not None and requireFront is not general.getFrontID()
        abilitiesCurrent = list(general.getAbilitiesByLevel(currentLevel))
        abilitiesFull = list(general.getAbilitiesByLevel(general.getMaxLevel()))
        abilitiesData = []
        for i in xrange(len(abilitiesFull)):
            abilityID = abilitiesCurrent[i] if len(abilitiesCurrent) > i else abilitiesFull[i]
            itemDescr = vehicles.g_cache.equipments()[abilityID]
            abilitiesData.append({'icon': RES_ICONS.getGeneralAbilityIconTiny(itemDescr.iconName),
             'enabled': len(abilitiesCurrent) > i,
             'tooltip': makeTooltip(itemDescr.userString, itemDescr.description)})

        if general.isCompleted() or totalGeneralProgress == 0:
            progress = _MAX_PROGRESS_BAR_VALUE
        else:
            progress = _MAX_PROGRESS_BAR_VALUE * currentGeneralProgress / totalGeneralProgress
        return {'id': generalID,
         'level': currentLevel,
         'levelIcon': RES_ICONS.getGeneralLevelIcon(currentLevel),
         'enabled': self._isGeneralEnabled(general),
         'icon': self._getGeneralIcon(general),
         'bgImage': RES_ICONS.getGeneralBackground(general.getID()),
         'label': self.__getInfoText(general, unitReady, unitGeneralID, isWrongFront),
         'progress': progress,
         'clickable': not unitReady,
         'frontID': general.getFrontID(),
         'abilities': abilitiesData,
         'tooltip': '',
         'specialArgs': [generalID, isWrongFront],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_FACTION_INFO,
         'isSpecial': True}

    def _onSelectedGeneralChanged(self):
        selectedGeneral = self.gameEventController.getSelectedGeneral()
        level = selectedGeneral.getCurrentProgressLevel()
        isEnabled = self._isGeneralEnabled(selectedGeneral)
        self.as_setGeneralInfoS({'enabled': isEnabled,
         'level': level,
         'nameStr': EVENT.getGeneralTooltipHeader(selectedGeneral.getID()),
         'rank': {'level': level,
                  'tanks': [ self._createVehicleVO(typeCompDescr) for typeCompDescr in selectedGeneral.getVehiclesByLevel(level) ],
                  'items': [ makeAbbilityVO(abilityID, emptyLabel=True, isHangar=True) for abilityID in selectedGeneral.getAbilitiesByLevel(level) ]}})

    def _getGeneralBackGroundInfoInHangar(self, generalID, enabled):
        return RES_ICONS.getGeneralBackGroundInfoInHangar(generalID) if enabled else RES_ICONS.getGeneralDisableBackGroundInfoInHangar(generalID)

    def _createVehicleVO(self, typeCompDescr):
        vehicle = self.itemsCache.items.getStockVehicle(typeCompDescr, useInventory=True)
        return {'intCD': vehicle.intCD,
         'vehicleName': vehicle.longUserName,
         'vehicleTypeIcon': getTypeSmallIconPath(vehicle.type),
         'levelIcon': getLevelIconPath(vehicle.level),
         'vehicleIcon': getContourIconPath(vehicle.name)}

    def _getGeneralIcon(self, general):
        return RES_ICONS.getGeneralIconInHangar(general.getID())

    def _leaveEvent(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher:
            self.__doLeaveAction(dispatcher)

    def _isGeneralEnabled(self, general):
        availableGenerals = self.gameEventController.getAvailableGeneralIDs()
        return general.getID() in availableGenerals and not general.isLocked()

    def _on3DObjectMouseEnter(self, entity):
        super(EventHangarPage, self)._on3DObjectMouseEnter(entity)
        if not self.app.isModalViewShown() and not self.__linkedSetHintsShown:
            self.as_showVehicleTooltipS({'specialArgs': [entity.typeDescriptor.type.compactDescr]})

    def _on3DObjectMouseExit(self, entity):
        super(EventHangarPage, self)._on3DObjectMouseExit(entity)
        self.as_hideVehicleTooltipS()

    def _on3DObjectMouseDown(self):
        pass

    def _on3DObjectMouseUp(self):
        pass

    def _onEnergyChanged(self, newValue):
        self._stopEnergyTimer()
        expectedEnergyOnNextDay = self.gameEventController.getEnergy().getExpectedEnergyOnNextDay()
        if expectedEnergyOnNextDay > 0 >= newValue:
            self._startEnergyTimer()
        else:
            self.as_setTimerS('')

    def _startEnergyTimer(self):
        self._stopEnergyTimer()
        self._energyUpdateCallback()

    def _energyUpdateCallback(self):
        energy = self.gameEventController.getEnergy()
        expectedEnergyOnNextDay = energy.getExpectedEnergyOnNextDay()
        if expectedEnergyOnNextDay > 0 >= energy.getCurrentCount():
            self.as_setTimerS(time_utils.getTillTimeString(energy.getTimeLeftToRecharge(), '#event:hangar/energy'))
            self._energyCallbackID = BigWorld.callback(_ENERGY_UPDATE_TIME, self._energyUpdateCallback)
        else:
            self._stopEnergyTimer()
            self.as_setTimerS('')

    def _stopEnergyTimer(self):
        if self._energyCallbackID is not None:
            BigWorld.cancelCallback(self._energyCallbackID)
            self._energyCallbackID = None
        return

    @process
    def __doLeaveAction(self, dispatcher):
        yield dispatcher.doLeaveAction(LeavePrbAction(isExit=True))

    def __getUnitReady(self):
        entity = self.prbEntity
        if entity and entity.getEntityType() is PREBATTLE_TYPE.EVENT:
            _, unit = entity.getUnit()
            dbID = getPlayerDatabaseID()
            ready = unit.getVehicles().get(dbID) is not None
            if ready:
                pInfo = entity.getPlayerInfo(dbID=dbID)
                generalID, _, _ = pInfo.eventData
                return (True, generalID)
        return (False, 0)

    def __getUnitRequireFront(self):
        entity = self.prbEntity
        return entity.getRequireFront() if entity and entity.getEntityType() is PREBATTLE_TYPE.EVENT else None

    def __getInfoText(self, general, unitReady, unitGeneralID, isWrongFront):
        if general.isLocked():
            return _ms(EVENT.GENERALS_IN_BATTLE)
        if unitReady:
            if general.getID() is unitGeneralID:
                return _ms(MENU.TANKCAROUSEL_VEHICLESTATES_INPREBATTLE)
            return ''
        return _ms(MENU.TANKCAROUSEL_VEHICLESTATES_UNSUITABLETOQUEUE) if isWrongFront else ''
