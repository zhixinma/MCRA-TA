import re
import nltk
import os
import pandas as pd
import spacy
from collections import defaultdict
from datetime import date
from nltk.stem.lancaster import LancasterStemmer
from tqdm import tqdm
from spacytextblob.spacytextblob import SpacyTextBlob

NLP = spacy.load('en_core_web_sm')
NLP.add_pipe('spacytextblob')
STOPWORDS = NLP.Defaults.stop_words

def get_emo_text(texts):
    texts = [NLP(text) if type(text)!=float else NLP("") for text in tqdm(texts)]
    return [(doc._.blob.polarity, doc._.blob.subjectivity) for doc in texts]

def process_text(texts):
    return  [[word for word in ''.join(e if (e.isalnum() or e==" ") else " " 
                                       for e in re.sub('-\n',' ',t)).lower().split()
             if word not in STOPWORDS]
            if type(t)!=float else "" for t in texts]

def get_phrases(outputs, threshold):
    single_count = defaultdict(int)
    tuple_count = defaultdict(int)

    for output in outputs:
        for text in output:
            if len(text) == 0:
                continue
            single_count[text[0]] += 1
            for i in range(1,len(text)):
                tuple_count[(text[i-1],text[i])] += 1
                single_count[text[i]] += 1

    single_count = dict(single_count)
    tuple_count = dict(tuple_count)

    # calculate probability word appears given previous word
    cond_prob = defaultdict(dict)
    for k,v in tuple_count.items():
        w1,w2 = k
        cond_prob[w2][w1] = v/single_count[w1]
    cond_prob = dict(cond_prob)

    new_outputs = []
    for output in outputs:
        new_output = []
        for text in output:
            new_text = []
            if len(text) == 0:
                new_output.append(text)
                continue
            add_next = text[0]
            for i in range(1,len(text)):
                if text[i-1] not in cond_prob[text[i]]:
                    new_text.append(add_next)
                    add_next=text[i]
                elif cond_prob[text[i]][text[i-1]]<threshold:
                    new_text.append(add_next)
                    add_next=text[i]
                else:
                    add_next += " " + text[i]

            new_output.append(new_text)
        new_outputs.append(new_output)

    # count again
    new_single_count = defaultdict(int)
    for output in new_outputs:
        for text in output:
            for i in range(0,len(text)):
                new_single_count[text[i]] += 1
    new_single_count = sorted( dict(new_single_count).items(), reverse=True, key=lambda x:x[1])
    new_single_count = {k:v for k,v in new_single_count if len(k)>1}

    # stem words to choose the most used 
    st = LancasterStemmer()
    word2stem = {key: tuple([st.stem(w) for w in key.split()]) for key in new_single_count}
    stem2words = defaultdict(list)
    for k,v in word2stem.items():
        stem2words[v].append(k)
    stem2words = dict(stem2words)
    stem2words = {k:sorted(v,key=lambda x:new_single_count[x]) for k,v in stem2words.items()}
    newer_single_count = {}
    for k,v in stem2words.items():
        newer_single_count[v[-1]] = sum([new_single_count[w] for w in v])
        
    return {k:v for k,v in newer_single_count.items() if v > 1}

def get_emo(df, headers):
    emo = [oo for o in [list(zip(*get_emo_text(df[header].values.tolist())))  for header in headers]
           for oo in o]
    output_headers = [prefix+header for header in headers for prefix in ['polarity_','subjectivity_']]
    output_df = pd.DataFrame.from_dict({output_headers[i]:list(emo[i]) for i in range(len(output_headers))})
    return output_df


def main():
    # ------------------ define input and output files -------------------------
    WEEK_NUM = "01"
    OUTPUT_DIR = f"Analysis/M15W{WEEK_NUM} ({date.today()})"
    INPUT_DIR = f"M15W{WEEK_NUM}"
    learn_file_es = f"ESM6W{WEEK_NUM}-Learn"
    topic_file_es = f"ESM6W{WEEK_NUM}-Topics"
    learn_file = f"M15W{WEEK_NUM}-Learn"
    topic_file = f"M15W{WEEK_NUM}-Topics"
    # --------------------------------------------------------------------------

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    learn = pd.read_csv(f"{INPUT_DIR}/{learn_file_es}.csv")
    learn2r = get_phrases([process_text(learn['comments'].values.tolist())],.2)
    pd.DataFrame(learn2r.items()).to_csv(f"{OUTPUT_DIR}/{learn_file_es}_phrases.csv",header=None, index=None)
    learn_emo = get_emo(learn, ['comments'])
    learn_emo.to_csv(f"{OUTPUT_DIR}/{learn_file_es}_emo.csv")

    topic = pd.read_csv(f"{INPUT_DIR}/{topic_file_es}.csv")
    topic2r = get_phrases([process_text(topic['comments'].values.tolist())],.2)
    pd.DataFrame(topic2r.items()).to_csv(f"{OUTPUT_DIR}/{topic_file_es}_phrases.csv",header=None, index=None)

    learn2 = pd.read_csv(f"{INPUT_DIR}/{learn_file}.csv")
    learn2r2 = get_phrases([process_text(learn2['comments'].values.tolist())],.2)
    pd.DataFrame(learn2r2.items()).to_csv(f"{OUTPUT_DIR}/{learn_file}_phrases.csv",header=None, index=None)
    learn_emo2 = get_emo(learn2, ['comments'])
    learn_emo2.to_csv(f"{OUTPUT_DIR}/{learn_file}_emo.csv")

    topic2 = pd.read_csv(f"{INPUT_DIR}/{topic_file}.csv")
    topic2r2 = get_phrases([process_text(topic2['comments'].values.tolist())],.2)
    pd.DataFrame(topic2r2.items()).to_csv(f"{OUTPUT_DIR}/{topic_file}_phrases.csv",header=None, index=None)


if __name__ == "__main__":
    main()