# this script is used to create initial app.db asset from text sources.

# %%

# import pureo_moa
import jamo

johap_moeum = {
    'ᅪ': 'ᅩᅡ',
    'ᅫ': 'ᅩᅢ',
    'ᅬ': 'ᅩᅵ',
    'ᅯ': 'ᅮᅥ',
    'ᅰ': 'ᅮᅦ',
    'ᅱ': 'ᅮᅵ',
    'ᅴ': 'ᅳᅵ',
}

def pureo(s, moeum=False):
    s = jamo.h2j(s)
    if moeum:
        for johap, moeum in johap_moeum.items():
            s = s.replace(johap, moeum)
    return list(s)

def moa_(s):
    s = "".join(s)
    for johap, moeum in johap_moeum.items():
        s = s.replace(moeum, johap)
    return s

def moa(s):
    s = list(moa_(s))
    ret = []
    while s:
        try:
            h = jamo.j2h(*s[:3])
            s = s[3:]
        except jamo.InvalidJamoError:
            h = jamo.j2h(*s[:2])
            s = s[2:]
        ret.append(h)
    return "".join(ret)


# pureo('꽗쒸')
# list(moa(pureo('꽗쒸')))
# jamo.j2h('ᄁ', 'ᅪ', 'ᄊ')

# %%
import re

def extract_from_plaintext(path):
    with open(path, 'rt') as f:
        text = f.read()

    hangule_text = re.sub(r'[^\uAC00-\uD7A3]', ' ', text)

    def remove_josa(word):
        josas = ['은','는','이','가','을','를','의','으로','도','들이','들을','들의']
        for josa in josas:
            if word.endswith(josa):
                return word.removesuffix(josa)
        return word

    for word in hangule_text.split():
        clean = remove_josa(word) 
        if len(clean) > 1:
            yield clean

def load_from_texts():
    words = set()
    words.update(extract_from_plaintext('공산당 선언.txt'))
    words.update(extract_from_plaintext('산업사회와 그 미래.txt'))
    words.update(extract_from_plaintext('세계인권선언.txt')) # 제 78 조 같은 거는 숫자 제외, 한 글자 단어 제외로 잘려나갈거임
    words.update(extract_from_plaintext('사회계약론.txt'))
    words.update("넋두리 뱃삯 핥다 훑다 홅다 훑어보기 개미핥기 읊다 읊어 읊조리다 곬 물곬 외곬 통곬 옰".split())
    return words

# %%
import json

def extract_from_termsfile(path):
    with open(path, "rt") as f:
        ret = json.load(f)

    for term in ret['terms']:
        yield from term['form'].replace('^', ' ').split()
        for rel in term['related_terms']:
            yield from rel['form'].replace('^', ' ').split()

def extract_from_graphfile(path):
    with open(path, "rt") as f:
        ret = json.load(f)

    for edge in ret['termList']:
        yield from edge['start_word'].replace('^', ' ').split()
        yield from edge['end_word'].replace('^', ' ').split()

def load_from_onyong():
    words = set()

    words.update(w for w in extract_from_termsfile("철학_용어_내려받기_20260604000001.json") if len(w) > 1)
    words.update(w for w in extract_from_termsfile("경제_용어_내려받기_20260604000815.json") if len(w) > 1)
    words.update(w for w in extract_from_termsfile("경제_용어_내려받기_20260604000248.json") if len(w) > 1)
    words.update(w for w in extract_from_termsfile("경제_용어_내려받기_20260604000247.json") if len(w) > 1)
    words.update(w for w in extract_from_termsfile("경제_용어_내려받기_20260604000244.json") if len(w) > 1)

    words.update(w for w in extract_from_graphfile("가족_지식_그래프_목록_20260603234553.json") if len(w) > 1)
    words.update(w for w in extract_from_graphfile("건축_지식_그래프_목록_20260603234614.json") if len(w) > 1)
    words.update(w for w in extract_from_graphfile("민간신앙_지식_그래프_목록_20260603234724.json") if len(w) > 1)
    words.update(w for w in extract_from_graphfile("민속인류_지식_그래프_목록_20260603234743.json") if len(w) > 1)
    words.update(w for w in extract_from_graphfile("식생활_지식_그래프_목록_20260603234818.json") if len(w) > 1)
    words.update(w for w in extract_from_graphfile("주생활_지식_그래프_목록_20260603234327.json") if len(w) > 1)

    return words

# %%
onyong_words = load_from_onyong()
text_words = load_from_texts()

print(
    len(onyong_words - text_words),
    len(onyong_words.intersection(text_words)),
    len(text_words - onyong_words)
)

# with open("../assets/wordset.list", "wt") as f:
#     for w in onyong_words.union(text_words):
#         f.write(w)
#         f.write('\n')

