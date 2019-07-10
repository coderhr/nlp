import os
import numpy as np
import pickle

test_file_path = './test2.txt'


if __name__ == '__main__':
    with open(test_file_path,encoding='utf-8') as file:
        test_out_lines = file.readlines()
    line_nums = 0
    match_word_start = False
    prec_word_start = False
    prec_cls = ''
    matches = 0
    prec_nums = 0
    label_nums = 0
    for line in test_out_lines:
        segs = line.strip().split('\t')
        if len(segs) <= 1:
            line_nums += 1
            continue
        character = segs[0]
        label = segs[-2]
        prec = segs[-1]
        if label == 'O' and prec == 'O':
            continue
        else:
            if label !='O':
                if label[0]=='B':
                    label_word = character
                    label_cls = label[2:]
                    if label == prec:
                        match_word_start = True
                    else:
                        match_word_start = False
                elif label[0]=='M':
                    if label != prec:
                        match_word_start = False
                elif label[0] == 'E':
                    label_nums +=1
                    if label == prec and match_word_start:
                        matches += 1
                    match_word_start = False
                elif label[0] == 'W':
                    label_nums +=1
                    if label == prec:
                        matches +=1

            if prec !='O':
                if prec[0] == 'W':
                    prec_nums+=1

                elif prec[0]=='B':
                    prec_cls = label[2:]
                    prec_word_start = True
                elif prec[0]=='M':
                    if prec[2:]!=prec_cls:
                        prec_word_start = False
                elif prec[0] == 'E':
                    if prec[2:]!=prec_cls:
                        prec_word_start = False
                    if prec_word_start:
                        prec_nums+=1
                    prec_word_start = False

            else:
                if prec_word_start:
                    prec_word_start = False

    print('*******TEST RESULT*******')
    print('Test lines:{}'.format(line_nums))
    print('Total noun words:{}'.format(label_nums))
    print('Predicted words:{}'.format(prec_nums))
    print('Precision:{:.2f} %'.format(matches/prec_nums*100))
    print('Recall:{:.2f} %'.format(matches/label_nums*100))