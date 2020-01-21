# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/arenas/__init__.py
import ArenaType
from gui.impl import backport
from gui.impl.gen import R
from web.web_client_api import w2c, w2capi, Field, W2CSchema
INVALID_DYN_ATTR = -1

class _ArenaInfoSchema(W2CSchema):
    arena_id = Field(required=True, type=int)


class _ArenasInfoSchema(W2CSchema):
    arena_ids = Field(type=list, default=[])


@w2capi(name='arenas', key='action')
class ArenasWebApi(object):

    @w2c(_ArenaInfoSchema, 'arena_info')
    def arenaInfo(self, cmd):
        arenaType = ArenaType.g_cache.get(cmd.arena_id)
        return {'arena_id': cmd.arena_id,
         'error': 'arena_id is invalid'} if arenaType is None else self.__collectArenaInfo(arenaType)

    @w2c(_ArenasInfoSchema, 'arenas_info')
    def arenasInfo(self, cmd):
        res = {}
        if cmd.arena_ids:
            for arenaTypeID in cmd.arena_ids:
                arenaType = ArenaType.g_cache.get(arenaTypeID)
                if arenaType is None:
                    return {'arena_id': arenaTypeID,
                     'error': 'arena_id is invalid'}
                res[arenaTypeID] = self.__collectArenaInfo(arenaType)

        else:
            for arenaTypeID, arenaType in ArenaType.g_cache.iteritems():
                res[arenaTypeID] = self.__collectArenaInfo(arenaType)

        return res

    def __collectArenaInfo(self, arenaType):
        arenaName = R.strings.arenas.num(arenaType.geometryName).dyn('name')()
        arenaDescription = R.strings.arenas.num(arenaType.geometryName).dyn('description')()
        gameplayName = R.strings.arenas.type.dyn(arenaType.gameplayName).dyn('name')()
        imageUrl = R.images.gui.maps.icons.map.num(arenaType.geometryName)()
        return {'arena_name': self.__getText(arenaName),
         'arena_description': self.__getText(arenaDescription),
         'gameplay_name': self.__getText(gameplayName),
         'image_url': self.__getImage(imageUrl)}

    def __getText(self, text):
        return backport.text(text) if text is not INVALID_DYN_ATTR else None

    def __getImage(self, image):
        return backport.image(image) if image is not INVALID_DYN_ATTR else None
