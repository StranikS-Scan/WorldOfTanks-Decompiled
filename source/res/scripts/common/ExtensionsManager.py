# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ExtensionsManager.py
import BigWorld
import ResMgr
from collections import namedtuple
_EXTENSIONS_RELATIVE_DIR = '../wot_ext'
_EXTENSIONS_ABS_DIR = 'res/wot_ext'
_EXTENSION_PATH_TEMPLATE = '{root}/{extension}/{path}'
_EXTENSION_IMPORT_PATHS = ['',
 'scripts',
 'scripts/base',
 'scripts/server_common',
 'scripts/common',
 'scripts/common/Lib']

def makeExtensionPath(extension, path):
    return _EXTENSION_PATH_TEMPLATE.format(root=_EXTENSIONS_RELATIVE_DIR, extension=extension, path=path)


Extension = namedtuple('Extension', ('path', 'name', 'isEnabled', 'dirName', 'personality', 'editorPersonality'))

class ExtensionsManager(object):
    __slots__ = ('_extensions',)

    def __init__(self):
        super(ExtensionsManager, self).__init__()
        self._extensions = self._readExtensions()

    @property
    def extensions(self):
        return self._extensions.values()

    @property
    def activeExtensions(self):
        return [ extension for extension in self.extensions if extension.isEnabled ]

    @property
    def activePaths(self):
        return [ '/'.join((_EXTENSIONS_ABS_DIR, extension.dirName, relativePath)) for extension in self.activeExtensions for relativePath in _EXTENSION_IMPORT_PATHS ]

    def hasExtensions(self):
        return bool(self._extensions)

    def _readExtensions(self):
        extensions = {}
        for root in self._getExtensionsDirList():
            extension = self._readExtension(root)
            if extension:
                extensions[extension.name] = extension

        return extensions

    @staticmethod
    def _readExtension(root):
        section = ResMgr.openSection(root + '/extension.xml')
        return None if not section else Extension(root + '/', section.readString('FeatureName'), section.readBool('IsEnabled'), root.split('/')[-1], section.readString('Personality'), section.readString('EditorPersonality'))

    @staticmethod
    def _getExtensionsDirList():
        if getattr(BigWorld, 'getExtensionsDirList', None):
            return BigWorld.getExtensionsDirList()
        else:
            import os
            return [ '{}/{}'.format(_EXTENSIONS_RELATIVE_DIR, item) for item in os.listdir(ResMgr.resolveToAbsolutePath(_EXTENSIONS_RELATIVE_DIR)) if os.path.isdir(ResMgr.resolveToAbsolutePath(os.path.join(_EXTENSIONS_RELATIVE_DIR, item))) ]


g_extensionsManager = ExtensionsManager()
