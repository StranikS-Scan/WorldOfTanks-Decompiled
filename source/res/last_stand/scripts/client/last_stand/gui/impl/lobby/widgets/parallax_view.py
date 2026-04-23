# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/parallax_view.py
from __future__ import absolute_import
import json
import logging
import typing
import ResMgr
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.shared.utils.graphics import isLowPreset
from helpers import dependency
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.parallax_view_model import ParallaxViewModel
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_story_point_controller import ILSStoryPointController
if typing.TYPE_CHECKING:
    from last_stand.gui.impl.gen.view_models.views.lobby.widgets.parallax_model import ParallaxModel
_logger = logging.getLogger(__name__)
PATH_TO_CONFIGS = 'last_stand/gui/parallax/configs.json'
PARALLAX_DEFAULT_SCALE = 1

class ParallaxView(ViewComponent[ParallaxViewModel]):
    lsCtrl = dependency.descriptor(ILSController)
    lsStoryPointCtrl = dependency.descriptor(ILSStoryPointController)

    def __init__(self):
        super(ParallaxView, self).__init__(R.aliases.last_stand.shared.Parallax(), ParallaxViewModel)
        self._parallaxConfig = _toJson(_readSection(PATH_TO_CONFIGS))
        self._currentSlideID = self.lsStoryPointCtrl.FIRST_STORY_POINT_INDEX

    @property
    def viewModel(self):
        return super(ParallaxView, self).getViewModel()

    def _subscribe(self):
        super(ParallaxView, self)._subscribe()
        self.viewModel.onSlide += self.__onSlide

    def _unsubscribe(self):
        self.viewModel.onSlide -= self.__onSlide
        super(ParallaxView, self)._unsubscribe()

    def __onSlide(self, args):
        self._currentSlideID = int(args.get('slideIndex', self.lsStoryPointCtrl.FIRST_STORY_POINT_INDEX))
        self.__readParallaxConfig(self._currentSlideID)

    def __readParallaxConfig(self, currentSlideID):
        with self.viewModel.transaction() as tx:
            if not self.lsCtrl.isParallaxEnabled():
                tx.setIsParallaxEnabled(False)
                _logger.info('last_stand_config.xml parallaxEnabled is False')
                return
            if isLowPreset():
                tx.setIsParallaxEnabled(False)
                _logger.info('Low graphics settings')
                return
            slideParallaxConfig = self._parallaxConfig.get(str(currentSlideID))
            if slideParallaxConfig is None:
                tx.setIsParallaxEnabled(False)
                _logger.info('cannot find config for %s', currentSlideID)
                return
            parallaxStructure = _readSection(slideParallaxConfig.get('structurePath', ''))
            if parallaxStructure == '':
                tx.setIsParallaxEnabled(False)
                _logger.info('cannot find parallax structure:%s', slideParallaxConfig.get('structurePath'))
                return
            tx.setIsParallaxEnabled(True)
            chunks = _getChunks(slideParallaxConfig.get('chunksCount', 0), slideParallaxConfig.get('chunkName', ''), slideParallaxConfig.get('chunksDataDirPath', ''))
            modelParallax = tx.parallax
            modelParallax.setSlideId(currentSlideID)
            modelParallax.setPerspective(slideParallaxConfig.get('perspective', 0))
            modelParallax.setPerspectiveOriginX(slideParallaxConfig.get('perspectiveOriginX', 0))
            modelParallax.setPerspectiveOriginY(slideParallaxConfig.get('perspectiveOriginY', 0))
            modelParallax.setWrapperWidth(slideParallaxConfig.get('wrapperWidth', 0))
            modelParallax.setWrapperHeight(slideParallaxConfig.get('wrapperHeight', 0))
            modelParallax.setOverallScale(slideParallaxConfig.get('overallScale', PARALLAX_DEFAULT_SCALE))
            modelParallax.setXTilt(slideParallaxConfig.get('xTilt', 0.0))
            modelParallax.setXTiltRange(slideParallaxConfig.get('xTiltRange', 0.0))
            modelParallax.setYTilt(slideParallaxConfig.get('yTilt', 0.0))
            modelParallax.setYTiltRange(slideParallaxConfig.get('yTiltRange', 0.0))
            modelParallax.setXSlide(slideParallaxConfig.get('xSlide', 0.0))
            modelParallax.setYSlide(slideParallaxConfig.get('ySlide', 0.0))
            modelParallax.setParallaxStructure(parallaxStructure)
            modelParallax.setAtlas(chunks)
            modelParallax.setChunkFileExt(slideParallaxConfig.get('chunkFileExt', ''))
            modelParallax.setChunksAssetsPath(slideParallaxConfig.get('chunksAssetsPath', ''))
        return


def _readSection(path):
    if path == '':
        return ''
    else:
        section = ResMgr.openSection(path)
        ResMgr.purge(path)
        return section.asString if section is not None else ''


def _toJson(inputData):
    try:
        jsonData = json.loads(inputData)
    except Exception as e:
        _logger.error('%s', e)
        return None

    if not jsonData:
        _logger.error('Empty jsonData received')
        return None
    else:
        return jsonData


def _getChunks(count, name, path):
    allChunks = {}
    for i in range(count):
        chunkPath = '{0}{1}{2}.json'.format(path, name, str(i))
        chunk = _toJson(_readSection(chunkPath))
        if chunk is not None:
            allChunks.update(chunk)
        _logger.error('Chunk of parallax atlas is None')

    return json.dumps(allChunks)
