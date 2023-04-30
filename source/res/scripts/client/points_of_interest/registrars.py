# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/registrars.py
import CGF
from cgf_script.managers_registrator import Rule, registerManager, registerRule
from points_of_interest.managers import PoiStateManager, PoiViewStateManager, PoiSoundManager

@registerRule
class PointsOfInterestRule(Rule):
    category = 'Points Of Interest'
    domain = CGF.DomainOption.DomainAll

    @registerManager(PoiStateManager)
    def registerPoiStateManager(self):
        return None

    @registerManager(PoiViewStateManager)
    def registerPoiViewStateManager(self):
        return None

    @registerManager(PoiSoundManager)
    def registerPoiSoundManager(self):
        return None
