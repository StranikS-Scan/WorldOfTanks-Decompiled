# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/statuses/constants.py
import enum
DEFAULT_CONTEXT = '<default_ctx>'

@enum.unique
class StatusTypes(enum.IntEnum):
    UNDEFINED = 0
    ADD_NEEDED = 1
    ADDED = 2
    CONFIRMATION_SENT = 3
    CONFIRMED = 4
    PROCESSING = 5
