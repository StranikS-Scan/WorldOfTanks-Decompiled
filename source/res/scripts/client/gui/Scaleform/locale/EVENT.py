# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/locale/EVENT.py
from debug_utils import LOG_WARNING

class EVENT(object):
    PUNISHMENTWINDOW_REASON_EVENT_DESERTER = '#event:punishmentWindow/reason/event_deserter'
    PUNISHMENTWINDOW_REASON_EVENT_AFK = '#event:punishmentWindow/reason/event_afk'
    BATTLEHINTS_TESTMESSAGE = '#event:battleHints/testMessage'
    BATTLEHINTS_TESTMESSAGEWITHPARAMS = '#event:battleHints/testMessageWithParams'
    CRAFTMACHINE_TITLE = '#event:craftMachine/title'
    CRAFTMACHINE_SUBTITLE = '#event:craftMachine/subTitle'
    CRAFTMACHINE_ENDDATETEXT = '#event:craftMachine/endDateText'
    DAILYREWARD_TEXT = '#event:dailyReward/text'
    DAILYREWARD_BUTTON_READY = '#event:dailyReward/button/ready'
    DAILYREWARD_BUTTON_DETAILS = '#event:dailyReward/button/details'
    GLOBALPROGRESSION_LABEL = '#event:globalProgression/label'
    ALL_ENUM = (PUNISHMENTWINDOW_REASON_EVENT_DESERTER,
     PUNISHMENTWINDOW_REASON_EVENT_AFK,
     BATTLEHINTS_TESTMESSAGE,
     BATTLEHINTS_TESTMESSAGEWITHPARAMS,
     CRAFTMACHINE_TITLE,
     CRAFTMACHINE_SUBTITLE,
     CRAFTMACHINE_ENDDATETEXT,
     DAILYREWARD_TEXT,
     DAILYREWARD_BUTTON_READY,
     DAILYREWARD_BUTTON_DETAILS,
     GLOBALPROGRESSION_LABEL)

    @classmethod
    def all(cls, key0):
        outcome = '#event:{}'.format(key0)
        if outcome not in cls.ALL_ENUM:
            LOG_WARNING('Localization key "{}" not found'.format(outcome))
            return None
        else:
            return outcome
