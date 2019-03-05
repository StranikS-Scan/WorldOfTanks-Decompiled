# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/blueprints/BlueprintTypes.py
from wotdecorators import singleton

@singleton
class BlueprintTypes(object):
    NONE = 0
    VEHICLE = 1
    NATIONAL = 2
    INTELLIGENCE_DATA = 3
    UNIVERSAL = (NATIONAL, INTELLIGENCE_DATA)
    ALL = (NATIONAL, VEHICLE, INTELLIGENCE_DATA)
