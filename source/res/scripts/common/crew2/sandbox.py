# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/sandbox.py
from constants import IS_CREW_SANDBOX

class SANDBOX_CONSTANTS(object):
    LEVEL_RESTRICTION_ENABLED = IS_CREW_SANDBOX and True
    MIN_LEVEL = 6
    NO_TEST_STATE = 'notParticipatingInTest'
    JOIN_ERROR_MSG = 'wrong level for sandbox'
    HIDE_PREMSHOP = IS_CREW_SANDBOX and True
    SHOP_PLACEHOLDER_ON = IS_CREW_SANDBOX and True
    DISABLE_PERSONAL_MISSIONS = IS_CREW_SANDBOX and True
