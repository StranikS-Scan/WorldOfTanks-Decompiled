# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/extension_utils.py
import importlib
from soft_exception import SoftException
from ExtensionsManager import g_extensionsManager
from constants import IS_CLIENT, IS_EDITOR
from debug_utils import LOG_CURRENT_EXCEPTION
from extension_rules import isExtXML, READ_METHOD
if IS_CLIENT or IS_EDITOR:
    import ResMgr as rmgr
else:
    from realm_utils import ResMgr as rmgr
    from realm_utils import getRealmFilePath
_ROOT_TAG = 'root'
_XML_NAMESPACE = ' xmlns:xmlref="http://bwt/xmlref"'
_MERGE_TAG = 'xmlref:merge'
_CONTENT_TAG = 'xmlref:content'
_INCLUDE_TAG = 'xmlref:include'
_cachedElements = set()

def importClass(classPath, defaultMod):
    modPath, _, className = classPath.rpartition('.')
    try:
        mod = importlib.import_module(modPath or defaultMod)
    except ImportError:
        LOG_CURRENT_EXCEPTION()
        return

    try:
        return getattr(mod, className)
    except AttributeError:
        LOG_CURRENT_EXCEPTION()
        return


class _MergeExtensionFile(object):

    @classmethod
    def makeMergeXMLString(cls, xmlPaths, isMergeRequired):
        if not xmlPaths:
            return ''
        genString = cls._openTag('{} {}'.format(_ROOT_TAG, _XML_NAMESPACE))
        if isMergeRequired:
            genString += cls._openTag(_MERGE_TAG)
        for path in xmlPaths:
            if isMergeRequired:
                genString += cls._openTag(_CONTENT_TAG)
            genString += cls._attributeTag(_INCLUDE_TAG, 'href', path)
            if isMergeRequired:
                genString += cls._closeTag(_CONTENT_TAG)

        if isMergeRequired:
            genString += cls._closeTag(_MERGE_TAG)
        genString += cls._closeTag(_ROOT_TAG)
        return genString

    @classmethod
    def openSection(cls, xmlPath, mergeFiles):
        xmlPaths = [ ext.path + xmlPath for ext in g_extensionsManager.activeExtensions if rmgr.isFile(ext.path + xmlPath) ]
        if not xmlPaths:
            return rmgr.openSection(xmlPath)
        if rmgr.isFile(xmlPath):
            xmlPaths = [xmlPath] + xmlPaths
        if not (IS_CLIENT or IS_EDITOR):
            xmlPaths = [ (getRealmFilePath(xmlPath) if rmgr.isFile(getRealmFilePath(xmlPath)) else xmlPath) for xmlPath in xmlPaths ]
        section = rmgr.DataSection('root')
        section.createSectionFromString(cls.makeMergeXMLString(xmlPaths, mergeFiles))
        section = section.child(0)
        return section

    @classmethod
    def _openTag(cls, tag):
        return '<' + tag + '>\n'

    @classmethod
    def _closeTag(cls, tag):
        return '</' + tag + '>\n'

    @classmethod
    def _attributeTag(cls, tag, attrName, attrValue):
        return '<{} {}="{}"/>\n'.format(tag, attrName, attrValue)


def mergeSection(xmlPath, mergeFiles):
    return _MergeExtensionFile.openSection(xmlPath, mergeFiles)


def makeMergeXMLString(xmlPaths, isMergeRequired):
    return _MergeExtensionFile.makeMergeXMLString(xmlPaths, isMergeRequired)


class ResMgr(object):

    class __metaclass__(type):

        def __getattr__(self, item):
            return getattr(rmgr, item) if IS_CLIENT else getattr(self if item in ('openSection', 'addToCache') else rmgr, item)

    @staticmethod
    def openSection(filepath, createIfMissing=False):
        readExtXML, readMethod = isExtXML(filepath)
        isXMLCached = rmgr.resolveToAbsolutePath(filepath) in _cachedElements
        return rmgr.openSection(filepath, createIfMissing) if isXMLCached or not readExtXML else mergeSection(filepath, readMethod == READ_METHOD.MERGE)

    @staticmethod
    def addToCache(ftPath, xml):
        extensions = g_extensionsManager.activeExtensions
        extPaths = [ ext.path + ftPath for ext in extensions if rmgr.isFile(ext.path + ftPath) ]
        corePath = [ftPath] if rmgr.isFile(ftPath) else []
        xmlPaths = corePath + extPaths
        if not xmlPaths:
            resourcePath = rmgr.resolveToAbsolutePath(ftPath)
            _cachedElements.add(resourcePath)
            return rmgr.addToCache(resourcePath, xml)
        mergeRequired, _ = isExtXML(ftPath)
        if len(xmlPaths) > 1 and not mergeRequired:
            raise SoftException('Multiple standalone resources for one relative path found: %s', ftPath)
        resourcePath = rmgr.resolveToAbsolutePath(next(iter(xmlPaths)))
        _cachedElements.add(resourcePath)
        return rmgr.addToCache(resourcePath, xml)
