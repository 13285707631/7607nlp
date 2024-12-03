import re
import baseline
import time
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def delete_extra_zero(n):
    '''Delete the extra 0 after the decimal point'''
    try:
        n=float(n)
    except:
        # print("None {}".format(n))
        return n
    if isinstance(n, int):
        return str(n)
    if isinstance(n, float):
        n = str(n).rstrip('0')  # 删除小数点后多余的0
        n = int(n.rstrip('.')) if n.endswith('.') else float(n)  # 只剩小数点直接转int，否则转回float
        n=str(n)
        return n


def extract_ans_from_response(answer: str, eos=None):
    '''
    :param answer: model-predicted solution or golden answer string
    :param eos: stop token
    :return:
    '''
    if eos:
        answer = answer.split(eos)[0].strip()

    answer = answer.split('####')[-1].strip()

    for remove_char in [',', '$', '%', 'g']:
        answer = answer.replace(remove_char, '')

    try:
        return int(answer)
    except ValueError:
        return answer



if __name__ == '__main__':

    start_time = time.time()
    answers,res_zero,res_few,num=baseline.train(1)
    correct_count_zero=0
    correct_count_few=0
    length=len(res_zero)
    count = length
    count_num=0
    for i in range(length):
        #print('questions',answers[i])
        answer = extract_ans_from_response(res_zero[i])
        few_answer=extract_ans_from_response(res_few[i])
        #print('few_answer',few_answer)
        t_answer=extract_ans_from_response(answers[i])
        t_answer = delete_extra_zero(t_answer)
        # print('type of answer',str(answer))
        if len(re.findall(r'-?\d+(?:\.\d+)?(?:/\d+)?', str(answer)))!=0:
            answer = re.findall(r'-?\d+(?:\.\d+)?(?:/\d+)?', str(answer))[0]
            answer = delete_extra_zero(answer)
            if t_answer == answer:
                correct_count_zero += 1
            else:
                print('i answer,t_answer', i, answer, t_answer)
        if len(re.findall(r'-?\d+(?:\.\d+)?(?:/\d+)?', str(few_answer)))!=0:
            few_answer=re.findall(r'-?\d+(?:\.\d+)?(?:/\d+)?', str(few_answer))[0]
            few_answer = delete_extra_zero(few_answer)
            if few_answer == t_answer:
                correct_count_few += 1
            else:
                print('i few answer,t_answer', i, few_answer, t_answer)
    print('zero accuracy',float(correct_count_zero)/count)
    print('few accuracy', float(correct_count_few) / count)
    print('few_nun',num)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"runing time ：{elapsed_time}秒")