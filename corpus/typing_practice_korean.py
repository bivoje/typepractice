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
with open('공산당 선언.txt', 'r') as f: 
    comm_text = f.read()
comm_text 

# %%
with open('산업사회와 그 미래.txt', 'r') as f:
    unab_text = f.read()
unab_text

# %%
with open('세계인권선언.txt') as f:
    udhr_text = f.read()
    # 제 78 조 같은 거는 숫자 제외, 한 글자 단어 제외로 잘려나갈거임
udhr_text

# %%
with open('사회계약론.txt') as f:
    sct_text = f.read()
sct_text

# %%
text = comm_text + '\n' + unab_text + '\n' + udhr_text + '\n' + sct_text
sorted(set(text))

# %%
import re
hangule_text = re.sub(r'[^\uAC00-\uD7A3]', ' ', text)
sorted(set(hangule_text))

# %%
def remove_josa(word):
    josas = ['은','는','이','가','을','를','의','으로','도','들이','들을','들의']
    for josa in josas:
        if word.endswith(josa):
            return word.removesuffix(josa)
    return word

danwoe = set(remove_josa(word) for word in hangule_text.split() if len(remove_josa(word)) > 1)
len(danwoe)

# %%
import random
random.seed(42)
practice_sets = []

def filter_danwoe(allowed, required, word):
    jamos = pureo(word)
    if not all(gulsoe in allowed for gulsoe in jamos):
        return False
    for req in required:
        if not any(gulsoe in jamos for gulsoe in req):
            return False
    return True

def gen_filtered_danwoe(allowed, required):
    for word in danwoe:
        if filter_danwoe(allowed, required, word):
            yield word

def add_practice_sliced(collected, misc):
    cut = len(collected) // misc['choice'] 
    take = misc.get('take', 3)
    print(f"{take} / {cut}")
    if cut > 1:
        k, m = divmod(len(collected), cut)
        for i in range(min(cut, take)):
            collectpart = collected[i*k+min(i,m):(i+1)*k+min(i+1,m)]
            practice_sets.append((f"{misc['title']}{i+1}", collectpart, misc['shuffle'], misc['choice']))
    else:
        practice_sets.append((misc['title'], collected, misc['shuffle'], misc['choice']))

def add_practice(allowed, required, misc=None):
    collected = []
    for word in gen_filtered_danwoe(allowed, required):
        collected.append(word)
    print(len(collected))

    random.shuffle(collected)

    if misc: add_practice_sliced(collected, misc)

    # return collected

