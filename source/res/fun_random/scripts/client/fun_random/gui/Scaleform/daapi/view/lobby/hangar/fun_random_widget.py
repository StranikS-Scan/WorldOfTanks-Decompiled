# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/fun_random_widget.py
from fun_random.gui.impl.lobby.feature.fun_random_hangar_widget_view import FunRandomHangarWidgetView
from gui.Scaleform.daapi.view.meta.FunRandomHangarWidgetMeta import FunRandomHangarWidgetMeta
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomHangarWidgetComponent(FunRandomHangarWidgetMeta):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def _makeInjectView(self):
        return FunRandomHangarWidgetView()

    def _populate(self):
        super(FunRandomHangarWidgetComponent, self)._populate()
        self.__funRandomCtrl.onGameModeStatusUpdated += self.__update
        self.__update()

    def _dispose(self):
        self.__funRandomCtrl.onGameModeStatusUpdated -= self.__update
        super(FunRandomHangarWidgetComponent, self)._dispose()

    def __update(self, *_):
        modifiersProvider = self.__funRandomCtrl.getModifiersDataProvider()
        modifiersCount = len(modifiersProvider.getDomains()) if modifiersProvider else 0
        self.as_setModifiersCountS(modifiersCount)
