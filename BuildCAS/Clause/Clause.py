from .subjectClause import *
from .objectClause import *
from .predicateClause import *
from .adClause import *


def getClauseFlags(info):
    """得到每种从句的中心词标志"""
    # 获得主语从句、宾语从句、表语从句、定语状语从句的中心词标志
    sc_flags = isSubjectClause(info)
    oc_flags = isObjectClause(info)
    pc_flags = isPredicateClause(info)
    ad_flags = isADClause(info)
    # 合并，不再确保每个词只有可能是一种从句的中心词标志
    clause_flags = [''.join(one) for one in zip(sc_flags, oc_flags, pc_flags, ad_flags)]
    # for flag in clause_flags:
    #     assert len(flag) <= 3, print(clause_flags, info['sentence'])
    return clause_flags
