# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/common/tech_tree_trade_in_common/tech_tree_trade_in_constants.py
TECH_TREE_TRADE_IN_CONFIG_PATH = 'tech_tree_trade_in/scripts/server_xml/tech_tree_trade_in_config.xml'
TRADING_BRANCHES_CONFIG_PATH = 'tech_tree_trade_in/scripts/item_defs/vehicles/common/tech_tree_trade_in_branches.xml'
TECH_TREE_TRADE_IN_CONFIG = 'tech_tree_trade_in_config'
MIN_TRADE_LEVEL = 6
MAX_TRADE_LEVEL = 10
BRANCH_TO_TRADE_IDX = 0
BRANCH_TO_RECEIVE_IDX = 100
EVENT_NAME = 'tech_tree_trade_in_event'

class TTT_OP_TYPES(object):
    FEE_WITHDRAW = 100
    DERESEARCH = 101
    RESEARCH = 102
    REMOVAL = 103
    ACCRUAL = 104
    CREDITS_COMPENSATION = 105
    TURN_CREW = 106
    MOVE_XP = 107
    POST_PROGRESSION = 108
    MOVE_EQUIPMENT = 109
    MOVE_TANKMAN = 110
    MOVE_CREW_SKIN = 111
    MOVE_CONSUMABLES = 112
    MOVE_SHELLS = 113
    MOVE_CUSTOMIZATION = 114
    VEHICLE_BLUEPRINTS = 115
