# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/map_info_tip.py
from gui.Scaleform.daapi.view.meta.MapInfoTipMeta import MapInfoTipMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class MapInfoTip(MapInfoTipMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(MapInfoTip, self)._populate()
        self.as_setEnabledS(self.__sessionProvider.arenaVisitor.extra.isMapsInDevelopmentEnabled())
