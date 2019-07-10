import os
import time
import pickle
import re

train_path = './train2.txt'

ner2label_dict = {'nr':'PER',\
                  'ns':'LOC',\
                  'nt':'ORG'}


test_ratio = 0.3

def get_indicate_words(half_window_size=2,threshold=20):
    print('start_processing_indicate_word')
    ner_indic_dict = {} #'nr'/'nt'/ : word:freq
    with open(train_path,'r',encoding='utf-8') as file:
        lines = file.readlines()

    # process long_word to be as short word
    for idx,line in enumerate(lines):
        while True:
            long_words_search = re.search('\[.+?\].+?\s', line)
            if not long_words_search :
                break
            st,ed = long_words_search.span()
            long_word,label = line[st:ed].split(']')
            long_word = long_word.split('[')[1]
            line = line[:st]+connect_long_word(long_word=long_word)+'/'+label+line[ed-1:]
            lines[idx] = line

    for line_idx,line in enumerate(lines):
        if(line_idx % 1000000==0):
            print('now processing line:{}'.format(line_idx))
        words = line[23:].strip().split(' ')
        words = [word for word in words if word !='']
        for idx,word in enumerate(words):
            word,label = word.split('/')

            if label in ner2label_dict:
                window_left = max(-idx,-half_window_size)
                window_right = min(len(words)-1-idx,half_window_size)

                for indic_idx in range(window_left,window_right+1):
                    if indic_idx!=0:
                        indic_word = words[indic_idx+idx]
                        indic_word = indic_word.split('/')[0]
                        word_freq_dict = ner_indic_dict.setdefault(label, {})
                        word_freq_dict[indic_word] = word_freq_dict.get(indic_word,0)+1

    for label in ner_indic_dict:
        indic_freq_dict = ner_indic_dict[label]
        for word in list(indic_freq_dict.keys()):
            if indic_freq_dict[word]<threshold:
                indic_freq_dict.pop(word)

    # return indic_word_sets
    indic_freq_sets = {}
    for label in ner2label_dict:
        indic_freq_sets[label] = set(list(ner_indic_dict[label].keys()))
    print('processing_indicate_word_complete!')
    return indic_freq_sets

def connect_long_word(long_word = ''):
    long_word = [x.split('/')[0] for x in long_word.strip().split(' ')]
    return ''.join(long_word)


def data_preprocess(process_lines, indic_dict, output_path):
    # process long_word to be as short word
    print('start processing {}'.format(output_path))
    with open(output_path,'w',encoding = 'utf-8') as out_file:
        for idx, line in enumerate(process_lines):
            if (idx % 5000 == 0):
                print('now processing line:{}'.format(idx))

            while True:
                long_words_search = re.search('\[.+?\].+?\s', line)
                if not long_words_search:
                    break

                st, ed = long_words_search.span()
                long_word, label = line[st:ed].split(']')
                long_word = long_word.split('[')[1]
                line = line[:st] + connect_long_word(long_word=long_word) + '/' + label + line[ed - 1:]
                process_lines[idx] = line

        for line_idx,line in enumerate(process_lines):

            words = line[23:].strip().split(' ')
            words = [word for word in words if word != '']
            for idx, word in enumerate(words):
                word, label = word.split('/')
                indic_flags = ['Y' if word in indic_dict[label] else 'N' for label in ner2label_dict]
                # {character}\t{edge}\t{flags}\t{train_label}\n
                if len(word)==1:
                    edges = ['W']
                else:
                    edges = ['B']+['M']*max(len(word)-2,0)+['E']

                if label in ner2label_dict:
                    cls = ner2label_dict[label]
                    train_labels = [edge+'_'+cls for edge in edges]
                else:
                    train_labels = ['O']*len(word)

                for char_idx,character in enumerate(word):
                    line_to_write = '{}\t{}\t{}\t{}\n'.format(character,edges[char_idx],'\t'.join(indic_flags),train_labels[char_idx])
                    out_file.writelines(line_to_write)

            out_file.writelines('\n')

if __name__ == '__main__':
    ner_indic_dict = get_indicate_words()
    with open('./indic_dict.pkl','wb') as file:
         pickle.dump(ner_indic_dict,file,2)

    #with open('./indic_dict.pkl','rb') as file:
    #ner_indic_dict = pickle.load(file)

    with open(train_path,encoding='utf-8') as file:
        doc_lines = file.readlines()

    test_nums = int(len(doc_lines) * test_ratio)
    train_lines = doc_lines[:-test_nums]
    test_lines = doc_lines[-test_nums:]
    data_preprocess(train_lines,ner_indic_dict,'./train.txt')
    data_preprocess(test_lines,ner_indic_dict,'./test.txt')


