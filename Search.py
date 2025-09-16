from utils import match_sentence, get_continual_nums, ndeep


def get_targetzone(info, net_parents, net_children, trigger_is):
    """
        寻找目标域方法
        整个句子删掉sub关系作为目标域，只不过trigger在的地方（目标句）不删。
        trigger_is是中心词下标列表
    """
    # 先找目标句
    target_sentence_is = set()
    for trigger_i in trigger_is:
        if trigger_i in target_sentence_is:
            continue
        # 首先，走到最近的主节点
        while 'sub' in net_parents[trigger_i]['nodetype']:
            trigger_i = net_parents[trigger_i]['parents'][0][1]
        if net_parents[trigger_i]['parents'] != []:
            for paren in net_parents[trigger_i]['parents']:
                if paren[0] not in ['SV', 'VO', 'P_SO', 'P_VP']:
                    parenti = paren[1]
                    break
            else:
                parenti = net_parents[trigger_i]['parents'][0][1]
            trigger_i = parenti
        # 然后，如果当前节点是S或O，走到最近的V
        while 'VP' not in net_parents[trigger_i]['nodetype'] and net_parents[trigger_i]['parents'] != []:
            for paren in net_parents[trigger_i]['parents']:
                if paren[0] in ['SV', 'VO', 'P_SO']:
                    parenti = paren[1]
                    break
            else:
                parenti = net_parents[trigger_i]['parents'][0][1]
            trigger_i = parenti
        print('trigger_i', net_parents[trigger_i]['parents'] == [])
        target_sentence_is = target_sentence_is.union(set(ndeep(info, net_parents, net_children, trigger_i, True)))
    # 再找目标域
    print('0_len',len(info['words']))
    print('t_len',len(target_sentence_is))
    words_is = [i for i, one in enumerate(net_parents) if 'sub' not in one['nodetype'] or i in target_sentence_is]
    part_is = get_continual_nums(words_is)
    parts = [match_sentence(info['sentence'], [info['words'][i] for i in one]) for one in part_is]
    return ' '.join(parts) 

