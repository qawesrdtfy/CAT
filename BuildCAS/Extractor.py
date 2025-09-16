from .utils import nodeType, is_S_O_BE, deepThrough, level_split, deep, get_children, Capital_continue, match_sentence, strip_relation, is_Capital, split_continues, match_sentence_capital
from .constants import parallel, mod, together, limit_v, limit_n, ms_relations, connect, mod_clause, subject, object, amod, advmod, nmod, nummod, obl, others, subject_clause


def find_entitys(info, net_parents, net_children, start_i=None, end_i=None, relations=None):
    """
        Building Stage 1: Find the head words of the entities.
    """
    if start_i is None:
        start_i = 0
    if end_i is None:
        end_i = len(info['words'])
    
    entitys = set()
    # subject, object, predicative
    nodes = {i for i in range(start_i, end_i) if is_S_O_BE(net_parents[i])}
    entitys = entitys.union(nodes)
    # conjunction, complement, modification
    nodes = {i for i in range(start_i, end_i) if info['dp_parent'][i][0] in parallel+together+mod}
    entitys = entitys.union(nodes)
    return entitys


def get_extends(children_subtrees, rooti):
    """
        The second step in Building Stage 2: Expand the head word bidirectionally.
        inputs:
            children_subtrees: the subtree of each child of the head word in the sentence.
            rooti: index of the head word
    """
    left_ones = [[]]
    left_one = []
    iter_i = rooti-1
    while iter_i >= 0:
        if children_subtrees[iter_i][-1]+1 != children_subtrees[iter_i+1][0]:
            break
        left_one = children_subtrees[iter_i]+left_one
        left_ones.append(left_one)
        iter_i -= 1

    right_ones = [[]]
    right_one = []
    iter_i = rooti+1
    while iter_i < len(children_subtrees):
        if children_subtrees[iter_i-1][-1]+1 != children_subtrees[iter_i][0]:
            break
        right_one = right_one+children_subtrees[iter_i]
        right_ones.append(right_one)
        iter_i += 1
    rets = []
    for left_one in left_ones:
        for right_one in right_ones:
            rets.append(left_one+children_subtrees[rooti]+right_one)
    return rets


def entity_extend(info, net_parents, net_children, entitys):
    """
        Building Stage 2: Expand the head words.
    """
    rets_set = set()
    # the subtree of each word in the sentence. each element is like [[nodes in the subtree], [continual part1], [continual part2] ...]
    node_subtrees = [None for _ in info['words']]
    # classify these words according to their depth (level) in the tree
    level_splits = level_split(info)[::-1]
    for level in level_splits: # from bottom to top
        for node in level:
            """the 1st step in Building Stage 2: Fine the subtrees of the head word's children. (children_subtrees)"""
            # the node's children
            children = get_children(info, node)
            # the node's subtree
            subtree = [node]
            # the subtree of each child of the node in the sentence.
            children_subtrees = [[node]]
            for child in children:
                subtree += node_subtrees[child][0]
                children_subtrees += node_subtrees[child][1:]
            subtree.sort()
            node_subtrees[node] = [subtree]+split_continues(subtree)
            """if the node is a head word, do the 2nd step in Building Stage 2"""
            if node in entitys:
                children_subtrees.sort(key=lambda x: x[0])
                node_idx = 0
                while node_idx < len(children_subtrees):
                    if children_subtrees[node_idx] == [node]:
                        break
                    node_idx += 1
                else:
                    assert False
                extends = get_extends(children_subtrees, node_idx)
                # delete some bad relations (CY)
                extends = [strip_relation(info, one, connect) for one in extends]
                # make sure the entities we got appear in the sentence
                extends = {match_sentence(info['sentence'], [info['words'][i] for i in one]) for one in extends}
                rets_set = rets_set.union(extends)
    return rets_set


def extract_entity(info, net_parents, net_children, start_i=None, end_i=None):
    """
        Construct the Candidate Argument Set: Prepare, Build and Filter
        Here is the "Build"
    """
    entity_seeds = find_entitys(info, net_parents, net_children, start_i, end_i)
    entity_set = entity_extend(info, net_parents, net_children, entitys=entity_seeds)
    return entity_set

