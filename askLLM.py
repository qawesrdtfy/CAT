import sglang
from sglang import function, system, user, assistant, gen, token_length_normalized


@function
def ask(s, sys, usr):
    s += system(f"{sys}")
    s += user(f"{usr}")
    s += assistant(gen(f"answer", max_tokens=256, temperature=0))


@function
def ask_history(s, sys, usr, history):
    s += system(f"{sys}")
    for u, a in history:
        s += user(u)
        s += assistant(a)
    s += user(f"{usr}")
    s += assistant(gen(f"answer", max_tokens=256, temperature=0))


@function
def ask_role(s, sentence, mainpart, subpart, candidates):
    s += system(f"""You are an assistant skilled in semantics. Particularly, you can only choose one from \"{', '.join(candidates)}\" as your result to my question.""")
    s += user(f"""What role does \"{subpart}\" play in the \"{mainpart}\" case in the following sentence: \"{sentence}\".""")
    s += assistant(f'"{subpart}" plays the role of ' + gen("answer", choices=candidates, choices_method=token_length_normalized, max_tokens=256) + f' in the \"{mainpart}\" case.')


@function
def _ask_entitys(s, sentence):
    s += system("""You are an assistant skilled in semantics.""")
    s += user(f"""\"{sentence}\"\nPlease list the entities of people, places, organizations, and countries in the sentence. If it is not explicitly stated in the sentence, just say none.""")
    s += assistant(f"- Example: entity1, entitiy2, entity3\n- People:" + gen("answer", max_tokens=256, temperature=0))


def ask_entitys(sentence):
    rets_set = set()
    rets_dict = {"People": [], "Places": [], "Organizations": [], "Countries": []}
    r = _ask_entitys.run(sentence)
    answers = r['answer'].split('\n')
    for i, answer in enumerate(answers):
        if i == 0:
            typ = 'People'
            answer = answer.strip(' ')
            entitys = answer.split(', ')
            entitys = [one for one in entitys if one != 'none']
            rets_dict[typ] = set(entitys)
            rets_set = rets_set.union(set(entitys))
        else:
            answer = answer.split(': ')
            if len(answer) == 1:
                continue
            typ = answer[0][2:]
            if typ not in ['Places', 'Organizations', 'Countries']:
                continue
            entitys = answer[1].split(', ')
            entitys = [one for one in entitys if one != 'none']
            rets_dict[typ] = set(entitys)
            rets_set = rets_set.union(set(entitys))
    return rets_set, rets_dict

@function
def _sent_explain(s, sentence, trigger, event_explain, history=[]):
    """
        The 1st turn.
    """
    event_explain = event_explain[0].upper()+event_explain[1:]
    
    s += system("""You are an assistant skilled in information extraction.""")
    for turn in history:
        s += user(turn['user'])
        s += assistant(turn['assistant'])
    s += user(f""""{sentence}"\n{event_explain} in the sentence. What does the word "{trigger}" in this sentence indicate?""")
    
    s += assistant(gen('answer', max_tokens=256, temperature=0, stop='\n'))


@function
def _think_eae(s, sentence, trigger, etype, sent_explain, event_explain, role_asks, history=[]):
    """
        The 2nd turn.
    """
    role_asks_str = '\n'.join(['- '+one for one in role_asks])
    s['event_sys'] = f"""You are an assistant skilled in information extraction."""
    s['event_user'] = f"""{sent_explain}\n\nIf the sentence does not specify some information, just say "None explicitly mentioned".\nHere is the information needed:\n{role_asks_str}"""
    
    s += system(s['event_sys'])
    for turn in history:
        s += user(turn['user'])
        s += assistant(turn['assistant'])
    s += user(s['event_user'])
    
    s += sglang.assistant_begin()
    for i, role_ask in enumerate(role_asks):
        if i > 0:
            s += '\n'
        s += f"""- {role_ask}:""" + gen(f"{role_ask}", max_tokens=256, temperature=0, stop='\n')
    s += sglang.assistant_end()


@function
def _choose_eae(s, sentence, trigger, etype, event_explain, refer_answer, role, role_explain, candidates, history=[]):
    """
        The 3rd turn.
    """
    s += system("""You are an assistant skilled in answering questions based on known information.""")
    for turn in history:
        s += user(turn['user'])
        s += assistant(turn['assistant'])
    s += user(f"""{sentence}\nThe word "{trigger}" in this sentence indicates that {event_explain}, which is a {etype} event.\n- **{role_explain}**:{refer_answer}\n\nBased on the above information, answer my question about {role}: {role_explain}?\nYou can only choose the best ones from the entities to answer. If it is not explicitly specified in the information, just say none.\n\nThe entities: {', '.join(candidates)}""")
    
    s += sglang.assistant_begin()
    i = 0
    Capital_candidates = [' '+one[0].upper()+one[1:] for one in candidates]
    s += f"- **Example1**: Entity1, Entity2.\n- **Example2**: None.\n"
    s += f"- **{role_explain}**:"+gen(f"answer0", max_tokens=256, temperature=0, choices=Capital_candidates+[' None.'], choices_method=token_length_normalized)
    if s[f"answer0"] != ' None.':
        answer0_idx = Capital_candidates.index(s[f"answer0"])
        s[f"answer0"] = candidates[answer0_idx]
        del candidates[answer0_idx]
        candidates = [', '+one for one in candidates]
        i = 1
        s += gen(f"answer{i}", max_tokens=256, temperature=0, choices=candidates+['.'], choices_method=token_length_normalized)
        while s[f"answer{i}"] != '.':
            del candidates[candidates.index(s[f"answer{i}"])]
            i += 1
            s += gen(f"answer{i}", max_tokens=256, temperature=0, choices=candidates+['.'], choices_method=token_length_normalized)
    s['answer_end'] = i
    s += sglang.assistant_end()


def ask_eae(sentence, trigger, etype, event_explain, roles_explains: dict, candidates: list, first_history=[], second_history=[], third_history=[]):
    """
        rets: {"role": ["argument1","argument2"...]}
    """
    rets = {}
    # the 1st turn
    sent_explain = _sent_explain.run(sentence, trigger, event_explain, first_history)['answer']
    # the 2nd turn
    free_output_arguments = _think_eae.run(sentence, trigger, etype, sent_explain, event_explain, [v for v in roles_explains.values()], second_history)
    # the 3rd turn
    for role, role_explain in roles_explains.items():
        rets[role] = []
        # smaller the candidate set for each role
        role_candidates = [one for one in candidates if one.lower() in free_output_arguments[role_explain].lower()]
        role_candidates.sort()
        newr = _choose_eae.run(sentence, trigger, etype, event_explain, free_output_arguments[role_explain], role, role_explain, role_candidates, third_history)
        for i in range(newr['answer_end']):
            rets[role].append(newr[f'answer{i}'].lstrip(', '))
    # if "a cute cat" and "cat" were extracted for the same role, choose the longest one.
    for role, predicts in rets.items():
        to_del = []
        for i, a in enumerate(predicts):
            for b in predicts:
                if a != b and a in b:
                    to_del.append(i)
                    break
        predicts = [one for i, one in enumerate(predicts) if i not in to_del]
        rets[role] = predicts
    
    return rets
