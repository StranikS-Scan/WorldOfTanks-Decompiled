# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/genConsts/PILLBOX_SIEGE_WIDGET_CONST.py


class PILLBOX_SIEGE_WIDGET_CONST(object):
    EMPTY = 'empty'
    IDLE = 'idle'
    SIEDGE = 'siege'
    PILLBOX = 'pillbox'
    IDLE_TO_SIEDGE = 'idle_to_siege'
    IDLE_TO_PILLBOX = 'idle_to_pillbox'
    SIEDGE_TO_IDLE = 'siege_to_idle'
    SIEDGE_TO_PILLBOX = 'siege_to_pillbox'
    PILLBOX_TO_IDLE = 'pillbox_to_idle'
    PILLBOX_TO_SIEDGE = 'pillbox_to_siege'
    PILLBOX_SIEGE_MECHANICS_WIDGET_STATE = [IDLE,
     SIEDGE,
     PILLBOX,
     IDLE_TO_SIEDGE,
     IDLE_TO_PILLBOX,
     SIEDGE_TO_IDLE,
     SIEDGE_TO_PILLBOX,
     PILLBOX_TO_IDLE,
     PILLBOX_TO_SIEDGE]
    PILLBOX_SIEGE_TRANSITIONS_STATE = [IDLE_TO_SIEDGE,
     IDLE_TO_PILLBOX,
     SIEDGE_TO_IDLE,
     SIEDGE_TO_PILLBOX,
     PILLBOX_TO_IDLE,
     PILLBOX_TO_SIEDGE]
    CONDITION_NORMAL = 'normal'
    CONDITION_WARNING = 'warning'
    CONDITION_CRITICAL = 'critical'
    PILLBOX_SIEGE_MECHANICS_WIDGET_CONDITION = [CONDITION_NORMAL, CONDITION_WARNING, CONDITION_CRITICAL]
    DEVICE_STATE_CRITICAL = 'critical'
    DEVICE_STATE_DESTROYED = 'destroyed'
    DEVICE_NONE = 'None'
    DEVICE_CHASSIS = 'chassis'
    DEVICE_ENGINE = 'engine'
    DEVICES = [DEVICE_NONE, DEVICE_CHASSIS, DEVICE_ENGINE]
