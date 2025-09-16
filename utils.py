
def getRoot(info):
    for i, dpline in enumerate(info['dp_parent']):
        if dpline[0] == 'root':
            return i
        
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
