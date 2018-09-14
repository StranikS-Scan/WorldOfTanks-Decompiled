# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AbstractRallyViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class AbstractRallyViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_setPyAliasS(self, alias):
        """
        :param alias:
        :return :
        """
        return self.flashObject.as_setPyAlias(alias) if self._isDAAPIInited() else None

    def as_getPyAliasS(self):
        """
        :return String:
        """
        return self.flashObject.as_getPyAlias() if self._isDAAPIInited() else None
