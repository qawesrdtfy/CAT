def strip_pos(info, xs, bad_pos):
    start_i = 0
    end_i = len(xs)
    while start_i < len(xs) and info['pos'][xs[start_i]] in bad_pos:
        start_i += 1
    while end_i > -1 and info['pos'][xs[end_i-1]] in bad_pos:
        end_i -= 1
    if end_i <= start_i:
        return []
    return xs[start_i:end_i]


def strip_relation(info, xs, bad_relations):
    start_i = 0
    end_i = len(xs)
    while start_i < len(xs) and info['dp_parent'][xs[start_i]][0] in bad_relations:
        start_i += 1
    while end_i > -1 and info['dp_parent'][xs[end_i-1]][0] in bad_relations:
        end_i -= 1
    if end_i <= start_i:
        return xs
    return xs[start_i:end_i]


def withroot_longest_continue(info, idxs, root):
    """
        得到root在的最长的idxs连续序列
    """
    rooti = idxs.index(root)
    right_end = rooti
    while right_end < len(idxs):
        if right_end-rooti != idxs[right_end]-root:
            break
        right_end += 1
    left_end = rooti
    while left_end >= 0:
        if left_end-rooti != idxs[left_end]-root:
            break
        left_end -= 1
    left_end += 1
    idxs = idxs[left_end:right_end]
    return idxs


def split_continues(idxs):
    rets = []
    line = []
    for i, idx in enumerate(idxs):
        if line == []:
            line.append(idx)
            continue
        if line[-1]+1 != idx:
            rets.append(line)
            line = []
        line.append(idx)
    else:
        rets.append(line)
        line = []
    return rets


def is_Capital(info, i):
    if i == 0:
        if info['lemma'][i][0].isupper():
            return True
        return False
    if info['words'][i][0].isupper():
        return True
    return False


def Capital_continue(info, rooti, good_relations=[]):
    """
        得到root在的最长首字母大写连续序列
    """
    right_end = rooti
    while right_end < len(info['lemma'])-1:
        if is_Capital(info, right_end+1) or info['dp_parent'][right_end+1][0] in good_relations:
            right_end += 1
        else:
            break
    left_end = rooti
    while left_end > 0:
        if is_Capital(info, left_end-1) or info['dp_parent'][left_end-1][0] in good_relations:
            left_end -= 1
        else:
            break
    idxs = list(range(left_end, right_end+1))
    idxs = strip_relation(info, idxs, good_relations)
    if rooti not in idxs:
        return [rooti]
    return idxs


def find_entity(info, entity):
    """
        return the entity's range in the sentence
    """
    origin_sentence = ' '.join(info['words'])
    part_words = entity.split(' ')
    origin_sentence_nosapce = origin_sentence.replace(' ', '')
    part_sentence_nospace = ''.join(part_words).replace(' ', '')
    s_start_i = origin_sentence_nosapce.find(part_sentence_nospace)
    if s_start_i == -1:
        return -1, -1
    s_end_i = s_start_i+len(part_sentence_nospace)
    origin_words = origin_sentence.split(' ')
    assert origin_words == info['words']
    count = 0
    start_i = -1 if s_start_i != 0 else 0
    end_i = -1
    # print(s_start_i, s_end_i)
    for word_i in range(len(origin_words)):
        count += len(origin_words[word_i])
        # print(count)
        if start_i == -1:
            if count == s_start_i:
                start_i = word_i+1
            elif count > s_start_i:
                start_i = word_i
        elif end_i == -1 and count >= s_end_i:
            end_i = word_i+1
            break
    assert start_i != -1 and end_i != -1, print(start_i, end_i, origin_sentence, part_words)
    return start_i, end_i


def get_continual_nums(nums):
    rets = []
    part = []
    for num in nums:
        if part == [] or part[-1]+1 == num:
            part.append(num)
        else:
            rets.append(part)
            part = [num]
    else:
        rets.append(part)
    return rets


def find_sublist_index(sublist, mainlist):
    # 子列表长度
    sublist_len = len(sublist)
    # 主列表长度
    mainlist_len = len(mainlist)

    # 遍历主列表，寻找子列表的开始位置
    for i in range(mainlist_len - sublist_len + 1):
        # 如果在主列表中找到了子列表的开始元素，并且接下来的元素也匹配
        if mainlist[i:i+sublist_len] == sublist:
            return i  # 返回子列表的开始下标
    return -1  # 如果没有找到，返回-1


