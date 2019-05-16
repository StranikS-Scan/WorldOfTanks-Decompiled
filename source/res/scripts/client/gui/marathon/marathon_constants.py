# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_constants.py
from collections import namedtuple
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.impl import backport
from gui.impl.gen import R
from shared_utils import CONST_CONTAINER
MarathonData = namedtuple('MarathonData', 'prefix tokenPrefix bonusQuestPrefix bonusToken url label tabTooltip tabTooltipDisabled\n                          vehiclePrefix vehicleID showRewardVideo showRewardScreen suspend completedTokenPostfix\n                          awardTokens vehicleAwardTokens questsInChain minVehicleLevel showInPostBattle\n                          tooltipHeaderType showFlagTooltipBottom showFlagIcons sounds tooltips icons quests')
SoundsData = namedtuple('SoundsData', 'tabEnter tabExit')
TooltipsData = namedtuple('TooltipsData', 'header body bodyExtra errorBattleType errorVehType extraStateSteps extraStateDiscount\n                          extraStateVehicle extraStateReward stateStart stateEnd stateProgress\n                          daysShort hoursShort')
IconsData = namedtuple('IconsData', 'tooltipHeader libraryOkIcon libraryDoubleOkIcon mainHangarFlag okIcon doubleOkIcon timeIcon\n                       timeIconGlow alertIcon iconFlag saleIcon mapFlagHeaderIcon')
QuestsData = namedtuple('QuestsData', 'titleSetProgress autoSetAnnounce autoSetProgress autoSetFinished announceTime timeFinish')
COUNTDOWN_TOOLTIP_HEADER = 'countdown'
PROGRESS_TOOLTIP_HEADER = 'progress'
TEXT_TOOLTIP_HEADER = 'simple_text'
MARATHON_COMPLETE_URL_ADD = 'overlay/'

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


MARATHONS_DATA = (MarathonData(prefix='event_marathon_', tokenPrefix='event_marathon_D', bonusQuestPrefix='event_bonus_XPCXP_LVL', bonusToken='event_bonus_XPCXP_BONUS', url='marathonDDAYUrl', label=R.strings.quests.missions.tab.label.dday(), tabTooltip=QUESTS.MISSIONS_TAB_DDAY, tabTooltipDisabled=QUESTS.MISSIONS_TAB_DDAY, vehiclePrefix='france:F112_M10_RBFM', vehicleID=61249, showRewardVideo=True, showRewardScreen=True, suspend=':suspend', completedTokenPostfix='_PASS', awardTokens=('event_marathon_DDAY_COMPLETE',), vehicleAwardTokens=('event_marathon_DDAY_TB', 'event_marathon_DDAY_TF'), questsInChain=14, minVehicleLevel=4, showInPostBattle=True, tooltipHeaderType=COUNTDOWN_TOOLTIP_HEADER, showFlagTooltipBottom=True, showFlagIcons=True, sounds=SoundsData(tabEnter=backport.sound(R.sounds.tasks_dday_enter()), tabExit=backport.sound(R.sounds.tasks_dday_exit())), tooltips=TooltipsData(header=R.strings.tooltips.dday.header(), body=R.strings.tooltips.dday.body(), bodyExtra=R.strings.tooltips.dday.body.extra(), errorBattleType=R.strings.tooltips.marathon.error.battle_type(), errorVehType=R.strings.tooltips.dday.error.veh_type(), extraStateSteps=R.strings.tooltips.dday.extra_state.steps(), extraStateDiscount=R.strings.tooltips.marathon.extra_state.discount(), extraStateVehicle=R.strings.tooltips.dday.extra_state.vehicle.completed(), extraStateReward=R.strings.tooltips.dday.extra_state.rewards.completed(), stateStart=R.strings.tooltips.marathon.state.start(), stateEnd=R.strings.tooltips.marathon.state.end(), stateProgress=R.strings.tooltips.dday.progress(), daysShort=R.strings.tooltips.template.days.short(), hoursShort=R.strings.tooltips.template.hours.short()), icons=IconsData(tooltipHeader=backport.image(R.images.gui.maps.icons.quests.ddayTooltipHeader()), libraryOkIcon=backport.image(R.images.gui.maps.icons.library.okIcon()), libraryDoubleOkIcon=backport.image(R.images.gui.maps.icons.library.doubleCheckmark()), mainHangarFlag=backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_dd()), okIcon=backport.image(R.images.gui.maps.icons.library.marathon.ok_icon()), doubleOkIcon=backport.image(R.images.gui.maps.icons.library.marathon.double_ok_icon()), timeIcon=backport.image(R.images.gui.maps.icons.library.marathon.time_icon()), timeIconGlow=backport.image(R.images.gui.maps.icons.library.marathon.time_icon_glow()), alertIcon=backport.image(R.images.gui.maps.icons.library.marathon.alert_icon()), iconFlag=backport.image(R.images.gui.maps.icons.library.marathon.icon_flag()), saleIcon=backport.image(R.images.gui.maps.icons.library.marathon.sale_icon()), mapFlagHeaderIcon={MARATHON_STATE.ENABLED_STATE: backport.image(R.images.gui.maps.icons.library.marathon.cup_icon()),
  MARATHON_STATE.DISABLED_STATE: backport.image(R.images.gui.maps.icons.library.marathon.cup_disable_icon())}), quests=QuestsData(titleSetProgress=R.strings.quests.actionCard.title.set_MarathonInProgress(), autoSetAnnounce=R.strings.quests.action.auto.set_MarathonAnnounce(), autoSetProgress=R.strings.quests.action.auto.set_MarathonInProgress(), autoSetFinished=R.strings.quests.action.auto.set_MarathonFinished(), announceTime=R.strings.quests.action.marathon.announceTime(), timeFinish=R.strings.quests.action.time.finish())),)
DEFAULT_MARATHON_PREFIX = MARATHONS_DATA[0].prefix if any(MARATHONS_DATA) else None
ZERO_TIME = 0.0