# %%
add_practice(
    pureo('아가자바인잉'),
    [],
    { "title": '기본자리', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가자바인잉느트'),
    [pureo('느트')],
    { "title": '가운뎃줄', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가자바인잉느트오우'),
    [pureo('오우')[1::2]],
    { "title": 'ㅗㅜ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트오우'),
    [pureo('까짜빠')[::2]],
    { "title": 'ㄲㅉㅃ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉리디띠'),
    [pureo('리디띠')[::2]],
    { "title": 'ㄹㄷ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠'),
    [pureo('리디띠')[::2], pureo('느트')],
    { "title": 'ㄹㄷ+ㄴㅌㅡ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트오우리디띠'),
    [pureo('리디띠')[::2], pureo('오우')[1::2]],
    { "title": 'ㄹㄷ+ㅗㅜ', "shuffle": True, "choice": 60, "take": 4 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉미치파'),
    [pureo('미치파')[::2]],
    { "title": 'ㅁㅊㅍ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치파'),
    [pureo('미치파')[::2], pureo('느트리디띠')[::2]],
    { "title": 'ㅁㅊㅍ+ㄴㅌㄹㄷ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느타오우리디띠미치파'),
    [pureo('미치파')[::2], pureo('오우')[1::2]],
    { "title": 'ㅁㅊㅍ+ㅗㅜ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉여애어에'),
    [pureo('여애어에')[1::2]],
    { "title": 'ㅕㅐㅓㅔ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트여애어에'),
    [pureo('여애어에')[1::2], pureo('느트')],
    { "title": 'ㅕㅐㅓㅔ+ㄴㅌㅡ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠여애어에'),
    [pureo('여애어에')[1::2], pureo('리디띠')[::2]],
    { "title": 'ㅕㅐㅓㅔ+ㄹㄷ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피여애어에'),
    [pureo('여애어에')[1::2], pureo('미치피')[::2]],
    { "title": 'ㅕㅐㅓㅔ+ㅁㅊㅍ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트오우여애어에'),
    [pureo('여애어에')[1::2], pureo('오우')[1::2]],
    { "title": 'ㅕㅐㅓㅔ+ㅗㅜ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에'),
    [pureo('여애어에')[1::2], pureo('오우')[1::2]],
    { "title": 'ㅕㅐㅓㅔ+ㅗㅜ+ㄹㄷㅁㅊㅍ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉사싸하'),
    [pureo('사싸하')[::2]],
    { "title": 'ㅅㅎ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피사싸하'),
    [pureo('사싸하')[::2], pureo('느트리디띠미치피')[::2]],
    { "title": 'ㅅㅎ+ㄴㅌ+ㄹㄷㅁㅊㅍ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하'),
    [pureo('사싸하')[::2], pureo('오우여애어에')[1::2]],
    { "title": 'ㅅㅎ+ㅗㅜ+ㅕㅐㅓㅔ', "shuffle": True, "choice": 60, "cut": 20, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트암악'),
    [pureo('암악')[2::3]],
    { "title": '/ㅁㄱ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피사싸하암악'),
    [pureo('암악')[2::3], pureo('리디띠미치피사싸하')[::2]],
    { "title": '/ㅁㄱ+ㄹㄷㅁㅊㅍㅅㅎ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악'),
    [pureo('암악')[2::3], pureo('오우여애어에')[1::2]],
    { "title": '/ㅁㄱ+ㅗㅜㅕㅐㅓㅔ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트앗알'),
    [pureo('앗알')[2::3]],
    { "title": '/ㅅㄹ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피사싸하앗알'),
    [pureo('앗알')[2::3], pureo('리디띠미치피사싸하')[::2]],
    { "title": '/ㅅㄹ+ㄹㄷㅁㅊㅍㅅㅎ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앗알'),
    [pureo('앗알')[2::3], pureo('오우여애어에')[1::2]],
    { "title": '/ㅅㄹ+ㅗㅜㅕㅐㅓㅔ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앋앛'),
    [pureo('앋앛')[2::3]],
    { "title": '/ㄷㅊ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앞앝앜'),
    [pureo('앞앝앜')[2::3]],
    { "title": '/ㅍㅌㅋ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앋앛앞앝앜'),
    [pureo('앋앛앞앝앜')[2::3]],
    { "title": '/ㄷㅊㅍㅌㅋ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
# add_practice(
#     pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜'),
#     [
#         pureo('암악앗알앋앛')[2::3],
#         pureo('앞앝앜')[2::3],
#     ],
#     { "title": '/ㅁㄱㅅㄹㄷㅊ+/ㅍㅌㅋ', "shuffle": True, "choice": 10, "take": 4 }
# )

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜'),
    [
        pureo('암악앗알앋앛')[2::3],
        pureo('암악앗알앞앝앜')[2::3],
        pureo('암악앋앛앞앝앜')[2::3],
        pureo('앗알앋앛앞앝앜')[2::3],
    ],
    { "title": '/ㅁㄱ+/ㅅㄹ+/ㄷㅊ+/ㅍㅌㅋ', "shuffle": True, "choice": 60, "take": 4 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앟았압'),
    [pureo('앟았압')[2::3]],
    { "title": '/ㅎㅆㅂ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앟았압'),
    [pureo('앟았압')[2::3], pureo('암악앗알')[2::3]],
    { "title": '/ㅎㅆㅂ+/ㅁㄱㅅㄹ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
# add_practice(
#     pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압'),
#     [pureo('앟았압')[2::3], pureo('앞앝앜')[2::3]],
#     # { "title": '/ㅎㅆㅂ+/앞앝앜', "shuffle": True, "choice": 60, "take": 3 }
# )

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피사싸하요유야'),
    [pureo('요유야')[1::2]],
    { "title": 'ㅛㅠㅑ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하요유야'),
    [
        pureo('요유야')[1::2],
        pureo('오우여애어에')[1::2],
        # pureo('오우여애어에')[1::2],
    ],
    { "title": 'ㅛㅠㅑ+ㅗㅜㅕㅐㅓㅔ', "shuffle": True, "choice": 60, "take": 4 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알요유야'),
    [pureo('요유야')[1::2], pureo('암악앗알')[2::3]],
    { "title": 'ㅛㅠㅑ+/ㅁㄱㅅㄹ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야'),
    [pureo('요유야')[1::2], pureo('앋앛앟았압')[2::3]],
    { "title": 'ㅛㅠㅑ+/ㄷㅊㅍㅌㅋㅎㅆㅂ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('컞')[:1],
    [pureo('컞')[0]],
    { "title": 'ㅋ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('컞')[:2],
    [pureo('컞')[1]],
    { "title": 'ㅒ', "shuffle": True, "choice": 10, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('콎')[:2],
    [pureo('콎')[1]],
    { "title": 'ㅖ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('콎')[:3],
    [pureo('콎')[2]],
    { "title": '/ㅈ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
# add_practice(
#     pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎'),
#     [
#         ['ᄏ', 'ᅤ', 'ᅨ',],
#         ['ᄏ', 'ᅤ', 'ᆽ',],
#         ['ᄏ', 'ᅨ', 'ᆽ',],
#         ['ᅤ', 'ᅨ', 'ᆽ',],
#     ],
#     # { "title": '/ㅈ', "shuffle": True, "choice": 60, "take": 1 }
# )

# %%
jamo_used = set(j for t in practice_sets for word in t[1] for j in pureo(word))
print(len(jamo_used))
jamo_used

# %%
jamo_avail = set(j for j in pureo(hangule_text))
jamo_avail.remove(' ')
print(len(jamo_avail))
jamo_avail

# %%
jamo_avail - jamo_used

# %%
jamo_all = set(chr(x) for x in range(0x1100, 0x11FF))
jamo_all - jamo_avail

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위'),
    [pureo('와외위')[1::2]],
    { "title": 'ㅘㅚㅟ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎왜워웨'),
    [pureo('왜워웨')[1::2]],
    { "title": 'ㅙㅝㅞ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨'),
    [pureo('와외위')[1::2], pureo('왜워웨')[1::2]],
    { "title": 'ㅘㅚㅟ+ㅙㅝㅞ', "shuffle": True, "choice": 60, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨'),
    [pureo('와외위왜워웨')[1::2]],
    { "title": 'ㅘㅚㅟㅙㅝㅞ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의'),
    [pureo('의')[1::2]],
    { "title": 'ㅢ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의'),
    [pureo('의')[1::2], pureo('와외위왜워웨')[1::2]],
    { "title": 'ㅢ+ㅘㅚㅟㅙㅝㅞ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의'),
    [pureo('의')[1::2], pureo('와외위왜워웨')[1::2]],
    { "title": 'ㅢ+ㅘㅚㅟㅙㅝㅞ', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆'),
    [pureo('않앍앆')[2::3]],
    { "title": 'ㄶㄺㄲ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의앖앎앓'),
    [pureo('앖앎앓')[2::3]],
    { "title": 'ㅄㄻㅀ', "shuffle": True, "choice": 60, "take": 3 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆앖앎앓읷앉앏'),
    [pureo('앇앉앏')[2::3]],
    { "title": 'ㄳㄵㄼ', "shuffle": True, "choice": 20, "take": 1 }
)

# %%
add_practice(
    pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆앖앎앓읷앉앏'),
    [
        pureo('암악앗알았압')[2::3],
        pureo('앋앛앟앞앝앜앚')[2::3],
    ],
    { "title": '/ㄷㅊㅎㅍㅌㅋㅈ++', "shuffle": True, "choice": 60, "take": 2 }
)

# %%
jamo_used = set(j for t in practice_sets for word in t[1] for j in pureo(word))
print(len(jamo_used))
jamo_avail - jamo_used

# %%
danwoe_used = set(word for t in practice_sets for word in t[1])
print(len(danwoe_used))
danwoe - danwoe_used

# %%
gulza_used = set(g for t in practice_sets for word in t[1] for g in word)
gulza = set(g for word in danwoe for g in word)
print(len(gulza), len(gulza_used))
gulza_unused = gulza - gulza_used
gulza_unused

# %%
collected = []
for word in danwoe:
    if any(g in word for g in gulza_unused):
        collected.append(word)
print(len(collected))
collected

# %%
add_practice_sliced(
    collected,
    { "title": '연습', "shuffle": True, "choice": 60, "take": 100 }
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

add_practice_sliced(
    pi_words,
    { "title": 'π500', "shuffle": False, "choice": 1000, }
)

# %%
import sqlite3
import os

dbpath = "../assets/app.db"

if os.path.exists(dbpath):
    os.remove(dbpath)

conn = sqlite3.connect(dbpath)
cursor = conn.cursor()

# %%
cursor.execute("""
CREATE TABLE IF NOT EXISTS practice (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    num_words INTEGER NOT NULL,
    shuffle INTEGER NOT NULL CHECK (shuffle IN (0,1))
)
""")

conn.commit()

# %%
cursor.execute("""
CREATE TABLE IF NOT EXISTS practice_history (
    id INTEGER PRIMARY KEY,

    practice_id INTEGER NOT NULL,

    wrong_cnt   INTEGER NOT NULL,
    word_cnt    INTEGER NOT NULL,
    seconds     INTEGER NOT NULL,
    typing_cnt  INTEGER NOT NULL,
    points      INTEGER NOT NULL,

    allow_del INTEGER NOT NULL CHECK (allow_del IN (0,1)),
    created_at INTEGER NOT NULL,

    FOREIGN KEY (practice_id)
        REFERENCES practice(id)
)
""")

conn.commit()

# %%
# cursor.execute("DELETE FROM practice")
# cursor.execute("DELETE FROM practice_history")
cursor.executemany(
    "INSERT INTO practice (title, content, shuffle, num_words) VALUES (?, ?, ?, ?)",
    [ (title, ' '.join(content), shuffle, choice) for title, content, shuffle, choice in practice_sets ]
)

conn.commit()

# %%
conn.close()

# %%
import sqlite3

dbpath = "../assets/app.db"
conn = sqlite3.connect(dbpath)
cursor = conn.cursor()
# %%
import json
data = cursor.execute("SELECT id, title, content, num_words FROM practice ORDER BY id ASC").fetchall()
with open("../assets/appdb.json", "wt") as f:
    json.dump(data, f)