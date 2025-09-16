"""
主干节点类型：事件中心词（谓语、表语、从句的谓语表语）VP、（从句的）主语S、（从句的）宾语O
主干节点之间的关系：主中关系SV、中宾关系VO、主宾表并列关系P_SO、事件中心词并列关系P_VP
次节点类型：同关系名
次节点之间的关系：sub
主次节点之间的关系：时间Time、地点Place、原因Reason、目的Purpose、条件Condition、方式Manner、让步Concession、比较Comparison、结果Result、只是修饰Modifier、限制词Limit、一起词Together、其他Other
"""
from .Clause.Clause import getClauseFlags, extractADClauseSent
from .utils import upUntil, upUntilButPrivilege, deep, deepThroughIdx
from .constants import subject, object, parallel, clause_marks, mod, limit_v, limit_n, together


def find_VPs(info, root, clause_flags):
    VPs = []
    stack = [i for i, flag in enumerate(clause_flags) if flag != '']
    stack.append(root)
    while len(stack) > 0:
        node = stack.pop()
        if node in VPs:
            continue

        VPs.append(node)
        for relation, children in info['dp_children'][node].items():
            if relation in ['appos', 'conj', 'list', 'parataxis']:  # 并列关系
                stack += children
    VPs.sort()
    return VPs


def find_Ss(info, clause_flags):
    Ss = []
    stack = [i for i, flag in enumerate(clause_flags) if 'sc' in flag] + \
        [i for i, dp_line in enumerate(info['dp_parent']) if dp_line[0] in subject]
    while len(stack) > 0:
        node = stack.pop()
        if node in Ss:
            continue

        Ss.append(node)
        for relation, children in info['dp_children'][node].items():
            if relation in ['appos', 'conj', 'list', 'parataxis']:  # 并列关系
                stack += children
    Ss.sort()
    return Ss


def find_Os(info, clause_flags):
    Os = []
    stack = [i for i, flag in enumerate(clause_flags) if 'oc' in flag] + \
        [i for i, dp_line in enumerate(info['dp_parent']) if dp_line[0] in object]
    while len(stack) > 0:
        node = stack.pop()
        if node in Os:
            continue

        Os.append(node)
        for relation, children in info['dp_children'][node].items():
            if relation in ['appos', 'conj', 'list', 'parataxis']:  # 并列关系
                stack += children
    Os.sort()
    return Os


def connect_P_VP(info, net_parents, net_children, VPs):
    for vp in VPs:
        if 'cop' in info['dp_children'][vp].keys():
            net_parents[vp]['nodetype'].append('VP_BE')
        else:
            net_parents[vp]['nodetype'].append('VP_DO')
        upbound = upUntil(info, vp, VPs)
        if upbound != -1:
            net_parents[vp]['parents'].append(['P_VP', upbound])
            net_children[upbound]['P_VP'] = net_children[upbound].get('P_VP', [])+[vp]


def connect_P_SO(info, net_parents, net_children, Ss, Os):
    for so in Ss+Os:
        parent = info['dp_parent'][so][6]
        if parent in Ss+Os:
            net_parents[so]['parents'].append(['P_SO', parent])
            net_children[parent]['P_SO'] = net_children[parent].get('P_SO', [])+[so]


def connect_SV(info, net_parents, net_children, Ss, VPs):
    for s in Ss:
        net_parents[s]['nodetype'].append('S')
        upbound = upUntilButPrivilege(info, s, VPs, parallel)
        if upbound != -1:
            net_parents[s]['parents'].append(['SV', upbound])
            net_children[upbound]['SV'] = net_children[upbound].get('SV', [])+[s]


def connect_VO(info, net_parents, net_children, Os, VPs):
    for o in Os:
        net_parents[o]['nodetype'].append('O')
        upbound = upUntilButPrivilege(info, o, VPs, parallel)
        if upbound != -1:
            net_parents[o]['parents'].append(['VO', upbound])
            net_children[upbound]['VO'] = net_children[upbound].get('VO', [])+[o]

def find_subnodes(info, mainodes):
    return [i for i in range(len(info['words'])) if i not in mainodes]

def get_clause_mark_sent(info, mark_idxs):
    mark_i = mark_idxs[0]
    if mark_i-2 >= 0:
        three_mark1 = ' '.join(info['lemma'][mark_i-2:mark_i+1])
        if three_mark1 in clause_marks.keys():
            mark_idxs = [mark_i-2, mark_i-1]+mark_idxs
            sent = ' '.join([info['words'][one] for one in mark_idxs])
            return three_mark1, sent
    if mark_i+2 < len(info['lemma']):
        three_mark2 = ' '.join(info['lemma'][mark_i:mark_i+1+2])
        if three_mark2 in clause_marks.keys():
            mark_idxs = mark_idxs+[mark_i+1, mark_i+2]
            sent = ' '.join([info['words'][one] for one in mark_idxs])
            return three_mark2, sent
    if mark_i-1 >= 0:
        two_mark1 = ' '.join(info['lemma'][mark_i-1:mark_i+1])
        if two_mark1 in clause_marks.keys():
            mark_idxs = [mark_i-1]+mark_idxs
            sent = ' '.join([info['words'][one] for one in mark_idxs])
            return two_mark1, sent
    if mark_i+1 < len(info['lemma']):
        two_mark2 = ' '.join(info['lemma'][mark_i:mark_i+1+1])
        if two_mark2 in clause_marks.keys():
            mark_idxs = mark_idxs+[mark_i+1]
            sent = ' '.join([info['words'][one] for one in mark_idxs])
            return two_mark2, sent
    one_mark = info['lemma'][mark_i]
    sent = ' '.join([info['words'][one] for one in mark_idxs])
    if one_mark in clause_marks.keys():
        return one_mark, sent
    else:
        return -1, sent


