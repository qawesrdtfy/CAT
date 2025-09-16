from ..constants import *
from ..utils import upThrough


def isPredicateClause(info):
    """
        判断每个单词是否是表语从句中心词
        input: 
            info 句子解析结果
        output: 
            rets 句子长度的列表，意为每个单词是否为表语从句中心词（如果是，是哪一种）
    """
    rets = []
    for i, dpline in enumerate(info['dp_parent']):
        if len(set(mod_clause).intersection(info['dp_children'][i].keys())) > 0 and 'cop' in info['dp_children'][i].keys():
            rets.append('pc1')
        elif 'nsubj:outer' in info['dp_children'][i].keys() and 'cop' in info['dp_children'][i].keys():
            rets.append('pc2')
        else:
            rets.append('')
    return rets
