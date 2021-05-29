# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/mode_selector/constants.py


class LOG_KEYS(object):
    RANDOM_CARD_FILTER = 'random_card_filter'
    ENTRY_POINT = 'entry_point'
    MS_WINDOW = 'ms_window'


class LOG_ACTIONS(object):
    CHANGED = 'changed'
    CARD_CLICKED = 'card_clicked'
    INFO_PAGE_ICON_CLICKED = 'info_page_icon_clicked'
    CLOSED = 'closed'
    OPENED = 'opened'
    TOOLTIP_WATCHED = 'tooltip_watched'


class LOG_CLOSE_DETAILS(object):
    CARD_CLICKED = 'card_clicked'
    OTHER = 'other'
    SELECTOR = 'selector'


FEATURE = 'mode_selector_2'
SELECTOR_BUTTON_TOOLTIP_LOG_ID = 'modeSelectorBtn'
