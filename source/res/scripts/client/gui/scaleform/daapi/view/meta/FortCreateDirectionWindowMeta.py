# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCreateDirectionWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortCreateDirectionWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def openNewDirection(self):
        """
        :return :
        """
        self._printOverrideError('openNewDirection')

    def closeDirection(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('closeDirection')

    def as_setDescriptionS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setDescription(value) if self._isDAAPIInited() else None

    def as_setupButtonS(self, enabled, visible, tooltip):
        """
        :param enabled:
        :param visible:
        :param tooltip:
        :return :
        """
        return self.flashObject.as_setupButton(enabled, visible, tooltip) if self._isDAAPIInited() else None

    def as_setDirectionsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setDirections(data) if self._isDAAPIInited() else None