def connect_MOD(info, net_parents, net_children, clause_flags, ad_clause_sents, mainodes, subnodes):
    for i, flag in enumerate(clause_flags):
        if 'ad' in flag:
            parent = ad_clause_sents[i][1]
            clause_mark, clause_sent = get_clause_mark_sent(info, ad_clause_sents[i][0])
            if clause_mark == -1:
                print('clause_mark==-1', clause_sent)
                relation = 'Modifier'
            else:
                candidates = clause_marks[clause_mark]
                relation = candidates[0]
                # if len(candidates) == 1:
                #     relation = candidates[0]
                # else:
                #     r = ask_role.run(info['sentence'], info['words'][parent], clause_sent, candidates)
                #     relation = r['answer']
            net_parents[i]['nodetype'].append(relation)
            net_parents[i]['parents'].append([relation, parent])
            net_children[parent][relation] = net_children[parent].get(relation, [])+[i]
    for subnode in subnodes:
        parent = info['dp_parent'][subnode][6]
        # subnodes and mainnodes
        if info['dp_parent'][subnode][6] in mainodes:
            dp_flag = info['dp_parent'][subnode][0]
            if dp_flag in limit_v+limit_n:
                relation = 'Limit'
            elif dp_flag in together:
                relation = 'Together'
            elif dp_flag in mod:
                if dp_flag in ['nmod:tmod', 'obl:tmod']:
                    relation = 'Time'
                else:
                    sent_idxs = deepThroughIdx(info, parent, subnodes)
                    sent = ' '.join([info['words'][one] for one in sent_idxs])
                    subpart = ' '.join([info['words'][one] for one in deep(info, subnode)])
                    # r = ask_role.run(sent, info['words'][parent], subpart, ['Time', 'Place', 'Modifier', 'Other'])
                    # relation = r['answer']
                    relation = 'Modifier'
            else:
                relation = 'Other'
            net_parents[subnode]['nodetype'].append(relation)
            net_parents[subnode]['parents'].append([relation, parent])
            net_children[parent][relation] = net_children[parent].get(relation, [])+[subnode]
        # subnodes and subnodes
        else:
            net_parents[subnode]['nodetype'].append('sub')
            net_parents[subnode]['parents'].append(['sub', parent])
            net_children[parent]['sub'] = net_children[parent].get('sub', [])+[subnode]


def get_level(info, net_parents, net_children, root):
    """
        为每个节点赋予深度，root深度为0
        存在这样的情况：从句a修饰主语b，且a以P_VP关系与b的谓语c相连。此时a的深度应该低于b，因此刷新就好了。
    """
    level = 0
    stack = []
    new_stack = [root]
    while len(new_stack) != 0:
        stack = new_stack
        new_stack = []
        while len(stack) > 0:
            node_i = stack.pop()
            net_parents[node_i]['level'] = level
            for k, v in net_children[node_i].items():
                new_stack += v
        new_stack = list(set(new_stack))
        level += 1


def build(info, root):
    """
        构建网络
    """
    """预备信息和初始化"""
    clause_flags = getClauseFlags(info)
    ad_clause_sents = extractADClauseSent(info, clause_flags)
    net_parents = [{"nodetype": [], "parents": []} for _ in clause_flags]
    net_children = [{} for _ in clause_flags]
    """构建主干网络"""
    # 找到主干节点
    VPs = find_VPs(info, root, clause_flags)
    Ss = find_Ss(info, clause_flags)
    Os = find_Os(info, clause_flags)
    # 连接主干节点
    connect_P_VP(info, net_parents, net_children, VPs)
    connect_P_SO(info, net_parents, net_children, Ss, Os)
    connect_SV(info, net_parents, net_children, Ss, VPs)
    connect_VO(info, net_parents, net_children, Os, VPs)
    # connect_C_MOD(info, net_parents, net_children, clause_flags)
    """补全网络"""
    # 找到次节点
    mainodes = VPs+Ss+Os
    subnodes = find_subnodes(info, mainodes)
    # 连接主干节点和次节点
    connect_MOD(info, net_parents, net_children, clause_flags, ad_clause_sents, mainodes, subnodes)
    get_level(info, net_parents, net_children, root)
    return net_parents, net_children
