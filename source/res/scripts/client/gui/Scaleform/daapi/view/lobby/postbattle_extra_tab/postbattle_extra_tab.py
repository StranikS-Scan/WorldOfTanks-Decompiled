# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/postbattle_extra_tab/postbattle_extra_tab.py
from frameworks.wulf import ViewFlags
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.impl.pub import ViewImpl
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.daapi.view.meta.PostbattleExtraTabMeta import PostbattleExtraTabMeta

class PostbattleExtraTab(InjectComponentAdaptor, PostbattleExtraTabMeta):
    __injectionView = None

    @classmethod
    def overrideInjectionView(cls, view):
        if not issubclass(view, PostbattleExtraTabView):
            LOG_ERROR('Parameter is not a subclass of ViewImpl', view)
            return
        cls.__injectionView = view

    @classmethod
    def deleteInjectionView(cls):
        cls.__injectionView = None
        return

    def _makeInjectView(self):
        if self.__injectionView:
            return self.__injectionView(flags=ViewFlags.VIEW)
        LOG_WARNING('Nothing to inject to PostbattleExtraTab.')

    def updateQuestsInfo(self, arenaUniqueID):
        view = self.getInjectView()
        if view:
            view.onArenaInfoUpdated(arenaUniqueID)

    @classmethod
    def isInjectionView(cls, view):
        return cls.__injectionView == view

    @classmethod
    def hasInjectionView(cls):
        return bool(cls.__injectionView)


class PostbattleExtraTabView(ViewImpl):

    def onArenaInfoUpdated(self, arenaUniqueID):
        raise NotImplementedError
