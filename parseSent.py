import stanza


class STANZA:
    def __init__(self) -> None:
        self.nlp = stanza.Pipeline('en',
                                   processors='tokenize,pos,lemma,depparse',
                                   model_dir='/data/sdb2/wyh/models/StanzaModel',
                                   download_method=None)

    def build_DP(self, words, head, pos, deprel):
        dp_parent = []
        for i, word in enumerate(words):
            dp_parent.append([
                deprel[i],
                word,
                pos[i],
                i,
                words[head[i]-1] if deprel[i] != 'root' else 'root',
                pos[head[i]-1] if deprel[i] != 'root' else 'root',
                head[i]-1
            ])
        dp_children = []
        for i in range(len(words)):
            chlidren = {}
            for j in range(len(words)):
                if dp_parent[j][6] == i:
                    chlidren[dp_parent[j][0]] = chlidren.get(dp_parent[j][0], [])+[j]
            dp_children.append(chlidren)
        return dp_parent, dp_children

    def union(self, words, lemma, pos, head, deprel, new_words, new_lemma, new_pos, new_head, new_deprel):
        idx0 = head.index(0)+1
        already_sum = len(words)
        words = words+new_words
        lemma = lemma+new_lemma
        pos = pos+new_pos
        new_deprel = [one if new_head[i] != 0 else 'parataxis' for i, one in enumerate(new_deprel)]
        deprel = deprel+new_deprel
        new_head = [one+already_sum if one != 0 else idx0 for one in new_head]
        head = head+new_head
        return words, lemma, pos, head, deprel

    def parse(self, sentence):
        nlped = self.nlp(sentence)

        words = [one.text for one in nlped.sentences[0].words]
        lemma = [one.lemma for one in nlped.sentences[0].words]
        pos = [one.pos for one in nlped.sentences[0].words]
        head = [one.head for one in nlped.sentences[0].words]
        deprel = [one.deprel for one in nlped.sentences[0].words]
        if len(nlped.sentences) > 1:
            for result in nlped.sentences[1:]:
                words, lemma, pos, head, deprel = self.union(words, lemma, pos, head, deprel,
                                                             [one.text for one in result.words],
                                                             [one.lemma for one in result.words],
                                                             [one.pos for one in result.words],
                                                             [one.head for one in result.words],
                                                             [one.deprel for one in result.words])
        dp_parent, dp_children = self.build_DP(words, head, pos, deprel)
        return {
            "sentence": sentence,
            "words": words,
            "pos": pos,
            "lemma": lemma,
            "dp_parent": dp_parent,
            "dp_children": dp_children
        }


if __name__ == '__main__':
    parser = STANZA()
    r = parser.parse("A Cuban patrol boat with four men landed on American shores .")
    print(r['dp_parent'])
    print(r['dp_children'])