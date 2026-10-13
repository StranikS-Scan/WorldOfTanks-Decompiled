# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common/__init__.py
import constants
from portal_common.portal_constants import PORTAL_GAME_PARAMS_KEY

def injectConsts(personality):
    constants.INBATTLE_CONFIGS.append(PORTAL_GAME_PARAMS_KEY)
