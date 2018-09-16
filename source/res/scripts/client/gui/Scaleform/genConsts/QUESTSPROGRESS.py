# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/genConsts/QUESTSPROGRESS.py
from debug_utils import LOG_WARNING

class QUESTSPROGRESS(object):
    C_183X63_OPERATION_1 = '183x63_operation_1'
    C_183X63_OPERATION_2 = '183x63_operation_2'
    C_183X63_OPERATION_3 = '183x63_operation_3'
    C_183X63_OPERATION_4 = '183x63_operation_4'
    C_183X63_OPERATION_5 = '183x63_operation_5'
    C_183X63_OPERATION_6 = '183x63_operation_6'
    C_183X63_OPERATION_7 = '183x63_operation_7'
    DONE = 'done'
    FAILED = 'failed'
    IN_PROGRESS = 'in_progress'
    LOCKED = 'locked'
    ORANGE_AT_SPG = 'orange_AT-SPG'
    ORANGE_HEAVY_TANK = 'orange_heavyTank'
    ORANGE_LIGHT_TANK = 'orange_lightTank'
    ORANGE_MEDIUM_TANK = 'orange_mediumTank'
    ORANGE_SPG = 'orange_SPG'
    QP_DOT = 'qp_dot'
    QUEST_DONE = 'quest_done'
    QUEST_DONE_PERFECTLY = 'quest_done_perfectly'
    QUEST_IN_PROGRESS = 'quest_in_progress'
    QUEST_NOT_AVAILABLE = 'quest_not_available'
    QUEST_ON_PAUSE = 'quest_on_pause'
    SILVER_AT_SPG = 'silver_AT-SPG'
    SILVER_HEAVY_TANK = 'silver_heavyTank'
    SILVER_LIGHT_TANK = 'silver_lightTank'
    SILVER_MEDIUM_TANK = 'silver_mediumTank'
    SILVER_SPG = 'silver_SPG'
    WARNING = 'warning'
    SILVER_ENUM = (SILVER_AT_SPG,
     SILVER_HEAVY_TANK,
     SILVER_LIGHT_TANK,
     SILVER_MEDIUM_TANK,
     SILVER_SPG)
    ORANGE_ENUM = (ORANGE_AT_SPG,
     ORANGE_HEAVY_TANK,
     ORANGE_LIGHT_TANK,
     ORANGE_MEDIUM_TANK,
     ORANGE_SPG)
    C_183X63_OPERATION_ENUM = (C_183X63_OPERATION_1,
     C_183X63_OPERATION_2,
     C_183X63_OPERATION_3,
     C_183X63_OPERATION_4,
     C_183X63_OPERATION_5,
     C_183X63_OPERATION_6,
     C_183X63_OPERATION_7)

    @classmethod
    def getQPSilverVehicleType(cls, vType):
        outcome = 'silver_{}'.format(vType)
        if outcome not in cls.SILVER_ENUM:
            LOG_WARNING('Class constant "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getQPOrangeVehicleType(cls, vType):
        outcome = 'orange_{}'.format(vType)
        if outcome not in cls.ORANGE_ENUM:
            LOG_WARNING('Class constant "{}" not found'.format(outcome))
            return None
        else:
            return outcome

    @classmethod
    def getOperationTrackingIcon(cls, operationID):
        outcome = '183x63_operation_{}'.format(operationID)
        if outcome not in cls.C_183X63_OPERATION_ENUM:
            LOG_WARNING('Class constant "{}" not found'.format(outcome))
            return None
        else:
            return outcome
