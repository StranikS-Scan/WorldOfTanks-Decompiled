# Embedded file name: scripts/client/tutorial/gui/commands.py
import types
from tutorial.control import g_tutorialWeaver
from tutorial.logger import LOG_ERROR, LOG_CURRENT_EXCEPTION

class GUICommand(object):

    def invoke(self, gui, cmdData):
        pass


class _PyDummyMethod(GUICommand):

    def __init__(self):
        super(_PyDummyMethod, self).__init__()

    def invoke(self, ui, cmdData):
        pathList = cmdData.name.split('.')
        method = pathList.pop()
        clazz = pathList.pop()
        g_tutorialWeaver.weave('.'.join(pathList), clazz, '^{0:>s}$'.format(method), avoid=True)


class _PyInvokeMethod(GUICommand):

    def _py_searchMethod(self, gui, cmdData):
        path = cmdData.name.split('.')
        ns = gui
        method = gui
        for attr in path:
            ns = method
            method = getattr(ns, attr, None)
            if method is None:
                break

        if type(method) not in [types.MethodType, types.FunctionType]:
            method = None
        return (ns, method)

    def invoke(self, ui, cmdData):
        ns, method = self._py_searchMethod(ui, cmdData)
        if method is not None and callable(method):
            try:
                method(*cmdData.args[:])
            except Exception:
                LOG_CURRENT_EXCEPTION()

        else:
            LOG_ERROR('GUI method not found', ui, cmdData)
        return


class _PyNoGuiInvokeMethod(GUICommand):

    def invoke(self, _, cmdData):
        pathList = cmdData.name.split('.')
        methodName = pathList.pop()
        path = '.'.join(pathList)
        imported = __import__(path, globals(), locals(), [methodName])
        method = getattr(imported, methodName, None)
        if method is not None and callable(method):
            method(*cmdData.args[:])
        else:
            LOG_ERROR('GUI method not found', cmdData)
        return


class GUICommandsFactory(object):

    def __init__(self, typeMap = None):
        super(GUICommandsFactory, self).__init__()
        self.__typeMap = {'python-invoke': _PyInvokeMethod,
         'python-dummy': _PyDummyMethod,
         'invoke-method': _PyNoGuiInvokeMethod}
        if typeMap is not None:
            self.__typeMap.update(typeMap)
        return

    def _factory(self, cmdType):
        clazz = self.__typeMap.get(cmdType)
        if clazz is None:
            LOG_ERROR('Unknown type for GUI command', cmdType)
        return clazz()

    def invoke(self, root, data):
        command = self._factory(data.type)
        if command is not None:
            command.invoke(root, data)
        return


__all__ = ['GUICommand', 'GUICommandsFactory']
