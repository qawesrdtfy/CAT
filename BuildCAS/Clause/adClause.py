from ..constants import *
from ..utils import deep,strip_pos

def isADClause(info):
    """
        判断每个单词是否是状语或定语从句中心词
        input: 
            info 句子解析结果
        output: 
            rets 句子长度的列表，意为每个单词是否为宾语从句中心词（如果是，是哪一种）
    """
    rets = []
    for i, dpline in enumerate(info['dp_parent']):
        if dpline[0] in mod_clause:
            rets.append('ad1')
        else:
            rets.append('')
    return rets


def extractADClauseSent(info, clause_flags):
    """
        抽取从句
        input: 
            info 句子解析结果
            clause_flags 从句中心词标记列表
        output: 
            rets 句子长度的列表，如果对应位置元素的单词是状语定语从句中心词，那么就是[从句下标列表，被修饰词下标]
    """
    rets = []
    for i, flag in enumerate(clause_flags):
        if 'ad' in flag:
            clasue_idxs = deep(info, i)
            clasue_idxs = strip_pos(info, clasue_idxs, ['PUNCT'])
            rets.append([clasue_idxs, info['dp_parent'][i][6]])
        else:
            rets.append(None)
    return rets
