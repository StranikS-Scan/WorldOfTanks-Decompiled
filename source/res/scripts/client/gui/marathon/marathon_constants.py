# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_constants.py
from collections import namedtuple
from shared_utils import CONST_CONTAINER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
MarathonData = namedtuple('MarathonData', 'prefix tokenPrefix url label tabTooltip vehiclePrefix vehicleID suspend\n                          completedTokenPostfix awardTokens questsInChain minVehicleLevel showInPostBattle\n                          tooltipHeaderType tooltips icons quests')
TooltipsData = namedtuple('TooltipsData', 'header body bodyExtra errorBattleType errorVehType extraStateSteps extraStateDiscount\n                          extraStateCompleted stateStart stateEnd stateProgress daysShort hoursShort')
IconsData = namedtuple('IconsData', 'tooltipHeader libraryOkIcon mainHangarFlag okIcon timeIcon alertIcon iconFlag saleIcon')
QuestsData = namedtuple('QuestsData', 'titleSetProgress autoSetAnnounce autoSetProgress autoSetFinished announceTime timeFinish')
COUNTDOWN_TOOLTIP_HEADER = 'countdown'
PROGRESS_TOOLTIP_HEADER = 'progress'
MARATHONS_DATA = tuple()
DEFAULT_MARATHON_PREFIX = MARATHONS_DATA[0].prefix if any(MARATHONS_DATA) else None
ZERO_TIME = 0.0

class MARATHON_STATE(CONST_CONTAINER):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    FINISHED = 3
    SUSPENDED = 4
    DISABLED = 5
    UNKNOWN = 6
    ENABLED_STATE = (NOT_STARTED, IN_PROGRESS, FINISHED)
    DISABLED_STATE = (SUSPENDED, DISABLED, UNKNOWN)


class MARATHON_WARNING(CONST_CONTAINER):
    WRONG_VEH_TYPE = 'veh_type'
    WRONG_BATTLE_TYPE = 'battle_type'
    NONE = ''


MAP_FLAG_HEADER_ICON = {MARATHON_STATE.ENABLED_STATE: RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_CUP_ICON,
 MARATHON_STATE.DISABLED_STATE: RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_CUP_DISABLE_ICON}
