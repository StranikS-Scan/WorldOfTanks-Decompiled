# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/training_room_external_handlers.py
from account_helpers import isDemonstrator, isDemonstratorExpert
from comp7.gui.prb_control.entities.limits import Comp7TrainingLimits
from comp7.gui.prb_control.entities.pre_queue.vehicles_watcher import Comp7VehiclesWatcher
from constants import PREBATTLE_ERRORS, PREBATTLE_STATE
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control import prb_getters
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.training_room_external_handlers import TrainingRoomBaseHandler
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache

class Comp7TrainingRoomHandler(TrainingRoomBaseHandler):
    _GUI_TYPE_NAME = 'comp7'

    def getArenaFilter(self):
        return _isComp7ArenaFilter

    def getArenaData(self):
        return {'size': self.getMaxPlayersInTeam(),
         'canChangeArenaTime': False,
         'additionalInfo': self.getAdditionalInfo()}

    def getAdditionalInfo(self):
        return PREBATTLE_ALIASES.TRAINING_ADDITIONAL_INFO_COMP7

    def getIcon(self):
        return BATTLE_TYPES.COMP7

    def getMaxPlayersInTeam(self):
        return _getComp7MaxPlayersInTeam()

    def getObserverValidator(self):
        return _canBeComp7Observer

    def getPlayerReadyHandler(self):
        return _handleComp7PlayerReady

    def getPrebattleLimits(self):
        return Comp7TrainingLimits

    def getPrebattlePropertyChecker(self):
        return _shouldComp7PlayerStateBeValidated

    def getVehicleWatcherType(self):
        return Comp7VehiclesWatcher

    def getClientMessageData(self, errorType=None):
        return (SYSTEM_MESSAGES.TRAINING_ERROR_ONSLAUGHTROSTERLIMIT, {'numPlayers': self.getMaxPlayersInTeam()}) if errorType == PREBATTLE_ERRORS.ONSLAUGHT_ROSTER_LIMIT else None

    def isEnabledForGuiTypeName(self, guiTypeName=None):
        return guiTypeName == self._GUI_TYPE_NAME


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _canBeComp7Observer(itemsCache=None):
    accountAttrs = itemsCache.items.stats.attributes
    return isDemonstrator(accountAttrs) or isDemonstratorExpert(accountAttrs)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getComp7MaxPlayersInTeam(comp7Controller=None):
    return comp7Controller.getModeSettings().numPlayers


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _isComp7ArenaFilter(arena, settings, comp7Controller=None):
    if not comp7Controller.isTrainingEnabled() or settings.isDevBattle:
        return False
    comp7Config = comp7Controller.getModeSettings()
    return arena.geometryID in comp7Config.maps


def _handleComp7PlayerReady():
    g_eventDispatcher.loadTrainingRoom()


def _shouldComp7PlayerStateBeValidated(propertyName):
    if propertyName != 'state':
        return False
    propertyValue = prb_getters.getClientPrebattle().properties['state']
    return propertyValue == PREBATTLE_STATE.IDLE
