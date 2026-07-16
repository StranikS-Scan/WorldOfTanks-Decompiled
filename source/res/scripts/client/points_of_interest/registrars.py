# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/points_of_interest/registrars.py
import CGF
from cgf_script.registration import registerModule
from points_of_interest.managers import PoiStateCreateSystem, PoiStateUpdateSystem, PoiViewStateSystem, PoiSoundSystem
_UPDATE_PERIOD = 0.2

@registerModule
class PointsOfInterestModule(object):
    name = 'POI Module'
    desc = 'Stuff for points of interest'
    group = 'Battle'
    systems = [CGF.RegisterSystem(PoiStateCreateSystem, domain=CGF.Domain.Client),
     CGF.RegisterSystem(PoiViewStateSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,), updatePeriod=_UPDATE_PERIOD, perTickUpdate=True),
     CGF.RegisterSystem(PoiSoundSystem, domain=CGF.Domain.Client, updatePeriod=_UPDATE_PERIOD),
     CGF.RegisterSystem(PoiStateUpdateSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem, PoiStateCreateSystem, PoiSoundSystem), updatePeriod=_UPDATE_PERIOD)]
    components = []
