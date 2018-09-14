# Embedded file name: scripts/client/tutorial/gui/Scaleform/items_manager.py
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import ExternalCriteria
from gui.app_loader.decorators import sf_lobby
from tutorial import LOG_WARNING

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

    def __init__(self):
        super(ItemsManager, self).__init__()

    @sf_lobby
    def app(self):
        return None

    def findTargetByCriteria(self, targetPath, valuePath, value):
        result = None
        if targetPath == ViewTypes.TOP_WINDOW:
            result = self.__findDialog(valuePath, value)
        else:
            LOG_WARNING('Dialogs supported only')
        return result

    def __findDialog(self, path, value):
        result = None
        view = self.app.containerManager.getView(ViewTypes.TOP_WINDOW, criteria=AttributeCriteria(path, value))
        if view is not None:
            result = (ViewTypes.TOP_WINDOW, view.uniqueName)
        return result
