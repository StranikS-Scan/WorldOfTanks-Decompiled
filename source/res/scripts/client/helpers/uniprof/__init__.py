# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/uniprof/__init__.py
import BigWorld
__all__ = ('regionDecorator', 'enterToRegion', 'exitFromRegion')

def _isRegionSupported():
    if not hasattr(BigWorld, 'uniprofRegionEnter'):
        return False
    return False if not hasattr(BigWorld, 'uniprofRegionExit') else True


_IS_REGION_SUPPORTED = _isRegionSupported()
if _IS_REGION_SUPPORTED:
    from .regions import regionDecorator
    from .regions import enterToRegion, exitFromRegion
else:

    class _DummyDecorator(object):
        __slots__ = ()

        def __call__(self, func):
            return func


    def enterToRegion(*_):
        pass


    def exitFromRegion(*_):
        pass


    def regionDecorator(*_, **__):
        return _DummyDecorator()
