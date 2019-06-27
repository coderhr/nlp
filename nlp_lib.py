# nlp_lib.py
# Author: liurui
# Date: 2019/6/15
import time

def getDict(path):
    "read dict file, return hash map"
    max_length = 0
    dict = {}
    file = open(path, 'r', encoding='GB2312')
    
    for line in file:
        line = line.strip()
        max_length = max(max_length, len(line))

        if (len(line) == 0):
            continue
        if not line[0] in dict:
            dict[line[0]] = []
        dict[line[0]].append(line)

    print("max word length = ", max_length)
    return dict

def MM(text, dict):
    ret = []
    index = 0
    maximum = 8

    while index < len(text):
        word = None
        for size in range(maximum, 0, -1):
            if index+size > len(text):
                continue

            piece = text[index: index+size]
            if piece[0] in dict and piece in dict[piece[0]]:
            # if piece in dict:
                word = piece
                ret.append(word)
                index += size
                break
        if word is None:
            index += 1
    return ret

def RMM(text, dict):
    ret = []
    index = len(text)
    maximum = 8

    while index > 0:
        word = None
        for size in range(maximum, 0, -1):
            if index - size < 0:
                continue

            piece = text[(index - size): index]
            if piece[0] in dict and piece in dict[piece[0]]:
            # if piece in dict:
                word = piece
                ret.append(word)
                index -= size
                break
        if word is None:
            index -= 1
    ret.reverse()
    return ret

def get_corpus_dict_and_transition_matrix(path, states):
    file = open(path, 'r', encoding='utf-8')
    corpus_dict = {}
    state_set = set()
    transition_matrix = [[0 for col in range(len(states))] for row in range(len(states))]
    states_cnt = [0 for _ in range(len(states))]

    for line in file:
        line = line.strip().split()
        line = line[1 :]
        pre_part = ""
        sig = 0

        pre_states = []
        for pair in line:
            pair = pair.split('/')
            if len(pair) < 2:
                continue

            word, labels = pair[0], pair[1]
            if len(word) > 1 and word[0] == "[": # 匹配到[
                word = word[1: ]
                sig = 1
            if sig == 1:
                pre_part += word

            labels = labels.split("]")
            label = labels[0]
            
            state_set.add(label)
            # 转移矩阵
            curr_states = labels
            for curr_stat in curr_states:
                states_cnt[states.index(curr_stat)] += 1
                for pre_stat in pre_states:
                    transition_matrix[states.index(pre_stat)][states.index(curr_stat)] += 1 # 对这一条转移频率加一
            pre_states = curr_states
                

            if not word in corpus_dict:
                corpus_dict[word] = {}
            if not label in corpus_dict[word]:
                corpus_dict[word][label] = 0
            corpus_dict[word][label] += 1

            if len(labels) > 1: # 匹配到后半个]
                label = labels[1]
                word = pre_part
                # 插入复合词
                if not word in corpus_dict:
                    corpus_dict[word] = {}
                if not label in corpus_dict[word]:
                    corpus_dict[word][label] = 0
                corpus_dict[word][label] += 1

                pre_states = labels
                pre_part = ""
                sig = 0

    # 处理转移矩阵
    for i in range(len(states)):
        for j in range(len(states)):
            if states_cnt[i] == 0:
                transition_matrix[i][j] = 0
            else:
                transition_matrix[i][j] = transition_matrix[i][j] / states_cnt[i]
    print("词性列表：", state_set)
    return corpus_dict, transition_matrix


def search_word(dict, word):
    '''
    从语料库生成的字典中获取word对应的value
    '''
    ret = {}
    if len(word)==0 or not word[0] in dict:
        return ret
    if not word in dict[word[0]]:
        return ret
    ret = dict[word[0]][word]
    print(ret)
    return ret

def get_word_frequency(dict, word):
    '''
    统计词频
    '''
    # pairs = search_word(dict, word)
    if not word in dict:
        return 0
    pairs = dict[word]
    cnt = 0
    for _, value in pairs.items():
        cnt += value
    
    return cnt

def get_wordxx_frequency(dict, word):
    '''
    统计word开头的词频
    '''
    cnt = 0
    if len(word)==0 or not word[0] in dict:
        return 0
    for key, values in dict[word].items():
        if key.find(word) == 0:
            for _, num in values.items():
                cnt += num
    
    return cnt

def get_word_label_freqency(dict, word, label):
    '''
    统计给定词和词性的频率
    '''
    pairs = search_word(dict, word)
    if label not in pairs:
        return 0
    else:
        return pairs[label]

def calc_transition_matrix(corpus_dict, state):
    "转移概率矩阵"
    transition_matrix = []

    return transition_matrix

def calc_transition_probability(corpus_dict, pre, next):
    "从pre到next的状态转移概率"
    # 这里好像是有一点问题，先放着，重写了一个版本
    numerator = get_word_frequency(corpus_dict, pre+next)
    denominator = get_wordxx_frequency(corpus_dict, pre)
    prob = numerator / denominator
    return prob

def calc_emission_probability(corpus_dict, word, label):
    "计算发射概率"
    numerator = get_word_label_freqency(corpus_dict, word, label)
    denominator = get_word_frequency(corpus_dict, word)
    prob = (numerator+1) / (denominator+len(corpus_dict))
    return prob

