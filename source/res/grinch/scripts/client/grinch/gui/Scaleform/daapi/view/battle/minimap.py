# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/minimap.py
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin

class GrinchMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(GrinchMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = GrinchArenaVehiclesPlugin
        return setup


class GrinchArenaVehiclesPlugin(ArenaVehiclesPlugin):

    def _setVehicleInfo(self, vehicleID, entry, vInfo, guiProps, isSpotted=False):
        vehicleType = vInfo.vehicleType
        classTag = vehicleType.classTag
        name = vehicleType.shortNameWithPrefix
        team = vInfo.team
        guiLabel = 'team_' + str(team)
        if classTag is not None:
            entry.setVehicleInfo(not guiProps.isFriend, guiLabel, classTag, vInfo.isAlive())
        animation = self._ArenaVehiclesPlugin__getSpottedAnimation(entry, isSpotted)
        if animation:
            self._ArenaVehiclesPlugin__playSpottedSound(entry)
        self._invoke(entry.getID(), 'setVehicleInfo', vehicleID, classTag, name, guiLabel, animation)
        return
