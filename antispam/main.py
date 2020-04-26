import base64
import gzip
from collections import namedtuple

import numpy as np
import scipy.sparse
from tqdm import tqdm

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier

DocItem = namedtuple('DocItem', ['doc_id', 'is_spam', 'url', 'features'])


def load_csv(input_file_name, calc_features_f, total: int = None):
    """
    Загружаем данные и извлекаем на лету признаки
    Сам контент не сохраняется, чтобы уменьшить потребление памяти - чтобы
    можно было запускать даже на ноутбуках в классе
    """

    with gzip.open(input_file_name) if input_file_name.endswith('gz') else open(input_file_name) as input_file:
        headers = input_file.readline()

        print("Read " + input_file_name)
        iterator = enumerate(input_file) if total is None else tqdm(enumerate(input_file), total=total)
        for i, line in iterator:
            # trace(i)
            line = line.decode()
            parts = line.strip().split('\t')
            url_id = int(parts[0])
            mark = bool(int(parts[1]))
            url = parts[2]
            pageInb64 = parts[3]
            html_data = base64.b64decode(pageInb64).decode(errors='ignore')
            features = calc_features_f(url, html_data)
            yield DocItem(url_id, mark, url, features)

        # trace(i, 1)


def main():
    get_html = lambda url, html_data: html_data
    skip_feature = lambda url, html_data: None
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    test = load_csv('data/kaggle_test_data_tab.csv.gz', get_html, total=16039)
    vectorizer.fit([item.features for item in test])
    train = load_csv('data/kaggle_train_data_tab.csv.gz', get_html, total=7044)
    X = vectorizer.fit_transform([item.features for item in train])
    print(">>> vectorizer fitted <<<")

    # get_url = lambda url, html_data: url
    # vectorizer_url = TfidfVectorizer(ngram_range=(5, 10), analyzer='char')
    # test = load_csv('data/kaggle_test_data_tab.csv.gz', get_url, total=16039)
    # vectorizer_url.fit([item.features for item in test])
    # train = load_csv('data/kaggle_train_data_tab.csv.gz', get_url, total=7044)
    # X_url = vectorizer_url.fit_transform([item.features for item in train])
    # print(">>> url vectorizer fitted <<<")

    clf = SGDClassifier(max_iter=1000, tol=1e-4)
    train = load_csv('data/kaggle_train_data_tab.csv.gz', skip_feature, total=7044)
    # clf.fit(scipy.sparse.hstack((X, X_url), format='csr'), np.array([item.is_spam for item in train]))
    clf.fit(X, np.array([item.is_spam for item in train]))
    print('>>> classifier fitted <<<')

    test = load_csv('data/kaggle_test_data_tab.csv.gz', get_html, total=16039)
    X_test = vectorizer.transform([item.features for item in test])
    # test = load_csv('data/kaggle_test_data_tab.csv.gz', get_url, total=16039)
    # X_url_test = vectorizer_url.transform([item.features for item in test])
    # X_test = scipy.sparse.hstack((X_test, X_url_test), format='csr')

    with open('submission.txt', 'w') as f:
        f.write('Id,Prediction\n')
        test = load_csv('data/kaggle_test_data_tab.csv.gz', skip_feature, total=16039)
        for i, item in enumerate(test):
            f.write(f'{item.doc_id},{clf.predict(X_test[i])[0]:b}\n')


if __name__ == '__main__':
    main()