def viterbi(corpus_dict, transition_matrix, obser, state, state_idx, start_p):
    '''
    viterbi算法，转移概率和发射概率调用transition_matrix和calc_emission_probability得到
    '''
    max_p = [[0 for col in range(len(state))] for row in range(len(obser))]
    path = [[0 for col in range(len(state))] for row in range(len(obser))]
    # 初始状态
    for i in range(len(state)):
        max_p[0][i] = start_p[i] * calc_emission_probability(corpus_dict, obser[0], state[state_idx[i]])
        path[0][i] = i
    
    for i in range(1, len(obser)):
        max_item = [0 for i in range(len(state))]
        for j in range(len(state)):
            item = [0 for i in state]
            for k in range(len(state)):
                p = max_p[i - 1][k] * transition_matrix[k][j] * calc_emission_probability(corpus_dict, obser[i], state[state_idx[j]])
                item[k] = p
            # 设置概率记录为最大情况
            max_item[j] = max(item)
            path[i][j] = item.index(max(item))
        max_p[i] = max_item

    ret = []
    #判断最后一个时刻哪个状态的概率最大
    p=max_p[len(obser)-1].index(max(max_p[len(obser)-1]))
    ret.append(p)

    for i in range(len(obser) - 1, 0, -1):
        ret.append(path[i][p])
        p = path[i][p]
    ret.reverse()
    return ret

def showDict(dict):
    # keys = dict.keys()
    for item in dict.items():
        print(item[0])
        print(item[1], '\n')

def test(text, dict):
    print("text: ", text)
    words = MM(text, dict)
    rwords = RMM(text, dict)
    
    print("MM: ", words)
    print("RMM: ", rwords)

def total_test(sentence, rflag = 0):
    states = ['t', 'z', 'vvn', 'Dg', 'vn', 'i', 's', 'Vg', 'ns', 'm', 'Tg', 'nt', 'b', 'c', 'Ng', 'Bg', 'e', 'nr', 'nz', 'h', 'an', 'u', 'Yg', 'y', 'q', 'l', 'ad', 'r', 'o', 'k', 'j', 'vd', 'nx', 'Ag', 'Rg', 'Mg', 'n', 'p', 'v', 'd', 'f', 'w', 'na', 'a']
    state_idx = [i for i in range(len(states))]
    start_p = [1/len(states) for _ in range(len(states))]

    dic_path = "./dic.txt"
    corpus_path = "./train2.txt"
    dic = getDict(dic_path)
    pre_time = time.time()
    corpus_dict, transition_matrix = get_corpus_dict_and_transition_matrix(corpus_path, states)
    after_time = time.time()
    print("读取字典耗时：", after_time - pre_time)

    # print("test: ", get_word_frequency(corpus_dict, "香港"))
    # print("test: ", get_word_frequency(corpus_dict, "香港特区"))
    #pre_time = time.time()
    if rflag == 0:
        obser = MM(sentence, dic)
    else:
        obser = RMM(sentence, dic)
    after_time = time.time()
    print("分词速度（词/秒）：", (int)(len(obser) / (after_time-pre_time)))
    print("原句：", sentence)
    print("分词: ", obser)
    # for line in transition_matrix:
    #     print(line)
    labels_idx = viterbi(corpus_dict, transition_matrix, obser, states, state_idx, start_p)
    labels = [states[idx] for idx in labels_idx]
    print("词性: ", labels)
    print()
# if __name__ == '__main__':
#     #   隐状态
#     hidden_state = ['rainy', 'sunny']
#     #   观测序列
#     obsevition = ['walk', 'shop', 'clean']
#     state_s = [0, 1]
#     obser = [0, 1, 2]
#     #   初始状态，测试集中，0.6概率观测序列以sunny开始
#     start_probability = [0.6, 0.4]
#     #   转移概率，0.7：sunny下一天sunny的概率
#     transititon_probability = [[0.7, 0.3], [0.4, 0.6]]
#     #   发射概率，0.4：sunny在0.4概率下为shop
#     emission_probability = [[0.1, 0.4, 0.5], [0.6, 0.3, 0.1]]
#     result = compute(obser, state_s, start_probability, transititon_probability, emission_probability)
#     for k in range(len(result)):
#         print(hidden_state[int(result[k])])
        
if __name__ == "__main__":
#     path = "./dic.txt"
#     dict = getDict(path)

#     # test("他说的的确在理", dict)
#     # test("我好像不太明白", dict)
#     while True:
#         text = input()
#         text = text.strip()
#         if len(text) == 0:
#             break
        
#         test(text, dict)

    total_test("云南全面完成党报党刊任务", rflag = 1)
    total_test("晚上喝水", rflag = 0)
    # labels = viterbi(corpus_dict, obser, state, state_idx, start_p)
    # print("labels: ", labels)
    

    # print("test: ")
    # path = "./train2.txt"
    # corpus_dict = get_corpus_dict(path)

    
    # #打印corpus_dict测试
    # for ch, elem in corpus_dict.items():
    #     print()
    #     for word, pairs in elem.items():
    #         print(word)
    #         print(pairs)


    # # 词频概率测试
    # cnt = get_word_frequency(corpus_dict, "打")
    # label_cnt = get_word_label_freqency(corpus_dict, "打", "v")

    # print(cnt)
    # print(label_cnt)


    # # 转移概率测试
    # prob = get_transition_probability(corpus_dict, "为", "什么")
    # print(prob)
    # # 发射概率测试
    # prob = calc_emission_probability(corpus_dict, "工作", "n")
    # print(prob)