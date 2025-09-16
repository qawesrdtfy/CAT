import os
import json
import tqdm
import random
from sglang import set_default_backend, RuntimeEndpoint


from askLLM import ask_eae
from BuildCAS.Builder import build
from parseSent import STANZA
from utils import find_entity, getRoot, level_split, get_head
from BuildCAS.Extractor import extract_entity
from Search import get_targetzone

SEED = 42
os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
set_default_backend(RuntimeEndpoint("http://localhost:30001"))


def test_ask_argument_for_explain():
    parser = STANZA()

    dataset = "ERE"
    data = json.load(
        open(
            f"Data/{dataset}/stanza-ONEIE-origin-sent/test.w1.oneie.json",
            "r",
            encoding="utf-8",
        )
    )
    definitions = json.load(
        open(f"Data/{dataset}/guideline-ask-ONEIE.json", "r", encoding="utf-8")
    )
    right, guess, answer = 0, 0, 0
    righti, guessi, answeri = 0, 0, 0
    right_len = []
    sen_len = 0
    sen_count = 0
    same_sen = 0
    outsf = open(f"{dataset}-EAE-result.jsonl", "w", encoding="utf-8")
    outsRes = open(f"predictResult.txt", "w", encoding='utf-8')
    for i, d in tqdm.tqdm(enumerate(data)):
        if d["event_mentions"] == []:
            continue
        # stanza解析
        info = parser.parse(d["o_sentence"])
        # 构建一种树
        parent, children = build(info, getRoot(info))
        levels = level_split(info)
        # 拿到所有实体
        entitys = extract_entity(info, parent, children, 0, len(info["words"]))
        print('0_sent', d["o_sentence"])
        for event in d["event_mentions"]:
            etype = event["event_type"]
            trigger = event["trigger"]["text"]
            gt_arguments = {}
            # 尝试剪枝句子
            try:
                start_i, end_i = find_entity(info, trigger)
                e_sentence = get_targetzone(
                    info, parent, children, list(range(start_i, end_i))
                )
            except Exception:
                print('wrong')
                e_sentence = d["o_sentence"]
            print('e_sent', e_sentence)
            sen_len += len(e_sentence.split(' '))
            sen_count += 1
            e_entitys = [one for one in entitys if one in e_sentence]
            for arg in event["arguments"]:
                gt_arguments[arg["role"]] = gt_arguments.get(arg["role"], []) + [
                    arg["text"]
                ]
            event_info = definitions[etype]["definition"]

            roles_explains = {}
            for k in definitions[etype]["args"].keys():
                roles_explains[k] = definitions[etype]["args"][k]
            #############################
            # 进行论元抽取
            try:
                guess_dict = ask_eae(
                    e_sentence, trigger, etype, event_info, roles_explains, e_entitys
                )
            except:
                print(e_entitys)
                print(e_sentence)
                assert False
            #############################
            all_predicts = []
            all_gts = []
            for role, predicts in guess_dict.items():
                guess += len(predicts)
                gts = gt_arguments.get(role, [])
                answer += len(gts)
                outs_p = []
                outs_r = []
                span_predicts = []
                predicts_hit = []
                for predict in predicts:
                    a, b = find_entity(info, predict)
                    head = get_head(levels, [one for one in range(a, b + 1)])
                    span_predicts.append("-".join([str(one) for one in head]))
                    predicts_hit.append(0)
                all_predicts += span_predicts
                for gt in gts:
                    a, b = find_entity(info, gt)
                    if a == -1 or b == -1:
                        assert False
                    gt_is = [one for one in range(a, b + 1)]
                    head = get_head(levels, gt_is)
                    span_gt = "-".join([str(one) for one in head])
                    all_gts.append(span_gt)
                    for spi, span_predict in enumerate(span_predicts):
                        if span_gt == span_predict:
                            right += 1
                            predicts_hit[spi] = 1
                            # print(e_sentence)
                            right_len.append(len(e_sentence.split(' ')))
                            if (e_sentence == d["o_sentence"]):
                                same_sen += 1
                            break
                    else:
                        outs_r.append(gt)
                outs_p = [
                    one for ii, one in enumerate(predicts) if predicts_hit[ii] == 0
                ]
                outsf.write(
                    json.dumps(
                        {
                            "o_sentence": e_sentence,
                            "trigger": trigger,
                            "etype": etype,
                            "role": role,
                            "guess": predicts,
                            "answer": gts,
                            "outs_p": outs_p,
                            "outs_r": outs_r,
                            "entitys": e_entitys,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
            for allpr in all_predicts:
                for allgt in all_gts:
                    if allgt == allpr:
                        righti += 1
                        break
            guessi += len(all_predicts)
            answeri += len(all_gts)
    print(sen_len/sen_count)
    print(right_len)
    print(sum(right_len)/len(right_len))
    print(same_sen)  # 与right比较
    print("##########")
    print(right, guess, answer)
    p = right / guess if guess != 0 else 0
    r = right / answer if answer != 0 else 0
    f = 2 * p * r / (p + r) if p + r != 0 else 0
    print("cp", p, "cr", r, "cf", f)
    print(righti, guessi, answeri)
    p = righti / guessi if guessi != 0 else 0
    r = righti / answeri if answeri != 0 else 0
    f = 2 * p * r / (p + r) if p + r != 0 else 0
    print("ip", p, "ir", r, "if", f)


if __name__ == "__main__":
    test_ask_argument_for_explain()
