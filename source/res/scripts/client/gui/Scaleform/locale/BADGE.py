# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/locale/BADGE.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from debug_utils import LOG_WARNING

class BADGE(object):
    ACCOUNTPOPOVER_BADGE_TOOLTIP_BODY = '#badge:accountPopover/badge/tooltip/body'
    ACCOUNTPOPOVER_BADGE_TOOLTIP_HEADER = '#badge:accountPopover/badge/tooltip/header'
    BADGESPAGE_HEADER_CLOSEBTN_LABEL = '#badge:badgesPage/header/closeBtn/label'
    BADGESPAGE_BODY_UNCOLLECTED_TITLE = '#badge:badgesPage/body/uncollected/title'
    BADGESPAGE_DUMMY_TITLE = '#badge:badgesPage/dummy/title'
    BADGESPAGE_DUMMY_DESCR = '#badge:badgesPage/dummy/descr'
    BADGESPAGE_DUMMY_BUTTON_LABEL = '#badge:badgesPage/dummy/button/label'
    BADGE_0 = '#badge:badge_0'
    BADGE_0_DESCR = '#badge:badge_0_descr'
    BADGE_1 = '#badge:badge_1'
    BADGE_1_DESCR = '#badge:badge_1_descr'
    BADGE_2 = '#badge:badge_2'
    BADGE_2_DESCR = '#badge:badge_2_descr'
    BADGE_3 = '#badge:badge_3'
    BADGE_3_DESCR = '#badge:badge_3_descr'
    BADGE_4 = '#badge:badge_4'
    BADGE_4_DESCR = '#badge:badge_4_descr'
    BADGE_5 = '#badge:badge_5'
    BADGE_5_DESCR = '#badge:badge_5_descr'
    BADGE_6 = '#badge:badge_6'
    BADGE_6_DESCR = '#badge:badge_6_descr'
    BADGE_7 = '#badge:badge_7'
    BADGE_7_DESCR = '#badge:badge_7_descr'
    BADGE_8 = '#badge:badge_8'
    BADGE_8_DESCR = '#badge:badge_8_descr'
    BADGE_9 = '#badge:badge_9'
    BADGE_9_DESCR = '#badge:badge_9_descr'
    BADGE_NOTE = '#badge:badge_note'
    TITLETEXT = '#badge:titleText'
    DESCTEXT = '#badge:descText'
    BADGE_ENUM = (BADGE_0,
     BADGE_0_DESCR,
     BADGE_1,
     BADGE_1_DESCR,
     BADGE_2,
     BADGE_2_DESCR,
     BADGE_3,
     BADGE_3_DESCR,
     BADGE_4,
     BADGE_4_DESCR,
     BADGE_5,
     BADGE_5_DESCR,
     BADGE_6,
     BADGE_6_DESCR,
     BADGE_7,
     BADGE_7_DESCR,
     BADGE_8,
     BADGE_8_DESCR,
     BADGE_9,
     BADGE_9_DESCR,
     BADGE_NOTE)
    BADGE_ALL_DESCR_ENUM = (BADGE_0_DESCR,
     BADGE_1_DESCR,
     BADGE_2_DESCR,
     BADGE_3_DESCR,
     BADGE_4_DESCR,
     BADGE_5_DESCR,
     BADGE_6_DESCR,
     BADGE_7_DESCR,
     BADGE_8_DESCR,
     BADGE_9_DESCR)

    @classmethod
    def badgeName(cls, key0):
        outcome = '#badge:badge_{}'.format(key0)
        if outcome not in cls.BADGE_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def badgeDescriptor(cls, key0):
        outcome = '#badge:badge_{}_descr'.format(key0)
        if outcome not in cls.BADGE_ALL_DESCR_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome
