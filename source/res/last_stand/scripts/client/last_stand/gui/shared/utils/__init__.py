# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shared/utils/__init__.py
import BigWorld

def findMarkerEntity():
    return [ e for e in BigWorld.entities.valuesOfType('EmptyEntity') if any((c.__class__.__name__ == 'EntityMarkerComponent' for c in e.dynamicComponents.itervalues())) ]
