# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/event_nots.py
from Event import Event
from gui.battle_control.controllers.event_mark1.events_ctrl import STATES
from gui.Scaleform.daapi.view.meta.EventNotificationPanelMeta import EventNotificationPanelMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from helpers.i18n import makeString

class _BG_NAMES(object):
    POSITIVE = 'positiveBG'
    NEGATIVE = 'negativeBG'
    ATTENTION = 'attentionBG'
    REPAIR_ENEMY = 'repairEnemy'


class _ICONS(object):
    BOMB = 'bomb'
    MARK_MOVING = 'markMoving'
    REPAIR = 'repair'
    MARK_STOPPED = 'markStopped'


class AbstractEventNotificationView(EventNotificationPanelMeta):

    def __init__(self):
        super(AbstractEventNotificationView, self).__init__()
        self.onStateHidden = Event()

    def showState(self, state):
        raise NotImplementedError


class Mark1EventNotification(AbstractEventNotificationView):

    def __init__(self):
        super(Mark1EventNotification, self).__init__()

    def showState(self, state):
        self.as_showS(state)

    def onHideAnimationComplete(self, state):
        self.onStateHidden(state)

    def _populate(self):
        super(Mark1EventNotification, self)._populate()
        self.as_initS(self.__getStates())

    def _dispose(self):
        self.onStateHidden.clear()
        super(Mark1EventNotification, self)._dispose()

    @staticmethod
    def __getStates():
        return [{'state': STATES.NEW_BONUS_REPAIR_KIT_ATTACK,
          'bgName': _BG_NAMES.POSITIVE,
          'header': makeString(INGAME_GUI.MARK1_NOTIFICATION_REPAIR_ATTACK_HEADER),
          'body': makeString(INGAME_GUI.MARK1_NOTIFICATION_REPAIR_ATTACK_BODY),
          'icon': _ICONS.REPAIR},
         {'state': STATES.NEW_BONUS_BOMB_DEFENCE,
          'bgName': _BG_NAMES.POSITIVE,
          'header': makeString(INGAME_GUI.MARK1_NOTIFICATION_BOMB_DEFENCE_HEADER),
          'body': makeString(INGAME_GUI.MARK1_NOTIFICATION_BOMB_DEFENCE_BODY),
          'icon': _ICONS.BOMB},
         {'state': STATES.MARK1_STOPPED_BY_DESTRUCTION_ATTACK,
          'bgName': _BG_NAMES.NEGATIVE,
          'header': makeString(INGAME_GUI.MARK1_NOTIFICATION_MARKSTOPPEDATTACK_REPAIR_HEADER),
          'body': makeString(INGAME_GUI.MARK1_NOTIFICATION_MARKSTOPPEDATTACK_REPAIR_BODY),
          'icon': _ICONS.MARK_STOPPED},
         {'state': STATES.MARK1_STOPPED_BY_DESTRUCTION_DEFENCE,
          'bgName': _BG_NAMES.POSITIVE,
          'header': makeString(INGAME_GUI.MARK1_NOTIFICATION_MARKSTOPPEDDEFENCE_BOMB_HEADER),
          'body': makeString(INGAME_GUI.MARK1_NOTIFICATION_MARKSTOPPEDDEFENCE_BOMB_BODY),
          'icon': _ICONS.MARK_STOPPED},
         {'state': STATES.BOMB_CAPTURED_ATTACK,
          'bgName': _BG_NAMES.ATTENTION,
          'header': makeString(INGAME_GUI.MARK1_NOTIFICATION_ATTENTION_ATTACK_HEADER),
          'body': makeString(INGAME_GUI.MARK1_NOTIFICATION_ATTENTION_ATTACK_BODY),
          'icon': _ICONS.BOMB},
         {'state': STATES.MARK1_REPAIRED_ATTACK,
          'bgName': _BG_NAMES.POSITIVE,
          'header': makeString(INGAME_GUI.MARK1_NOTIFICATION_MARKREPAIRED_BOMB_ATTACK_HEADER),
          'body': makeString(INGAME_GUI.MARK1_NOTIFICATION_MARKREPAIRED_BOMB_ATTACK_BODY),
          'icon': _ICONS.MARK_MOVING},
         {'state': STATES.MARK1_REPAIRED_DEFENCE,
          'bgName': _BG_NAMES.NEGATIVE,
          'header': makeString(INGAME_GUI.MARK1_NOTIFICATION_MARKREPAIRED_BOMB_DEFENCE_HEADER),
          'body': makeString(INGAME_GUI.MARK1_NOTIFICATION_MARKREPAIRED_BOMB_DEFENCE_BODY),
          'icon': _ICONS.MARK_MOVING},
         {'state': STATES.REPAIR_KIT_CAPTURED_DEFENCE,
          'bgName': _BG_NAMES.ATTENTION,
          'header': makeString(INGAME_GUI.MARK1_NOTIFICATION_DEFENCE_REPAIR_HEADER),
          'body': makeString(INGAME_GUI.MARK1_NOTIFICATION_DEFENCE_REPAIR_BODY),
          'icon': _ICONS.REPAIR}]
