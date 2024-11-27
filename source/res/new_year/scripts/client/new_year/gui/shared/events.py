# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/events.py
from gui.shared.events import HasCtxEvent

class NewYearEvent(HasCtxEvent):
    ON_BREAK_TOYS_FILTER_APPLIED = 'newYear/onBreakToysFilterApplied'
    ON_BREAK_TOYS_ANIMATION_COMPLETED = 'newYear/onBreakToysAnimationCompleted'
    ON_PRE_SWITCH_VIEW = 'newYear/onPreSwitchView'
    ON_SWITCH_VIEW = 'newYear/onSwitchView'
    ON_SIDEBAR_SELECTED = 'newYear/onSidebarSelected'
    SELECT_SIDEBAR_TAB_OUTSIDE = 'newYear/selectSidebarTabOutside'
    UPDATE_BACK_BUTTON = 'newYear/updateBackButton'
    ON_TOY_INSTALLED = 'newYear/onToyInstalled'
