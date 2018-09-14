# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Singleton.py


class Singleton(object):

    def __new__(cls, *args, **kwargs):
        singleton_instance = cls.__dict__.get('__instance__')
        if singleton_instance is not None:
            return singleton_instance
        else:
            cls.__instance__ = singleton_instance = object.__new__(cls)
            singleton_instance._singleton_init(*args, **kwargs)
            return singleton_instance

    def _singleton_init(self, *args, **kwargs):
        pass


if __name__ == '__main__':

    class MySingleton(Singleton):

        def _singleton_init(self, instanceName):
            self.instanceName = instanceName


    ins1 = MySingleton('instance1')
    print id(ins1), ins1.instanceName
    ins2 = MySingleton('instance2')
    print id(ins2), ins2.instanceName
