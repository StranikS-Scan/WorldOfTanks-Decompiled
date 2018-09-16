# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_constants.py
from collections import namedtuple
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from shared_utils import CONST_CONTAINER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
MarathonData = namedtuple('MarathonData', 'prefix tokenPrefix url businessSwitcher label tabTooltip tabTooltipDisabled\n                          vehiclePrefix vehicleID suspend completedTokenPostfix awardTokens questsInChain\n                          minVehicleLevel showInPostBattle tooltipHeaderType showFlagTooltipBottom showFlagIcons\n                          tooltips icons quests')
TooltipsData = namedtuple('TooltipsData', 'header body bodyExtra errorBattleType errorVehType extraStateSteps extraStateDiscount\n                          extraStateCompleted stateStart stateEnd stateProgress daysShort hoursShort')
IconsData = namedtuple('IconsData', 'tooltipHeader libraryOkIcon mainHangarFlag okIcon timeIcon alertIcon iconFlag saleIcon\n                       mapFlagHeaderIcon')
QuestsData = namedtuple('QuestsData', 'titleSetProgress autoSetAnnounce autoSetProgress autoSetFinished announceTime timeFinish')
COUNTDOWN_TOOLTIP_HEADER = 'countdown'
PROGRESS_TOOLTIP_HEADER = 'progress'
TEXT_TOOLTIP_HEADER = 'simple_text'

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


MARATHONS_DATA = (MarathonData(prefix='bloggers_event:', tokenPrefix='bloggers_event:BE', url='bloggersEventUrl', businessSwitcher='isMarathonEnabled', label=QUESTS.MISSIONS_TAB_LABEL_BLOGGERS, tabTooltip=QUESTS.MISSIONS_TAB_BLOGGERS, tabTooltipDisabled=QUESTS.MISSIONS_TAB_BLOGGERS_DISABLED, vehiclePrefix='It13_Progetto_M35_mod_46', vehicleID=51361, suspend=':suspend', completedTokenPostfix='STOP', awardTokens=('bloggers_event:BESR7DONE',), questsInChain=50, minVehicleLevel=8, showInPostBattle=True, tooltipHeaderType=TEXT_TOOLTIP_HEADER, showFlagTooltipBottom=False, showFlagIcons=True, tooltips=TooltipsData(header=TOOLTIPS.BLOGGERS_HEADER, body=TOOLTIPS.BLOGGERS_BODY, bodyExtra=TOOLTIPS.MARATHON_BODY_EXTRA, errorBattleType=TOOLTIPS.KURSK_ERROR_BATTLE_TYPE, errorVehType=TOOLTIPS.MARATHON_ERROR_VEH_TYPE, extraStateSteps=TOOLTIPS.KURSK_EXTRA_STATE_STEPS, extraStateDiscount=TOOLTIPS.MARATHON_EXTRA_STATE_DISCOUNT, extraStateCompleted=TOOLTIPS.MARATHON_EXTRA_STATE_COMPLETED, stateStart=TOOLTIPS.MARATHON_STATE_START, stateEnd=TOOLTIPS.MARATHON_STATE_END, stateProgress=TOOLTIPS.KURSK_PROGRESS, daysShort=TOOLTIPS.TEMPLATE_DAYS_VALUE, hoursShort=TOOLTIPS.TEMPLATE_HOURS_SHORT), icons=IconsData(tooltipHeader=RES_ICONS.MAPS_ICONS_QUESTS_BLOGGERSTOOLTIPHEADER, libraryOkIcon=RES_ICONS.MAPS_ICONS_LIBRARY_OKICON, mainHangarFlag=RES_ICONS.MAPS_ICONS_LIBRARY_HANGARFLAG_FLAG_BLOGGERS, okIcon=RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ICON_FLAG, timeIcon=RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ICON_FLAG, alertIcon=RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ICON_FLAG, iconFlag=RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ICON_FLAG, saleIcon=RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ICON_FLAG, mapFlagHeaderIcon={MARATHON_STATE.ENABLED_STATE: RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ICON_LIKE,
  MARATHON_STATE.DISABLED_STATE: RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ICON_DIZ}), quests=QuestsData(titleSetProgress=QUESTS.ACTIONCARD_TITLE_SET_MARATHONINPROGRESS, autoSetAnnounce=QUESTS.ACTION_AUTO_SET_MARATHONANNOUNCE, autoSetProgress=QUESTS.ACTION_AUTO_SET_MARATHONINPROGRESS, autoSetFinished=QUESTS.ACTION_AUTO_SET_MARATHONFINISHED, announceTime=QUESTS.ACTION_MARATHON_ANNOUNCETIME, timeFinish=QUESTS.ACTION_TIME_FINISH)),)
DEFAULT_MARATHON_PREFIX = MARATHONS_DATA[0].prefix if any(MARATHONS_DATA) else None
ZERO_TIME = 0.0