# %%
# try to learn new gulso from most frequent to lease frequent for practice word diversity
from collections import Counter
gp_onyong = Counter(gulsoe for word in onyong_words for gulsoe in pureo(word)).most_common()
gp_text = Counter(gulsoe for word in text_words for gulsoe in pureo(word)).most_common()
gp_both = Counter(gulsoe for word in onyong_words.union(text_words) for gulsoe in pureo(word)).most_common()

def index_by(it, pred):
    for i,x in enumerate(it):
        if pred(x):
            return i

def gulsoe_popularity(gulsoe):
    def find(ls):
        idx = index_by(ls, lambda x: x[0] == gulsoe)
        if idx is not None:
            return (idx, ls[idx][1])
        else:
            return (-1, 0)
    return (find(gp_onyong), find(gp_both), find(gp_text))

# %%
def shufle_gen_fixed(gulzas):
    if len(gulzas) == 2:
        return "a b aa bb aaa bbb aaaa bbbb aabb bbaa aaba bbab aba aba bab bab abba baab abab baba a b a b" \
            .replace('a', gulzas[0]) \
            .replace('b', gulzas[1]) \
            .split()

    if len(gulzas) == 3:
        return "a b c aa bb cc aaa bbb ccc aabb ccaa bbcc aacc bbaa ccbb abc bca cab bac acb cba abac bcab cabc bcba acba caba bacb acab cbac a b c" \
            .replace('a', gulzas[0]) \
            .replace('b', gulzas[1]) \
            .replace('c', gulzas[2]) \
            .split()

    if len(gulzas) == 4:
        return "a b c d aa bb cc dd aabb ccdd ddaa bbcc ccbb abc bda bca dbc cab cda bac adb acb cbd cba acd abac abdc bcab bcda cabc cdab bcba dacb acba bacd caba dbca bacb cdba acab bdad cbac dbca a b c d" \
            .replace('a', gulzas[0]) \
            .replace('b', gulzas[1]) \
            .replace('c', gulzas[2]) \
            .replace('d', gulzas[3]) \
            .split()

    if len(gulzas) == 5:
        return "a b c d e aa bb cc dd ee aabb ccdd eeaa ddbb eecc abc bda ebc bca dbc ace cab cda dce bac adb bec acb cbd ebd cba eac acd abac abdc aceb bcab bcda edbc cabc cdab ceba bcba dacb aebc acba bacd eabc caba dbca bacb becd cdba acab bdad cbac dbca a b c d e" \
            .replace('a', gulzas[0]) \
            .replace('b', gulzas[1]) \
            .replace('c', gulzas[2]) \
            .replace('d', gulzas[3]) \
            .replace('e', gulzas[4]) \
            .split()

# %%
def check_danwoe(allowed, required, word, max_coupled_range=(0,3)):
    if not isinstance(max_coupled_range, tuple):
        max_coupled_range = (max_coupled_range, max_coupled_range)

    if allowed and not all(gulsoe in allowed for gulsoe in pureo(word)):
        return None

    def filter_jamos(jamos, pred):
        return [ jamo for jamo in jamos if jamo in pred ]

    profile_by_gulza = [
        [ filter_jamos(pureo(gulza), req) for req in required ]
        for gulza in word
    ]

    # print(list(zip(word,profile_by_gulza)))

    # ensure each gulza satisfies more than 'coupled' requirements
    coupled = []
    for profile in profile_by_gulza:
        passed_req_num = sum(
            len(filtered) > 0
            for filtered in profile
        )
        coupled.append(passed_req_num)
    if len(required) > 0:
        if max(coupled) < max_coupled_range[0] or max_coupled_range[1] < max(coupled):
            return None

    # ensure all the requirements are satisfied at least once
    passed_reqs = set(
        i
        for profile in profile_by_gulza
        for i, filtered in enumerate(profile)
        if len(filtered)>0)
    # print(passed_reqs)
    if len(passed_reqs) != len(required):
        return None

    found = set(
        gulsoe
        for profile in profile_by_gulza
        for filtered in profile
        for gulsoe in filtered
    )

    return found

def filter_words(words, allowed, required, max_coupled_range=(0,3)):
    for word in words:
        found = check_danwoe(allowed, required, word, max_coupled_range=max_coupled_range)
        if found is not None:
            yield word, found

# %%
import math
import random