def match_sentence_capital(origin_sentence: str, parts: set):
    """
        如果part在origin_sentence里（无论大小写），就返回origin_sentence里对应的样子。
    """
    rets = set()
    origin_sentence_list = origin_sentence.rstrip('.').split(' ')
    origin_sentence_lower = origin_sentence.rstrip('.').lower()
    for part in parts:
        # 如果无论大小写part在origin_sentence里，返回origin_sentence里对应的样子
        origin_sentence_lower_list = origin_sentence_lower.split(' ')
        part_lower_list = part.lower().split(' ')
        start_i = find_sublist_index(part_lower_list, origin_sentence_lower_list)
        if start_i != -1:
            rets.add(' '.join(origin_sentence_list[start_i:start_i+len(part_lower_list)]))
    return rets


def match_sentence(origin_sentence: str, part_words: list, precise=True):
    """
        Get the appearance of 'part_words' in the 'origin_sentence'.
    """
    if len(part_words) == 1 and part_words[0] in origin_sentence:
        return part_words[0]
    origin_sentence_nosapce = origin_sentence.replace(' ', '#######')
    part_sentence_nospace = '#######'.join(part_words).replace(' ', '#######')
    s_start_i = origin_sentence_nosapce.find(part_sentence_nospace)
    if s_start_i != -1:
        s_start_i -= origin_sentence_nosapce[:s_start_i].count('#######')*len('#######')
        origin_sentence_nosapce = origin_sentence.replace(' ', '')
        part_sentence_nospace = ''.join(part_words).replace(' ', '')
        assert part_sentence_nospace == origin_sentence_nosapce[s_start_i:s_start_i+len(part_sentence_nospace)], print(part_words, origin_sentence_nosapce, part_sentence_nospace, origin_sentence_nosapce[s_start_i:s_start_i+len(part_sentence_nospace)], s_start_i)
    else:
        origin_sentence_nosapce = origin_sentence.replace(' ', '')
        part_sentence_nospace = ''.join(part_words).replace(' ', '')
        s_start_i = origin_sentence_nosapce.find(part_sentence_nospace)
    if s_start_i == -1:
        return ''
    s_end_i = s_start_i+len(part_sentence_nospace)
    origin_words = origin_sentence.split(' ')
    count = 0
    start_i = -1 if s_start_i != 0 else 0
    end_i = -1
    # print(s_start_i, s_end_i)
    left_overflow = -1
    right_overflow = -1
    for word_i in range(len(origin_words)):
        count += len(origin_words[word_i])
        # print(count)
        if start_i == -1:
            if count == s_start_i:
                start_i = word_i+1
            elif count > s_start_i:
                start_i = word_i
                left_overflow = count-s_start_i
        if end_i == -1 and count >= s_end_i:
            if count > s_end_i:
                right_overflow = count-s_end_i
            end_i = word_i+1
            break
    assert start_i != -1 and end_i != -1, print(start_i, end_i, origin_sentence, part_words)
    if precise:
        if left_overflow == -1 and right_overflow == -1:
            return ' '.join(origin_words[start_i:end_i])
        elif left_overflow == -1:  # right overflow
            if end_i == start_i+1:
                return origin_words[end_i-1][:-right_overflow]
            else:
                return ' '.join(origin_words[start_i:end_i-1])+' '+origin_words[end_i-1][:-right_overflow]
        elif right_overflow == -1:  # left overflow
            if end_i == start_i+1:
                return origin_words[start_i][-left_overflow:]
            else:
                return origin_words[start_i][-left_overflow:]+' '+' '.join(origin_words[start_i+1:end_i])
        else:  # both overflow
            if end_i == start_i+1:
                return origin_words[start_i][-left_overflow:-right_overflow]
            elif end_i == start_i+2:
                return origin_words[start_i][-left_overflow:]+' '+origin_words[end_i-1][:-right_overflow]
            else:
                return origin_words[start_i][-left_overflow:]+' '+' '.join(origin_words[start_i+1:end_i-1])+' '+origin_words[end_i-1][:-right_overflow]
    return ' '.join(origin_words[start_i:end_i])

###################################

def getRoot(info):
    for i, dpline in enumerate(info['dp_parent']):
        if dpline[0] == 'root':
            return i


