# -*- coding: utf-8 -*-
import os
from pypdf import PdfReader
from gensim import corpora, models
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def get_book_paths():
    books_dir = 'books'
    book_paths = []
    for filename in sorted(os.listdir(books_dir)):
        if filename.endswith('.pdf'):
            book_path = os.path.join(books_dir, filename)
            book_paths.append(book_path)
    return book_paths


def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file, strict=False)
            page_count = len(pdf_reader.pages)
            text = ''
            for page_number in range(page_count):
                page = pdf_reader.pages[page_number]
                text += page.extract_text()
        return text
    except Exception:
        print(f'Error reading PDF file: {file_path}')
        return ''


def create_texts(documents):
    stoplist = set(stopwords.words('russian'))
    #stoplist = set(stopwords.words('english')) | set(stopwords.words('russian'))
    tokenized_texts = [
        [word for word in word_tokenize(document.lower()) if word not in stoplist]
        for document in documents
    ]

    frequency = Counter(token for text in tokenized_texts for token in text)

    return [
        [token for token in text if frequency[token] > 1]
        for text in tokenized_texts
    ]


if __name__ == '__main__':
    raw_documents = []
    paths = get_book_paths()

    for path in paths:
        doc = extract_text_from_pdf(path)
        if doc != '':
            raw_documents.append(doc)
        else:
            os.remove(path)
    texts = create_texts(raw_documents)
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)

    dictionary.save('model_data/dictionary')
    corpora.MmCorpus.serialize('model_data/corpus', corpus)
    lsi.save('model_data/lsi_model')
