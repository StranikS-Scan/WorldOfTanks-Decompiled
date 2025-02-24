# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/prb_control/__init__.py


def registerComp7OthersPrbParams():
    from comp7.gui.comp7_constants import PREBATTLE_ACTION_NAME
    from comp7.gui.impl.lobby.tooltips.main_widget_tooltip import MainWidgetTooltip
    from comp7.gui.impl.lobby.tooltips.rank_inactivity_tooltip import RankInactivityTooltip
    from comp7.gui.prb_control.storages.comp7_storage import Comp7Storage
    from comp7_common.comp7_constants import PREBATTLE_TYPE
    from constants import ARENA_BONUS_TYPE
    from constants import QUEUE_TYPE
    from gui.impl.gen import R
    from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
    from gui.impl.lobby.mode_selector.items import _arenaBonusTypeByModeName
    from gui.impl.lobby.platoon.platoon_config import PREBATTLE_TYPE_TO_VEH_CRITERIA, RANDOM_VEHICLE_CRITERIA
    from gui.prb_control.prb_getters import _PRB_TO_QUEUE
    from gui.prb_control.settings import ENTER_UNIT_MGR_RESET_ERRORS
    from gui.prb_control.storages import makeQueueName
    from gui.shared.system_factory import registerModeSelectorTooltips, registerPrbStorage
    from UnitBase import UNIT_ERROR
    registerModeSelectorTooltips([ModeSelectorTooltipsConstants.COMP7_CALENDAR_DAY_EXTENDED_INFO], {R.views.comp7.lobby.tooltips.MainWidgetTooltip(): MainWidgetTooltip,
     R.views.comp7.lobby.tooltips.RankInactivityTooltip(): RankInactivityTooltip})
    registerPrbStorage(makeQueueName(QUEUE_TYPE.COMP7), Comp7Storage())
    _PRB_TO_QUEUE.update({PREBATTLE_TYPE.COMP7: QUEUE_TYPE.COMP7})
    _arenaBonusTypeByModeName.update({PREBATTLE_ACTION_NAME.COMP7: ARENA_BONUS_TYPE.COMP7})
    PREBATTLE_TYPE_TO_VEH_CRITERIA.update({PREBATTLE_TYPE.COMP7: RANDOM_VEHICLE_CRITERIA})
    ENTER_UNIT_MGR_RESET_ERRORS.append(UNIT_ERROR.COMP7_QUALIFICATION)