# probabilistic version (random variance)
def balanced_sample_rand(elements, K, M, alpha=2.0, initial_temperature=1.0):
    """
    elements: list of lists of property indices
    K: number of properties
    M: number of selections (multiset size)
    alpha: duplicate penalty weight
    
    Returns:
        selected_indices: list of chosen element indices (with duplicates)
        property_counts: final property counts
    """
    N = len(elements)
    avg_r = sum(len(e) for e in elements) / N
    target = M * avg_r / K

    property_counts = [0] * K
    usage_counts = [0] * N
    selected_indices = []

    for step in range(M):
        scores = []

        for i, props in enumerate(elements):
            delta_balance = 0.0
            for j in props:
                before = property_counts[j] - target
                after = (property_counts[j] + 1) - target
                delta_balance += after**2 - before**2

            dup_penalty = alpha * (usage_counts[i] ** 2)
            score = delta_balance + dup_penalty
            scores.append(score)

        # --- Softmax sampling ---
        min_score = min(scores)
        shifted = [s - min_score for s in scores]  # improve stability

        temperature = initial_temperature * (0.95 ** step) 
        weights = [math.exp(-s / temperature) for s in shifted]
        total = sum(weights)
        probs = [w / total for w in weights]

        chosen = random.choices(range(N), weights=probs, k=1)[0]

        selected_indices.append(chosen)
        usage_counts[chosen] += 1
        for j in elements[chosen]:
            property_counts[j] += 1

    return selected_indices, property_counts

# deterministic version
def balanced_sample_det(elements, K, M, alpha=2.0):
    """
    elements: list of lists of property indices
    K: number of properties
    M: number of selections (multiset size)
    alpha: duplicate penalty weight
    
    Returns:
        selected_indices: list of chosen element indices (with duplicates)
        property_counts: final property counts
    """
    N = len(elements)
    
    # Estimate average properties per element
    avg_r = sum(len(e) for e in elements) / N
    
    # Ideal equal target per property
    target = M * avg_r / K
    
    # Current state
    property_counts = [0] * K
    usage_counts = [0] * N
    selected_indices = []

    for step in range(M):
        best_score = float("inf")
        best_i = None
        
        for i, props in enumerate(elements):
            
            # ---- Balance delta ----
            delta_balance = 0.0
            for j in props:
                before = property_counts[j] - target
                after = (property_counts[j] + 1) - target
                delta_balance += after**2 - before**2
            
            # ---- Duplicate penalty ----
            dup_penalty = alpha * (usage_counts[i] ** 2)
            
            score = delta_balance + dup_penalty
            
            if score < best_score:
                best_score = score
                best_i = i
        
        # Update with chosen element
        selected_indices.append(best_i)
        usage_counts[best_i] += 1
        
        for j in elements[best_i]:
            property_counts[j] += 1
    
    return selected_indices, property_counts

# run-length-encode
def rle(arr):
    if not arr: return []

    result = []
    current_value = arr[0]
    count = 1

    for x in arr[1:]:
        if x == current_value:
            count += 1
        else:
            result.append((current_value, count))
            current_value = x
            count = 1

    result.append((current_value, count))
    return result

def view_practice_set(
        wordsets, allowed, required,
        alpha=10.0, temp=1.0,
        max_coupled_range=(0,3), misc=None
    ):
    req_list = list(set(gulsoe for req in required for gulsoe in req))

    wordset_all = set()
    for wordset in wordsets:
        wordset_all.update(wordset)

    words, word_props = zip(*filter_words(wordset_all, allowed, required, max_coupled_range=max_coupled_range))
    req_stat = Counter(gulsoe for prop in word_props for gulsoe in prop)
    word_props = [
        [ req_list.index(gulsoe) for gulsoe in prop ]
        for prop in word_props
    ]
    sel_indexes, cnt = balanced_sample_rand(word_props, len(req_list), misc[1], alpha, initial_temperature=temp)
    print(f"{misc[1]}/{len(words)}")
    print([f"{words[idx]} {n if n > 1 else ''}" for idx, n in sorted(rle(sorted(sel_indexes)), key=lambda x: x[1], reverse=True)])
    print(', '.join(
        f"{gulsoe}: {n}/{req_stat[gulsoe]}"
        for n, gulsoe in sorted(zip(cnt, req_list), reverse=True)
    ))

    return [ words[idx] for idx in sorted(sel_indexes) ]

def practice_set_from_wordset(*args, **kwargs):
    view_practice_set(*args, **kwargs)

    reqacc = set()
    for req in args[2]:
        dup = reqacc.intersection(req)
        if dup: raise Exception(f"duplication found for {kwargs['misc'][0]}: {dup}")
        reqacc.update(req)

def practice_set_from_fixed(title, gulzas):
    print(gulzas)

def practice_set_from_rand(title, num, gulzas):
    print(gulzas)

# %%
class Practice:
    def __init__(self, name):
        self.practices = []
        self.name = name

    def add_practice_set(self,
        wordsets, allowed, required,
        alpha=10.0, temp=1.0,
        max_coupled_range=(0,3), misc=None
    ):

        if not isinstance(max_coupled_range, tuple):
            (max_coupled_min, max_coupled_max) = (max_coupled_range, max_coupled_range)
        else:
            (max_coupled_min, max_coupled_max) = max_coupled_range

        self.practices.append({
            'type': 'words',
            'title': misc[0],
            'num': misc[1],
            'allowed': ''.join(set(allowed)),
            'required': ' '.join(''.join(set(req)) for req in required),
            'alpha': alpha,
            'temp': temp,
            'mc_min': max_coupled_min,
            'mc_max': max_coupled_max,
        })
    
    def add_fixed_words(self, title, words):
        self.practices.append({
            'type': 'fixed_gulza',
            'title': title,
            'num': len(words),
            'words': ' '.join(words),
        })

    def add_rand_gulza(self, title, num, gulzas):
        self.practices.append({
            'type': 'rand_gulza',
            'title': title,
            'num': num,
            'gulzas': ''.join(gulzas),
        })

