# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/bsddb/dbutils.py
# Compiled at: 2010-05-25 20:46:16
from time import sleep as _sleep
import sys
absolute_import = sys.version_info[0] >= 3
if absolute_import:
    exec 'from . import db'
else:
    import db
_deadlock_MinSleepTime = 1.0 / 128
_deadlock_MaxSleepTime = 3.14159
_deadlock_VerboseFile = None

def DeadlockWrap--- This code section failed: ---

  62       0	LOAD_GLOBAL       '_deadlock_MinSleepTime'
           3	STORE_FAST        'sleeptime'

  63       6	LOAD_FAST         '_kwargs'
           9	LOAD_ATTR         'get'
          12	LOAD_CONST        'max_retries'
          15	LOAD_CONST        -1
          18	CALL_FUNCTION_2   ''
          21	STORE_FAST        'max_retries'

  64      24	LOAD_FAST         '_kwargs'
          27	LOAD_ATTR         'has_key'
          30	LOAD_CONST        'max_retries'
          33	CALL_FUNCTION_1   ''
          36	JUMP_IF_FALSE     '49'

  65      39	LOAD_FAST         '_kwargs'
          42	LOAD_CONST        'max_retries'
          45	DELETE_SUBSCR     ''
          46	JUMP_FORWARD      '49'
        49_0	COME_FROM         '46'

  66      49	SETUP_LOOP        '197'
          52	LOAD_GLOBAL       'True'
          55	JUMP_IF_FALSE     '196'

  67      58	SETUP_EXCEPT      '78'

  68      61	LOAD_FAST         'function'
          64	LOAD_FAST         '_args'
          67	LOAD_FAST         '_kwargs'
          70	CALL_FUNCTION_VAR_KW_0 ''
          73	RETURN_VALUE      ''
          74	POP_BLOCK         ''
          75	JUMP_BACK         '52'
        78_0	COME_FROM         '58'

  69      78	DUP_TOP           ''
          79	LOAD_GLOBAL       'db'
          82	LOAD_ATTR         'DBLockDeadlockError'
          85	COMPARE_OP        'exception match'
          88	JUMP_IF_FALSE     '192'
          91	POP_TOP           ''
          92	POP_TOP           ''
          93	POP_TOP           ''

  70      94	LOAD_GLOBAL       '_deadlock_VerboseFile'
          97	JUMP_IF_FALSE     '120'

  71     100	LOAD_GLOBAL       '_deadlock_VerboseFile'
         103	LOAD_ATTR         'write'

  72     106	LOAD_CONST        'dbutils.DeadlockWrap: sleeping %1.3f\n'
         109	LOAD_FAST         'sleeptime'
         112	BINARY_MODULO     ''
         113	CALL_FUNCTION_1   ''
         116	POP_TOP           ''
         117	JUMP_FORWARD      '120'
       120_0	COME_FROM         '117'

  73     120	LOAD_GLOBAL       '_sleep'
         123	LOAD_FAST         'sleeptime'
         126	CALL_FUNCTION_1   ''
         129	POP_TOP           ''

  75     130	LOAD_FAST         'sleeptime'
         133	LOAD_CONST        2
         136	INPLACE_MULTIPLY  ''
         137	STORE_FAST        'sleeptime'

  76     140	LOAD_FAST         'sleeptime'
         143	LOAD_GLOBAL       '_deadlock_MaxSleepTime'
         146	COMPARE_OP        '>'
         149	JUMP_IF_FALSE     '161'

  77     152	LOAD_GLOBAL       '_deadlock_MaxSleepTime'
         155	STORE_FAST        'sleeptime'
         158	JUMP_FORWARD      '161'
       161_0	COME_FROM         '158'

  78     161	LOAD_FAST         'max_retries'
         164	LOAD_CONST        1
         167	INPLACE_SUBTRACT  ''
         168	STORE_FAST        'max_retries'

  79     171	LOAD_FAST         'max_retries'
         174	LOAD_CONST        -1
         177	COMPARE_OP        '=='
         180	JUMP_IF_FALSE     '189'

  80     183	RAISE_VARARGS_0   ''
         186	JUMP_ABSOLUTE     '193'
         189	JUMP_BACK         '52'
         192	END_FINALLY       ''
       193_0	COME_FROM         '192'
         193	JUMP_BACK         '52'
         196	POP_BLOCK         ''
       197_0	COME_FROM         '49'

Syntax error at or near 'POP_BLOCK' token at offset 196