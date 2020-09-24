# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/items_manager.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.managers.containers import ExternalCriteria
from gui.app_loader import sf_lobby
from tutorial.logger import LOG_WARNING

class AttributeCriteria(ExternalCriteria):

    def __init__(self, dottedPath, value):
        super(AttributeCriteria, self).__init__((dottedPath.split('.'), value))

    def find(self, name, obj):
        path, value = self._criteria
        return self.__getValue(obj, path) == value

    def __getValue(self, popUp, path):
        nextAttr = popUp
        for attr in path:
            nextAttr = getattr(nextAttr, attr, None)

        return nextAttr


class ItemsManager(object):

    @sf_lobby
    def app(self):
        return None

    def findTargetByCriteria(self, targetPath, valuePath, value):
        result = None
        if targetPath == WindowLayer.TOP_WINDOW:
            result = self.__findDialog(valuePath, value)
        else:
            LOG_WARNING('Dialogs supported only')
        return result

    def __findDialog(self, path, value):
        result = None
        view = self.app.containerManager.getView(WindowLayer.TOP_WINDOW, criteria=AttributeCriteria(path, value))
        if view is not None:
            result = (WindowLayer.TOP_WINDOW, view.uniqueName)
        return result