# %%
practice = Practice("세모e 2018")

def practice_set_from_wordset(*args, **kwargs):
    practice.add_practice_set(*args, **kwargs)

def practice_set_from_fixed(title, gulzas):
    practice.add_fixed_words(title, gulzas)

def practice_set_from_rand(title, num, gulzas,):
    practice.add_rand_gulza(title, num, gulzas)

# %% =====================================================================
# 단타입력

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가'),
    [pureo('이가')],
    misc=("ㅇㄱ + ㅣㅏ [j k + d f]", 20)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가하자'),
    [pureo('이가하자')],
    temp=0.1,
    misc=("ㅎㅇㄱㅈ + ㅣㅏ [h j k l + d f]", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장'),
    [pureo('한장')[2::3]],
    misc=("+/ㅇㄴ [as]", 30)
)

# %% ----------------------------------------------
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장'),
    [pureo('이가한장')],
    misc=("ㅎㅇㄱㅈ +ㅣㅏ +/ㅇㄴ", 60)
)

# %%
practice_set_from_fixed("(자리) ㅁㄴ [y u]", shufle_gen_fixed('마나'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장마나'),
    [pureo('머녀')[0::2]],
    misc=("+ㅁㄴ", 40)
)

# %%
practice_set_from_fixed('(자리) ㅓㅕ [r t]', shufle_gen_fixed('어여'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장어여'),
    [pureo('어여')[1::2]],
    misc=("+ㅓㅕ", 40)
)

# %% -----------------------------------------------
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀'),
    [pureo('머녀')[0::2], pureo('어여')[1::2]],
    max_coupled_range=1,
    misc=("+ㅁㄴㅓㅕ ①", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀'),
    [pureo('머녀')[0::2], pureo('어여')[1::2]],
    max_coupled_range=2,
    misc=("+ㅁㄴㅓㅕ ②", 60)
)

# %%
practice_set_from_fixed('(자리) ㅅㄹ [n m]', shufle_gen_fixed('사라'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장사라'),
    [pureo('사라')[::2]],
    misc=("+ㅅㄹ", 30)
)

# %%
practice_set_from_fixed('(자리) ㅗㅜ [v b]', shufle_gen_fixed('오우'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장오우'),
    [pureo('오우')[1::2]],
    misc=("+ㅗㅜ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀'),
    [pureo('머녀')[0::2], pureo('어여')[1::2]],
    misc=("+ㅁㄴㅓㅕ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀사라'),
    [pureo('사라')[::2]],
    misc=("+ㅁㄴㅅㄹ +ㅓㅕ", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀오우'),
    [pureo('오우')[1::2]],
    misc=("+ㅁㄴ +ㅓㅕㅗㅜ", 60)
)

# %% -------------------------------------------------------
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루'),
    [pureo('사라')[0::2], pureo('오우')[1::2]],
    max_coupled_range=1,
    misc=("+ㅁㄴㅅㄹ+ㅓㅕㅗㅜ ①", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루'),
    [pureo('사라')[0::2], pureo('오우')[1::2]],
    max_coupled_range=2,
    misc=("+ㅁㄴㅅㄹ+ㅓㅕㅗㅜ ②", 60)
)

# %%
practice_set_from_fixed('(자리) ㄷㅂ [i o]', shufle_gen_fixed('다바'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루다바'),
    [pureo('다바')[::2]],
    misc=("+ㄷㅂ", 30)
)

# %%
practice_set_from_fixed('(자리) /ㄹㄱ [e x]', shufle_gen_fixed('알악'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루알악'),
    [pureo('알악')[2::3]],
    misc=("+/ㄹㄱ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박'),
    [pureo('다바')[::2], pureo('알악')[2::3]],
    max_coupled_range=1,
    misc=("+ㄷㅂ +/ㄹㄱ ①", 60)
)

# %% ----------------------------------------------------
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박'),
    [pureo('다바')[::2], pureo('알악')[2::3]],
    max_coupled_range=2,
    misc=("+ㄷㅂ +/ㄹㄱ ②", 60)
)

# %%
practice_set_from_fixed('(자리) /ㅅㅂㅁ [q w z]', shufle_gen_fixed('앗압암'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루앗압암'),
    [pureo('앗압암')[2::3]],
    misc=("+/ㅅㅂㅁ 1", 30)
)

# %%
practice_set_from_fixed('(자리) ㅔㅡ [c g]', shufle_gen_fixed('에으'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루에으'),
    [pureo('에으')[1::2]],
    misc=("+/ㅔㅡ 1", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박'),
    [pureo('다바')[::2] + pureo('알악')[2::3]],
    misc=("+ㄷㅂ +/ㄹㄱ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박앗압암'),
    [pureo('다바')[::2] + pureo('알악')[2::3], pureo('앗압암')[2::3]],
    max_coupled_range=1,
    misc=("+/ㅅㅂㅁ 2 ①", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박앗압암'),
    [pureo('다바')[::2] + pureo('알악')[2::3], pureo('앗압암')[2::3]],
    max_coupled_range=2,
    misc=("+/ㅅㅂㅁ 2 ②", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으'),
    [pureo('다바')[::2] + pureo('알악')[2::3], pureo('에으')[1::2]],
    max_coupled_range=1,
    misc=("+ㅔㅡ 2 ①", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으'),
    [pureo('다바')[::2] + pureo('알악')[2::3], pureo('에으')[1::2]],
    max_coupled_range=2,
    misc=("+ㅔㅡ 2 ②", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암'),
    [pureo('에으')[1::2], pureo('앗압암')[2::3]],
    max_coupled_range=1,
    misc=("+ㅔㅡ +/ㅅㅂㄹ ①", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암'),
    [pureo('에으')[1::2], pureo('앗압암')[2::3]],
    max_coupled_range=2,
    misc=("+ㅔㅡ +/ㅅㅂㄹ ②", 60)
)

# %% =====================================================================
# 복타입력

# %%
practice_set_from_fixed('(자리) ㅊㅋㅌㅍ [hl hk hi ho]', shufle_gen_fixed('차카타파'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이아안앙머녀소루알악에으앗압암차카타파'),
    [pureo('차카타파')[::2]],
    misc=("+ㅊㅋㅌㅍ", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암차카타파'),
    [pureo('차카타파')[::2], pureo('자가다바하')[::2]],
    misc=("+ㅊㅋㅌㅍ +ㅈㄱㄷㅂ", 60)
)

# %%
practice_set_from_fixed('(자리) ㅐㅢㅟㅚ [df dg dc,db dv]', shufle_gen_fixed('애의위외')) # ㅚ = ㅜ + ㅣ = ㅔ + ㅣ

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('애개핸쟁매내새래댈백애애앳앱앰애의위외'),
    [pureo('애의위외')[1::2]],
    alpha=2.0,
    misc=("+ㅐㅢㅟㅚ", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암애의위외'),
    [pureo('애의위외')[1::2], pureo('이아어여오우에으')[1::2]],
    misc=("+ㅐㅢㅟㅚ +단모음", 60)
)

# %% =========================================================
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀'),
    [pureo('차카타파')[::2], pureo('애의위외')[1::2]],
    max_coupled_range=1,
    misc=("+ㅊㅋㅌㅍ +ㅐㅢㅟㅚ ①", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀'),
    [pureo('차카타파')[::2], pureo('애의위외')[1::2]],
    max_coupled_range=2,
    misc=("+ㅊㅋㅌㅍ +ㅐㅢㅟㅚ ②", 60)
)

# %%
practice_set_from_fixed('(자리) ㄲㄸㅆㅉㅃ [jk ji jn jl jo]', shufle_gen_fixed('까따싸짜빠'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암애의위외까따싸짜빠'),
    [pureo('까따싸짜빠')[::2]],
    misc=("+ㄲㄸㅆㅉㅃ", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀까따싸짜빠'),
    [pureo('까따싸짜빠')[::2], pureo('차카타파')[::2]],
    alpha=2.0,
    misc=("+ㄲㄸㅆㅉㅃ +ㅊㅋㅌㅍ", 60)
)

# %%
practice_set_from_fixed('(자리) ㅘㅛㅠㅑ [.f .b .v .g]', shufle_gen_fixed('와요유야'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한앙머녀소루달악에으앗압암차카타파와요유야'),
    [pureo('와요유야')[1::2]],
    misc=("+ㅘㅛㅠㅑ", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한앙머녀소루달악에으앗압암채킈튀푀와요유야'),
    [pureo('와요유야')[1::2], pureo('애의위외')[1::2]],
    misc=("+ㅘㅛㅠㅑ +ㅐㅢㅟㅚ", 60)
)

# %%
# can use right middle finger for ㅂㅈ
# can use left ㅗ for moeum shift
# can use rf for ㅛ
# practice_set_from_wordset([onyong_words, text_words],
#     pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠'),
#     [pureo('와요유야')[1::2], pureo('바자빠짜')[::2]],
#     max_coupled_range=2,
#     misc=("+ㅘㅛㅠㅑ +ㅂㅈ ②", 60)
# )

practice_set_from_fixed("+ㅘㅛㅠㅑ +ㅂㅈ ② 1", [ jamo.j2h(c,v) for c in pureo('바자빠짜')[::2] for v in pureo('와요유야')[1::2] ])
practice_set_from_rand("+ㅘㅛㅠㅑ +ㅂㅈ ② 2", 90, [ jamo.j2h(c,v,j) for c in pureo('바자빠짜')[::2] for v in pureo('와요유야')[1::2] for j in pureo('안앙알악앗압암')[2::3]+[None]])

# %% ==========================================================
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠'),
    [pureo('까따싸짜빠')[::2], pureo('와요유야')[1::2]],
    alpha=2.0,
    misc=("+ㄲㄸㅆㅉㅃ +ㅘㅛㅠㅑ", 60)
)

# %%
practice_set_from_fixed('(자리) ㅝㅒㅖㅙ [.r .t .c .df]', shufle_gen_fixed('워얘예왜'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한앙머녀소루달악에으앗압암채킈튀푀꽈뚀쓔야아워얘예왜'),
    [pureo('워얘예왜')[1::2]],
    alpha=2.0,
    misc=("+ㅝㅒㅖㅙ", 60)
)

# %%
# practice_set_from_wordset([onyong_words, text_words],
#     pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠워얘예왜'),
#     [pureo('워얘예왜')[1::2], pureo('뱌자빠짜')[::2]],
#     max_coupled_range=2,
#     misc=("+ㅝㅒㅖㅙ ②", 60)
# )

practice_set_from_fixed('+ㅝㅒㅖㅙ 1 ②', [ jamo.j2h(c,v) for c in pureo('뱌자빠짜')[::2] for v in pureo('워얘예왜')[1::2] ])
practice_set_from_rand('+ㅝㅒㅖㅙ 2 ②', 90, [ jamo.j2h(c,v,j) for c in pureo('뱌자빠짜')[::2] for v in pureo('워얘예왜')[1::2] for j in pureo('안앙알악앗압암')[2::3]+[None]])

# %%
practice_set_from_fixed('(자리) /ㅆㅊㅍㅈ [; ;q ;w ;e]', shufle_gen_fixed('았앛앞앚'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠았앛앞앚'),
    [pureo('았앛앞앚')[2::3]],
    misc=("+/ㅆㅊㅍㅈ", 60)
)

# %%
practice_set_from_fixed('(자리) /ㄷㅋㅎㅀ [;z ;x ;d ;a]', shufle_gen_fixed('앋앜앟앓'))

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠앋앜앟앓'),
    [pureo('앋앜앟앓')[2::3]],
    alpha=2.0,
    misc=("+/ㄷㅋㅎㅀ", 60)
)

# %% ==================================================================
practice_set_from_rand('복모음 랜덤글자', 120, [
    jamo.j2h(c,v,j)
    for c in pureo('아가하자마나사라다바차카타파까따싸짜빠')[::2]
    for v in pureo('와요유야워얘예왜')[1::2]
    for j in pureo('았앛앞앚앋앜앟앓')[2::3]
])

# %%
# '앆앍' ㅇㄱ ㅁㄱ
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠웠얯옢왲앋앜앟앓앆앍'),
    [pureo('앆앍')[2::3]],
    misc=('/ㄲㄺ [ax zx]', 30)
)

# %%
# '앏앐앖' ㄹㅂ ㄹㅅ ㅂㅅ
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠웠얯옢왲앋앜앟앓앏앐앖'),
    [pureo('앏앐앖')[2::3]],
    misc=('/ㄼㄽㅄ [ew eq wq]', 30)
)

# %%
# '앉않앝' ㄴㄹ ㄴㅇ ㄴㅁ/ㄹㅂㅆ
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠웠얯옢왲앋앜앟앓앉않앝'),
    [pureo('앉않앝')[2::3]],
    misc=('/ㄵㄶㅌ [se sa zs,ew;]', 30)
)

# %%
# '앑앒' ㅇㅁ ㅇㅂ
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠웠얯옢왲앋앜앟앓앑앒'),
    [pureo('앑앒')[2::3]],
    misc=('/ㄾㄿ [ax aw]', 30)
)

# %%
# '앇앎' ㄱㅁㅆ ㅂㅅㅆ/ㄹㅁ
practice_set_from_wordset([onyong_words, text_words],
    pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠웠얯옢왲앋앜앟앓앇앎'),
    [pureo('앇앎')[2::3]],
    misc=('/ㄳㄻ [xz; wq;]', 30)
)

# %%
# jamos = pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쓔쨔빠웠얯옢왲앋앜앟앓')
# for (c, count) in gp_both:
#     if c not in jamos and not re.match(r'[0-9A-Za-z]', c):
#         print(repr(c), f"({ord(c)})", count)

with open("../assets/data/practices_semoe2018.json", "wt") as f:
    json.dump(practice.practices, f, ensure_ascii=False)

# %%
practice = Practice('공세벌식 390')

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아기'),
    [pureo('아기')],
    misc=('ㅇㄱ + ㅏㅣ', 30),
)

#%%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아기자바'),
    [pureo('자바')[::2]],
    misc=('+ㅈㅂ', 30),
)

#%%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아기자바인잉'),
    [pureo('인잉')[2::3]],
    misc=('+/ㄴㅇ', 30),
)

#%%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아기자바인잉'),
    [pureo('아기자바인잉')],
    misc=('기본자리', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가자바인잉느트'),
    [pureo('느트')],
    misc=('가운뎃줄', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가자바인잉느트오우'),
    [pureo('오우')[1::2]],
    misc=('ㅗㅜ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트오우'),
    [pureo('까짜빠')[::2]],
    misc=('ㄲㅉㅃ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉리디띠'),
    [pureo('리디띠')[::2]],
    misc=('ㄹㄷ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠'),
    [pureo('리디띠')[::2], pureo('느트')],
    misc=('ㄹㄷ+ㄴㅌㅡ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트오우리디띠'),
    [pureo('리디띠')[::2], pureo('오우')[1::2]],
    misc=('ㄹㄷ+ㅗㅜ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉미치파'),
    [pureo('미치파')[::2]],
    misc=('ㅁㅊㅍ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치파'),
    [pureo('미치파')[::2], pureo('느트리디띠')[::2]],
    misc=('ㅁㅊㅍ+ㄴㅌㄹㄷ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느타오우리디띠미치파'),
    [pureo('미치파')[::2], pureo('오우')[1::2]],
    misc=('ㅁㅊㅍ+ㅗㅜ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉여애어에'),
    [pureo('여애어에')[1::2]],
    misc=('ㅕㅐㅓㅔ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트여애어에'),
    [pureo('여애어에')[1::2], pureo('느트')],
    misc=('ㅕㅐㅓㅔ+ㄴㅌㅡ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠여애어에'),
    [pureo('여애어에')[1::2], pureo('리디띠')[::2]],
    misc=('ㅕㅐㅓㅔ+ㄹㄷ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피여애어에'),
    [pureo('여애어에')[1::2], pureo('미치피')[::2]],
    misc=('ㅕㅐㅓㅔ+ㅁㅊㅍ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트오우여애어에'),
    [pureo('여애어에')[1::2], pureo('오우')[1::2]],
    misc=('ㅕㅐㅓㅔ+ㅗㅜ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에'),
    [pureo('여애어에')[1::2], pureo('오우')[1::2]],
    misc=('ㅕㅐㅓㅔ+ㅗㅜ+ㄹㄷㅁㅊㅍ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉사싸하'),
    [pureo('사싸하')[::2]],
    misc=('ㅅㅎ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피사싸하'),
    [pureo('사싸하')[::2], pureo('느트리디띠미치피')[::2]],
    misc=('ㅅㅎ+ㄴㅌ+ㄹㄷㅁㅊㅍ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하'),
    [pureo('사싸하')[::2], pureo('오우여애어에')[1::2]],
    misc=('ㅅㅎ+ㅗㅜ+ㅕㅐㅓㅔ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트암악'),
    [pureo('암악')[2::3]],
    misc=('/ㅁㄱ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피사싸하암악'),
    [pureo('암악')[2::3], pureo('리디띠미치피사싸하')[::2]],
    misc=('/ㅁㄱ+ㄹㄷㅁㅊㅍㅅㅎ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악'),
    [pureo('암악')[2::3], pureo('오우여애어에')[1::2]],
    misc=('/ㅁㄱ+ㅗㅜㅕㅐㅓㅔ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트앗알'),
    [pureo('앗알')[2::3]],
    misc=('/ㅅㄹ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피사싸하앗알'),
    [pureo('앗알')[2::3], pureo('리디띠미치피사싸하')[::2]],
    misc=('/ㅅㄹ+ㄹㄷㅁㅊㅍㅅㅎ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앗알'),
    [pureo('앗알')[2::3], pureo('오우여애어에')[1::2]],
    misc=('/ㅅㄹ+ㅗㅜㅕㅐㅓㅔ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앋앛'),
    [pureo('앋앛')[2::3]],
    misc=('/ㄷㅊ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앞앝앜'),
    [pureo('앞앝앜')[2::3]],
    misc=('/ㅍㅌㅋ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앋앛앞앝앜'),
    [pureo('앋앛앞앝앜')[2::3]],
    misc=('/ㄷㅊㅍㅌㅋ', 60),
)

# %%
# practice_set_from_wordset([onyong_words, text_words],
#     pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜'),
#     [ pureo('암악앗알앋앛')[2::3], pureo('앞앝앜')[2::3], ],
#     misc=('/ㅁㄱㅅㄹㄷㅊ+/ㅍㅌㅋ', 10),
# )

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜'),
    [ pureo('암악앗알앋앛앞앝앜')[2::3], ],
    misc=('/ㅁㄱ+/ㅅㄹ+/ㄷㅊ+/ㅍㅌㅋ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앟았압'),
    [pureo('앟았압')[2::3]],
    misc=('/ㅎㅆㅂ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앟았압'),
    [pureo('앟았압')[2::3], pureo('암악앗알')[2::3]],
    misc=('/ㅎㅆㅂ+/ㅁㄱㅅㄹ', 60),
)

# %%
# practice_set_from_wordset([onyong_words, text_words],
#     pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압'),
#     [pureo('앟았압')[2::3], pureo('앞앝앜')[2::3]],
#     misc=('/ㅎㅆㅂ+/앞앝앜', 60),
# )

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피사싸하요유야'),
    [pureo('요유야')[1::2]],
    misc=('ㅛㅠㅑ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하요유야'),
    [ pureo('요유야')[1::2], pureo('오우여애어에')[1::2], ],
    misc=('ㅛㅠㅑ+ㅗㅜㅕㅐㅓㅔ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알요유야'),
    [pureo('요유야')[1::2], pureo('암악앗알')[2::3]],
    misc=('ㅛㅠㅑ+/ㅁㄱㅅㄹ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야'),
    [pureo('요유야')[1::2], pureo('앋앛앟았압')[2::3]],
    misc=('ㅛㅠㅑ+/ㄷㅊㅍㅌㅋㅎㅆㅂ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('컞')[:1],
    [pureo('컞')[0]],
    misc=('ㅋ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('컞')[:2],
    [pureo('컞')[1]],
    misc=('ㅒ', 10),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('콎')[:2],
    [pureo('콎')[1]],
    misc=('ㅖ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('콎')[:3],
    [pureo('콎')[2]],
    misc=('/ㅈ', 60),
)

# %%
# practice_set_from_wordset([onyong_words, text_words],
#     pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎'),
#     [ ['ᄏ', 'ᅤ', 'ᅨ',], ['ᄏ', 'ᅤ', 'ᆽ',], ['ᄏ', 'ᅨ', 'ᆽ',], ['ᅤ', 'ᅨ', 'ᆽ',], ],
#     misc=('/ㅈ', 60),
# )

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위'),
    [pureo('와외위')[1::2]],
    misc=('ㅘㅚㅟ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎왜워웨'),
    [pureo('왜워웨')[1::2]],
    misc=('ㅙㅝㅞ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨'),
    [pureo('와외위')[1::2], pureo('왜워웨')[1::2]],
    misc=('ㅘㅚㅟ+ㅙㅝㅞ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨'),
    [pureo('와외위왜워웨')[1::2]],
    misc=('ㅘㅚㅟㅙㅝㅞ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의'),
    [pureo('의')[1::2]],
    misc=('ㅢ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의'),
    [pureo('의')[1::2], pureo('와외위왜워웨')[1::2]],
    misc=('ㅢ+ㅘㅚㅟㅙㅝㅞ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의'),
    [pureo('의')[1::2], pureo('와외위왜워웨')[1::2]],
    misc=('ㅢ+ㅘㅚㅟㅙㅝㅞ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆'),
    [pureo('않앍앆')[2::3]],
    misc=('ㄶㄺㄲ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의앖앎앓'),
    [pureo('앖앎앓')[2::3]],
    misc=('ㅄㄻㅀ', 60),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆앖앎앓읷앉앏'),
    [pureo('앇앉앏')[2::3]],
    misc=('ㄳㄵㄼ', 20),
)

# %%
practice_set_from_wordset([onyong_words, text_words],
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆앖앎앓읷앉앏'),
    [ pureo('암악앗알았압')[2::3], pureo('앋앛앟앞앝앜앚')[2::3], ],
    misc=('/ㄷㅊㅎㅍㅌㅋㅈ++', 60),
)

# %%
pi = """
3.1415926535 8979323846 2643383279 5028841971 6939937510
  5820974944 5923078164 0628620899 8628034825 3421170679
  8214808651 3282306647 0938446095 5058223172 5359408128
  4811174502 8410270193 8521105559 6446229489 5493038196
  4428810975 6659334461 2847564823 3786783165 2712019091
  4564856692 3460348610 4543266482 1339360726 0249141273
  7245870066 0631558817 4881520920 9628292540 9171536436
  7892590360 0113305305 4882046652 1384146951 9415116094
  3305727036 5759591953 0921861173 8193261179 3105118548
  0744623799 6274956735 1885752724 8912279381 8301194912
"""

pi = pi.replace(' ', '').replace('\n', '')[2:]

from itertools import batched
import random

puncs = ''';<>/':"!,.'''

pi_words = [
    ''.join(chunk[:3] + (random.choice(puncs),) + chunk[3:] + (random.choice(puncs),))
    for chunk in batched(pi, 6)
]

practice_set_from_fixed('π500', pi_words)

# %%
with open("../assets/data/practices_kong390.json", "wt") as f:
    json.dump(practice.practices, f, ensure_ascii=False)
