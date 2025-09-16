parallel = ['appos', 'conj', 'list', 'parataxis']
subject = ['nsubj', 'nsubj:outer', 'nsubj:pass']
object = ['obj', 'iobj']
subject_clause = ['csubj', 'csubj:outer', 'csubj:pass']
object_clause = []

mod_clause = ['advcl', 'advcl:relcl', 'acl', 'acl:relcl', 'xcomp', 'ccomp']
amod = ['amod']
advmod = ['advmod']
nmod = ['nmod', 'nmod:npmod', 'nmod:poss', 'nmod:tmod']
nummod = ['nummod']
obl = ['obl', 'obl:agent', 'obl:npmod', 'obl:tmod']
mod = amod+advmod+nmod+nummod+obl

limit_v = ['cop', 'aux', 'aux:pass']
limit_n = ['det', 'det:predet']
together = ['compound', 'compound:prt', 'fixed', 'flat', 'goeswith']
ms_relations = ['Time', 'Place', 'Reason', 'Purpose', 'Condition', 'Manner', 'Concession', 'Comparison', 'Result', 'Modifier', 'Limit', 'Together', 'Other']
connect = ['case', 'cc', 'cc:preconj', 'mark', 'punct']
others = ['dislocated', 'vocative', 'discourse', 'reparandum', 'orphan', 'dep']
clause_marks = {
    "as": ["Time", "Reason", "Manner", "Comparison"],
    "to": ["Modifier", "Purpose"],
    "if": ["Condition"],
    "that": ["Result"],
    "whether": ["Condition"],
    "why": ["Modifier"],
    "what": ["Modifier"],
    "whatever": ["Concession"],
    "how": ["Modifier"],
    "however": ["Concession"],
    "who": ["Modifier"],
    "whom": ["Modifier"],
    "whoever": ["Concession"],
    "when": ["Time"],
    "whenever": ["Concession"],
    "where": ["Place"],
    "wherever": ["Concession"],
    "which": ["Modifier"],
    "whichever": ["Concession"],
    "while": ["Time", "Concession"],
    "before": ["Time"],
    "after": ["Time"],
    "since": ["Time", "Reason"],
    "until": ["Time"],
    "till": ["Time"],
    "as soon as": ["Time"],
    "once": ["Time"],
    "because": ["Reason"],
    "now that": ["Reason"],
    "unless": ["Condition"],
    "provided that": ["Condition"],
    "suppose": ["Condition"],
    "supposing": ["Condition"],
    "in case": ["Condition"],
    "on condition that": ["Condition"],
    "although": ["Concession"],
    "though": ["Concession"],
    "even though": ["Concession"],
    "even if": ["Concession"],
    "whereas": ["Concession"],
    "no matter how": ["Concession"],
    "no matter who": ["Concession"],
    "no matter what": ["Concession"],
    "no matter where": ["Concession"],
    "no matter when": ["Concession"],
    "so that": ["Purpose", "Result"],
    "in order that": ["Purpose"],
    "so as to": ["Purpose"],
    "in order to": ["Purpose"],
    "than": ["Comparison"],
    "as if": ["Manner"],
    "as though": ["Manner"]
}
