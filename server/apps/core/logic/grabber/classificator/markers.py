from django.conf import settings

IGNORED_WORD_COMBINATIONS = []


def rate(normalized_text):
    if not normalized_text:
        relevance = -1
    else:
        normalized_text = _remove_subsequences(
            normalized_text, IGNORED_WORD_COMBINATIONS)
        found_markers = sum((1 for word in normalized_text if word in settings.MARKERS))
        relevance = round(100 * found_markers / len(normalized_text))
    return relevance >= settings.RELEVANCE_TRESHOLD


def _remove_subsequences(seq, subseqs):
    clean = []
    i = 0
    while i < len(seq):
        for subseq in subseqs:
            a = seq[i: i + len(subseq)]
            if a == list(subseq):
                i += len(subseq)
                break
        else:
            clean += [seq[i]]
            i += 1
    return clean
