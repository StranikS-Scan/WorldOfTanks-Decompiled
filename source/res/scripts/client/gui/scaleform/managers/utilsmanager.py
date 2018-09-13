# Embedded file name: scripts/client/gui/Scaleform/managers/UtilsManager.py
import string
from helpers import i18n
import nations
import BigWorld
from gui import GUI_NATIONS
from gui.shared import utils
from gui.Scaleform.framework.entities.abstract.UtilsManagerMeta import UtilsManagerMeta

class UtilsManager(UtilsManagerMeta):

    def getGUINations(self):
        return GUI_NATIONS

    def getNationNames(self):
        return nations.NAMES

    def getNationIndices(self):
        return nations.INDICES

    def changeStringCasing(self, s, isUpper, _):
        return utils.changeStringCasing(str(s).decode('utf-8'), isUpper)

    def getAbsoluteUrl(self, value):
        return string.replace(value, '../', 'img://gui/')

    def getHtmlIconText(self, properties):
        template = "<img src='{0}' width='{1}' height='{2}' vspace='{3}' hspace='{4}'/>"
        absoluteUrl = self.getAbsoluteUrl(properties.imageAlias)
        return template.format(absoluteUrl, properties.width, properties.height, properties.vSpace, properties.hSpace)


class ImageUrlProperties(object):

    def __init__(self, imageAlias, width = 16, height = 16, vSpace = -4, hSpace = 0):
        super(ImageUrlProperties, self).__init__()
        self.imageAlias = imageAlias
        self.width = width
        self.height = height
        self.vSpace = vSpace
        self.hSpace = hSpace
