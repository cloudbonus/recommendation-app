# -*- coding: utf-8 -*-
import os
from gensim import corpora, models
from gensim import similarities
from create_model import extract_text_from_pdf


def analyze_book(path):
    dictionary = corpora.Dictionary.load('model_data/dictionary')
    corpus = corpora.MmCorpus('model_data/corpus')
    lsi = models.LsiModel.load('model_data/lsi_model')

    doc = extract_text_from_pdf(path)
    vec_bow = dictionary.doc2bow(doc.lower().split())
    vec_lsi = lsi[vec_bow]

    index = similarities.MatrixSimilarity(lsi[corpus])

    index.save('/tmp/deerwester.index')
    index = similarities.MatrixSimilarity.load('/tmp/deerwester.index')

    sims = index[vec_lsi]

    return sorted(enumerate(sims), key=lambda item: -item[1])


if __name__ == '__main__':
    directory_path = 'current_book'
    file_name = os.listdir(directory_path)[0]
    res = analyze_book(os.path.join(directory_path, file_name))

    for doc_position, doc_score in res:
        print(doc_position, doc_score)