def upUntil(info, start_i, stop_idxs):
    # 向上直到遇到stop_idxs
    i = start_i
    untils = stop_idxs.copy()
    untils.append(-1)
    while info['dp_parent'][i][6] not in untils:
        i = info['dp_parent'][i][6]
    return info['dp_parent'][i][6]


def upUntilButPrivilege(info, start_i, stop_idxs, good_relations):
    # 向上直到遇到stop_idxs，但是如果遇到的时候是good_relations，那么可以继续
    i = start_i
    untils = stop_idxs.copy()
    untils.append(-1)
    while info['dp_parent'][i][6] not in untils or info['dp_parent'][i][0] in good_relations:
        i = info['dp_parent'][i][6]
    return info['dp_parent'][i][6]


def upThrough(info, start_i, good_relations):
    # 沿着good_relations向上
    i = start_i
    while info['dp_parent'][i][0] in good_relations:
        i = info['dp_parent'][i][6]
    return i


def deep(info, start_i):
    rets = []
    stack = [start_i]
    while len(stack) > 0:
        node_i = stack.pop()
        rets.append(node_i)
        for children in info['dp_children'][node_i].values():
            stack += children
    rets.sort()
    return rets


def get_children(info, root):
    rets = []
    for v in info['dp_children'][root].values():
        rets += v
    rets.sort()
    return rets


def deepThroughIdx(info, start_i, good_idxs):
    rets = []
    stack = [start_i]
    while len(stack) > 0:
        node_i = stack.pop()
        rets.append(node_i)
        for children in info['dp_children'][node_i].values():
            stack += [one for one in children if one in good_idxs]
    rets.sort()
    return rets


def deepThrough(info, start_i, good_relations, cont=False):
    rets = []
    stack = [start_i]
    while len(stack) > 0:
        node_i = stack.pop()
        rets.append(node_i)
        for relation, children in info['dp_children'][node_i].items():
            if relation in good_relations:
                stack += children
    rets.sort()
    if cont:
        rets = withroot_longest_continue(info, rets, start_i)
    return rets


def deepUntil(info, start_i, bad_relations, cont=False):
    rets = []
    stack = [start_i]
    while len(stack) > 0:
        node_i = stack.pop()
        rets.append(node_i)
        for relation, children in info['dp_children'][node_i].items():
            if relation not in bad_relations:
                stack += children
    rets.sort()
    if cont:
        rets = withroot_longest_continue(info, rets, start_i)
    return rets


def level_split(info):
    rets = []
    root = getRoot(info)
    this_level = []
    next_level = [root]
    while len(next_level) > 0:
        this_level = next_level
        next_level = []
        for node in this_level:
            for v in info['dp_children'][node].values():
                next_level += v
        rets.append(this_level)
    return rets


def get_head(levels, xs):
    head = []
    for level in levels:
        found = False
        for x in xs:
            if x in level:
                head.append(x)
                found = True
        if found:
            break
    return head

###################################

def nodeType(node):
    """
        判断节点类型，主节点1次节点0
    """
    if len(set(['S', 'O', 'VP_BE', 'VP_DO']).intersection(set(node['nodetype']))) > 0:
        return 1
    return 0


def is_S_O_BE(node):
    """
        判断节点类型
    """
    return len(set(['S', 'O', 'VP_BE']).intersection(set(node['nodetype']))) > 0


def ndeep(info, net_parents, net_children, start_i, cont=False):
    rets = set()
    stack = [start_i]
    while len(stack) > 0:
        node_i = stack.pop()
        rets.add(node_i)
        goods = []
        for relation, children in net_children[node_i].items():
            goods += children
        goods = list(set(goods))
        stack += goods
    rets = list(rets)
    rets.sort()
    if cont:
        rets = withroot_longest_continue(info, rets, start_i)
    return rets


def ndeepThrough(info, net_parents, net_children, start_i, good_relations, bad_relations, cont=False):
    rets = set()
    stack = [start_i]
    while len(stack) > 0:
        node_i = stack.pop()
        rets.add(node_i)
        goods = []
        bads = []
        for relation, children in net_children[node_i].items():
            if relation in good_relations:
                goods += children
            if relation in bad_relations:
                bads += children
        goods = list(set(goods))
        bads = list(set(bads))
        stack += [one for one in goods if one not in bads]
    rets = list(rets)
    rets.sort()
    if cont:
        rets = withroot_longest_continue(info, rets, start_i)
    return rets
