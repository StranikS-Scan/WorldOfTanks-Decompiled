# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/debug_plan_loader.py
from constants import IS_DEVELOPMENT
if IS_DEVELOPMENT:
    import VSE
    from plan_holder import PlanHolder
    import weakref
    from debug_utils import LOG_DEBUG_DEV
    from plan_tags import getAllTags

    class DebugPlanHolder(PlanHolder):
        __slots__ = 'contextName'

        def __init__(self, plan, state, auto=False):
            super(DebugPlanHolder, self).__init__(plan, state, auto)
            self.contextName = ''


    class DebugPlanLoader(object):

        def __init__(self):
            self.__contextAll = []
            self.__plans = {}
            self.__tags = getAllTags()

        def getContext(self, name):
            for ctx in self.__contextAll:
                if type(ctx()).__name__ == name:
                    return ctx()

            return None

        def regContext--- This code section failed: ---

  31       0	SETUP_LOOP        '87'
           3	LOAD_FAST         'self'
           6	LOAD_ATTR         '__contextAll'
           9	GET_ITER          ''
          10	FOR_ITER          '38'
          13	STORE_FAST        'ctx'

  32      16	LOAD_FAST         'ctx'
          19	CALL_FUNCTION_0   ''
          22	LOAD_FAST         'context'
          25	COMPARE_OP        '=='
          28	POP_JUMP_IF_FALSE '10'

  33      31	BREAK_LOOP        ''
          32	CONTINUE          '10'
          35	JUMP_BACK         '10'
          38	POP_BLOCK         ''

  35      39	LOAD_FAST         'self'
          42	LOAD_ATTR         '__contextAll'
          45	LOAD_ATTR         'append'
          48	LOAD_GLOBAL       'weakref'
          51	LOAD_ATTR         'ref'
          54	LOAD_FAST         'context'
          57	CALL_FUNCTION_1   ''
          60	CALL_FUNCTION_1   ''
          63	POP_TOP           ''

  36      64	LOAD_GLOBAL       'LOG_DEBUG_DEV'
          67	LOAD_CONST        'VSContext %s was registered'
          70	LOAD_GLOBAL       'type'
          73	LOAD_FAST         'context'
          76	CALL_FUNCTION_1   ''
          79	LOAD_ATTR         '__name__'
          82	BINARY_MODULO     ''
          83	CALL_FUNCTION_1   ''
          86	POP_TOP           ''
        87_0	COME_FROM         '0'

Syntax error at or near 'POP_BLOCK' token at offset 38

        def unregContext(self, context):
            for ctx in self.__contextAll[:]:
                if ctx() == context:
                    self.__contextDestroyed(context)
                    self.__contextAll.remove(ctx)
                    LOG_DEBUG_DEV('VSContext %s was unregistered' % type(context).__name__)
                    break

        def startPlan(self, planName, contextName, aspect, params={}):
            if planName in self.__plans:
                self.__plans[planName].start()
                return True
            holder = DebugPlanHolder(VSE.Plan(), PlanHolder.LOADING, False)
            holder.params = params
            if contextName != '':
                context = self.getContext(contextName)
                if context:
                    holder.plan.setContext(context)
                    holder.contextName = contextName
                else:
                    return False
            holder.load(planName, aspect, self.__tags)
            if holder.isLoaded:
                holder.start()
                self.__plans[planName] = holder
                return True
            return False

        def stopPlan(self, planName):
            if planName in self.__plans:
                self.__plans[planName].plan.stop()
                del self.__plans[planName]
                return True
            return False

        def stopAllPlans(self):
            res = True
            for planName in list(self.__plans.keys()):
                res &= self.stopPlan(planName)

            return res

        def __contextDestroyed(self, context):
            for planName in list(self.__plans.keys()):
                holder = self.__plans[planName]
                if holder.contextName == type(context).__name__:
                    holder.plan.stop()
                    del self.__plans[planName]


    debugPlanLoader = DebugPlanLoader()