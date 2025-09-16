from ..constants import *
from ..utils import upThrough


def isObjectClause(info):
    """
        判断每个单词是否是宾语从句中心词
        input: 
            info 句子解析结果
        output: 
            rets 句子长度的列表，意为每个单词是否为宾语从句中心词（如果是，是哪一种）
    """
    rets = []
    for i, dpline in enumerate(info['dp_parent']):
        if len(set(mod_clause).intersection(info['dp_children'][i].keys())) > 0 and info['dp_parent'][upThrough(info, i, parallel)][0] in object:
            rets.append('oc1')
        elif dpline[0] in object_clause:
            rets.append('oc2')
        else:
            rets.append('')
    return rets
