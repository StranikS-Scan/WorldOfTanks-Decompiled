# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/base/vehicle_playlists_helper.py
from __future__ import absolute_import
import typing

class IVehiclePlaylistsGuiHelper(object):

    @classmethod
    def isPlaylistsSupported(cls):
        raise NotImplementedError


class EmptyVehiclePlaylistsGuiHelper(IVehiclePlaylistsGuiHelper):

    @classmethod
    def isPlaylistsSupported(cls):
        return None


class DefaultVehiclePlaylistsGuiHelper(IVehiclePlaylistsGuiHelper):

    @classmethod
    def isPlaylistsSupported(cls):
        return False


class RandomVehiclePlaylistsGuiHelper(IVehiclePlaylistsGuiHelper):

    @classmethod
    def isPlaylistsSupported(cls):
        return True
