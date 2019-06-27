import os

class mm_tokenizer():
    def __init__(self,dict = None):
        if not dict:
            dict = './dic.txt'
        self._init_dict(open(dict,encoding='utf8'))


    def _init_dict(self,dic_file):
        self.tok_dict = set()
        self.max_len = 0
        while True:
            line = dic_file.readline().strip()
            if len(line)<1:
                break
            self.max_len = max(len(line),self.max_len)
            self.tok_dict.add(line)

    def tokenize(self,string,maxlen = -1,reverse = False):
        if maxlen <=0:
            maxlen = self.max_len
        tokens = ''
        sentence = string
        while len(sentence)>0:
            len_w = min(len(sentence),maxlen)
            if reverse:
                word = sentence[-len_w:]
            else:
                word = sentence[:len_w]

            while not(word in self.tok_dict or len(word)<=1):
                if reverse:
                    word = word[1:]
                else:
                    word = word[:-1]

            if reverse:
                tokens = word + '/' + tokens
                sentence = sentence[:-len(word)]
            else:
                tokens = tokens + word + '/'
                sentence = sentence[len(word):]
        return tokens

if __name__ =='__main__':
    token = mm_tokenizer()
    print(token.tokenize('她说的确实在理'))
    print(token.tokenize('她说的确实在理',reverse=True))