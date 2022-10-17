import json
import jieba
from collections import Counter
import re


class Parser:
    stop_list = "../dataset/stopword.txt"

    def __init__(self, text: str):
        # text is a book/movie information
        self.data = text
        self.freq = {}
        self.stop_words = []
        with open(Parser.stop_list, 'r', encoding='utf-8') as stoplst:
            for line in stoplst.readlines():
                self.stop_words.append(line.strip())

    def document2sentence(self):
        self.data = re.sub('[\n\r\t ]|', '', self.data)
        self.data = re.sub('[（](.*?)[）]', '', self.data)
        if isinstance(self.data, str):
            pass
        else:
            raise ValueError
        self.data = self.data.strip()
        sentence = re.split('(。|！|\!|\.|？|\?|，|\,|、)', self.data)
        sentence = [sentence[2 * i] for i in range(len(sentence) // 2)]
        self.data = sentence

    def sentence2token(self):
        words = []
        for each in self.data:
            words += jieba.cut(each)
        self.data = words

    def stop_word(self):
        clean = []
        for each_word in self.data:
            if each_word not in self.stop_words:
                clean.append(each_word)
        self.data = clean

    def word_freq(self):
        self.freq = Counter(self.data)

    def simply_word(self):
        self.data = list(set(self.data))

    def process_word(self):
        self.document2sentence()
        self.sentence2token()
        self.stop_word()
        self.word_freq()
        self.simply_word()
        return self.data, self.freq
