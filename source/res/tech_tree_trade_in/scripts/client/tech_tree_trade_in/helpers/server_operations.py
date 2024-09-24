# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/helpers/server_operations.py
from tech_tree_trade_in_common.tech_tree_trade_in_constants import TTT_OP_TYPES
from items import ITEM_TYPES

def processOperationsLog(opLogData):
    operations = {}
    for opLog in opLogData:
        opLogType = opLog['tech_tree_trade_in_op']
        vehCD = opLog['vehicle_type_cd']
        if opLogType in (TTT_OP_TYPES.MOVE_XP, TTT_OP_TYPES.POST_PROGRESSION):
            catDict = operations.setdefault(vehCD, {}).setdefault(opLogType, {})
            catDict['amount'] = opLog['value_amount']
            catDict['intCD'] = opLog['item_type_cd']
        if opLogType in (TTT_OP_TYPES.MOVE_EQUIPMENT, TTT_OP_TYPES.MOVE_CONSUMABLES):
            catList = operations.setdefault(vehCD, {}).setdefault(opLogType, [])
            catList.append(opLog['item_type_cd'])
        if opLogType in (TTT_OP_TYPES.MOVE_TANKMAN, TTT_OP_TYPES.TURN_CREW) and opLog['item_cd']:
            catList = operations.setdefault(vehCD, {}).setdefault(opLogType, [])
            catList.append(opLog['item_cd'])
        if opLogType == TTT_OP_TYPES.MOVE_CUSTOMIZATION:
            catList = operations.setdefault(vehCD, {}).setdefault(opLogType, [])
            catList.append((opLog['item_type_cd'], opLog['value_amount']))
        if opLogType == TTT_OP_TYPES.MOVE_SHELLS:
            catList = operations.setdefault(vehCD, {}).setdefault(opLogType, [])
            catList.append((opLog['item_type_cd'], opLog['item_number']))
        if opLogType == TTT_OP_TYPES.CREDITS_COMPENSATION:
            if opLog['value_amount'] > 0:
                operations.setdefault(vehCD, {})[opLogType] = opLog['value_amount']
        if opLogType in (TTT_OP_TYPES.REMOVAL,
         TTT_OP_TYPES.ACCRUAL,
         TTT_OP_TYPES.DERESEARCH,
         TTT_OP_TYPES.RESEARCH) and opLog['item_type_id'] == ITEM_TYPES.vehicle:
            operations.setdefault(vehCD, {})[opLogType] = True
        if opLogType == TTT_OP_TYPES.FEE_WITHDRAW:
            catDict = operations.setdefault(vehCD, {}).setdefault(opLogType, {})
            catDict.setdefault(opLog['item_type_id'], {})[opLog['item_type_cd']] = opLog['value_amount']

    return operations
