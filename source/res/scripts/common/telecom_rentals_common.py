# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/telecom_rentals_common.py
from enum import IntEnum
RENT_TOKEN_NAME = 'telecom_rent_token'
PARTNERSHIP_TOKEN_NAME = 'telecom_partnership_token'
PARTNERSHIP_BLOCKED_TOKEN_NAME = 'telecom_partnership_blocked_token'
ROSTER_EXPIRATION_TOKEN_NAME = 'telecom_roster_expiration_token'
TELECOM_RENTALS_CONFIG = 'telecom_rentals_config'
TELECOM_RENTALS_RENT_KEY = 'telecom'

class PartnershipState(IntEnum):
    NO_PARTNERSHIP = 0
    ACTIVE_PARTNERSHIP = 1
    BLOCKED_PARTNERSHIP = 2
