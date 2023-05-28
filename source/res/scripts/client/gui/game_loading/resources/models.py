# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/models.py
from typing import Optional, Union, TYPE_CHECKING
from gui.game_loading.resources.consts import InfoStyles
if TYPE_CHECKING:
    from gui.game_loading.resources.consts import ImageVfxs

class BaseResourceModel(object):
    __slots__ = ('minShowTimeSec',)

    def __init__(self, minShowTimeSec):
        self.minShowTimeSec = max(minShowTimeSec, 0)


class LocalImageModel(BaseResourceModel):
    __slots__ = ('imageRelativePath', 'vfx', 'localizationText', 'descriptionText', 'transition')

    def __init__(self, imageRelativePath, vfx=None, localizationText=None, descriptionText=None, minShowTimeSec=0, transition=0):
        super(LocalImageModel, self).__init__(minShowTimeSec=minShowTimeSec)
        self.imageRelativePath = imageRelativePath
        self.vfx = vfx
        self.localizationText = localizationText
        self.descriptionText = descriptionText
        self.transition = transition

    def __repr__(self):
        string = '<{}(image={}, vfx={}, localizationExist={}, descriptionExist={}, minShowTimeSec={}, transition={})>'
        return string.format(self.__class__.__name__, self.imageRelativePath, self.vfx, bool(self.localizationText), bool(self.descriptionText), self.minShowTimeSec, self.transition)


class LogoModel(BaseResourceModel):
    __slots__ = ('type', 'showCopyright', 'showVersion', 'transition', 'info', 'infoStyle')

    def __init__(self, logoType, minShowTimeSec=0, showCopyright=True, showVersion=True, transition=0, info='', infoStyle=InfoStyles.DEFAULT):
        super(LogoModel, self).__init__(minShowTimeSec=minShowTimeSec)
        self.type = logoType
        self.showCopyright = showCopyright
        self.showVersion = showVersion
        self.transition = transition
        self.info = info
        self.infoStyle = infoStyle

    def __repr__(self):
        return '<LogoModel(type={}, minShowTimeSec={}, copyright={}, version={}, transition={}, info={}, infoStyle={})>'.format(self.type, self.minShowTimeSec, self.showCopyright, self.showVersion, self.transition, self.info, self.infoStyle)


class StatusTextModel(BaseResourceModel):
    __slots__ = ('text',)

    def __init__(self, text, minShowTimeSec=0):
        super(StatusTextModel, self).__init__(minShowTimeSec=minShowTimeSec)
        self.text = text

    def __repr__(self):
        return '<StatusTextModel(text={}, minShowTimeSec={})>'.format(self.text, self.minShowTimeSec)
