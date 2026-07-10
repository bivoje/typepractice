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

    # supplimentary words found using https://wordrow.kr/%ED%8F%AC%ED%95%A8%ED%95%98%EB%8A%94-%EB%A7%90/%ED%9B%95/
    words.update("넋두리 뱃삯 핥다 훑다 홅다 훑어보기 개미핥기 읊다 읊어 읊조리다 곬 물곬 외곬 통곬 옰".split())
    words.update('굽신 굽이돌아 눕히다 어둡다 그룹 우스웁다 웁살라 수줍어하다 어줍게 머줍다 '.split())
    words.update('오뎅 뎅강 벵갈호랑이 스미마셍 엥기다 헹가레'.split())
    words.update('엘도라도 헵번 조니뎁 렙틸리언 셀렙 엡실론 렛잇비 멧비둘기 셋업 에셋 헤드셋'.split())
    words.update("가냘프다 말괼량이 먈쑥히 얄긋거리다 귀얄질 얄팍한 얄타회담 얄밉다 시보귬 아셀레늄산 악티늄족 디아조늄염 플래티늄 다이크로뮴산 암모늄 라듐실크 팔라듐 클리니듐 플라스모듐속 스칸듐 디필리듐속 나트륨 과칼륨 과레늄산칼륨 니켈카드뮴 크로뮴황 멘델레븀 덴드로븀 칼슘 대슘치마 뿌윰히 보윰하다 테크네튬 코스튬 알루미늄리튬 퍼퓸매니큐어 유로퓸 흄로터리규칙 흄관 셋괏다 결괏값 괏쇠 기왓장 왓슨 왓닥갓닥 스왓 멘왓 유왓대 와이드스쾃 패러쾃 봉홧불 장홧발 중홧값 조홧속 홧김비용 포홧값 매홧간 얌냠거리다 부냠웨라열 할냠 뱜딸구 뱜댕이 도마뱜 할아뱜 샴쌍둥이 샴푸 샴페인 샴버그병 얌체 아얌고랭 얌셍이 기얌나무 얌전히 똠얌쿰 얌운센 덩크슛 로빙슛 여윳돈 우윳빛 석윳각지 고윳값 아웨윱다 가윱다 욥기 욥전 묫자리 성묫길 묫등 숏포지션 숏건법 욧거죽 욧속 도욧과 욧카이치천식 춋블 푯대 푯말 좌푯값 푯돌 대푯값 굠나무 대뇸 고욤나무 굴레시욤 귀욤 하외욤 카르마뇰재킷 에스파뇰 비뇰라 오룔 묠니르 숄더백 숄카라 욜래방정 욜레스검사 욜삭다 로욜라 횰로 맨숀 숀가우어 데니숀무용단 욘족 비욘드 욘존 프레트욘가 죤득죤득 괌티다 괌밥 곽밥 풋봠 왐마 왐스 브왐바열 쥐왐쥐왐 얼걋 키로프뱟카 원샷법 벙커샷 슬링샷 뙤얏하다 오얏밭에 지얏개미 오얏추 이얏동모 쟛고야 뱝뛰다 포토샵 워크샵 펫샵 얍실허다 가븨얍다 얍슬얍슬 챱챱 샤기냔 서냔장사 하탸투랸 말랸게기 침랸스크호 뱐뱐하다 뱐둥뱐둥 세묘노프탼샨스키 아샨티제국 두샨베 알류샨해구 얀선주의 얀스키 비엘쇼브스키병 카얀족 쟌누치세포 쟌경색 크리스챤병 캰날".split())
    words.update("튜토리얼 스튜어트 튜너 도쿄 쿄야마 똬머리 꽈릿빛 꽈리 꽈르릉 허파꽈리 빈툐 셰툐 젼툐 사탸그라하 보탸크어 류탸오후사건 오스탸크족 콰당탕 에콰도르 콰직 콰트로 캬프슈 캬사누르 레이캬비크 캬라멜 쿠드랴프카 뜌뚀땨 때뀨 꺄룩꺄룩 꺄트리엠므 뽀지씨용 꺄르 꺄락떼르 꾸뻬 뜨루아 뀨잉".split())
    words.update("쥬니어 해쥬 그랑쥬떼 쥬크스 앙쥬아리다 알롱쥬 디죠지증후군 반죠 아이죠드충격시험기 쟈코비안 쟈오락 꼬떼쟈르댕 샤쿠뵤시 뵤도인 뵤른슈타드 뱌암 뱌우리 뱌슬대다 린뱌오 돌뱌크".split())
    words.update("촤라락 퍄티고르스키 액츄에이터 시츄에이션 위츄라 크리스챠니아 플란챠 켄챠야자 미니쮸 쬬꼼 뾰족코 뾰족뒤쥐 뾰로통 뾰루지 뺘드득 뺘무리".split())
    words.update("캴캴대다 큠큠한 마좟다 좟녁 좟장 쟘보 쟘불말 쟘뱅이".split())
    words.update("늴리리 흴뇌리 엠버".split())
    words.update("감자퓌레 드레퓌스 복어튀김 걸픠여기 설픠다 밀푀우 푀트르 푀부스 밀푀유나베 틔움 틔우미 드틔우다 킈다 쾨니히스베르크 쾨페결절 쾨미이창법 즈츼이다 저리짐츼".split())
    words.update("픵픵이 얼픳 푄현상 챌린지 챔버 챈들러 오픈챗 쵝오 퀵배달 탬퍼 튁튁 튕기다 팹리스 ".split())
    words.update("애걔 걔툉이 도독고냬이 쑷고냬이 콧구냬 섀도우박스 섀넌강 섀복밥 섀플리 섀기카펫 얘물얘물 보얘지다 깍쟤 햬기 주금꺠 뺴끼다 썌비".split())
    words.update("임곗값 곗날 비곗덩이 곗돈 오롓다 대롓술 순롓길 차롓걸음 몟자리 솃바눌 옛사람 옛날짜장 궝게 실궝가래 뭥미 뭥개 쉉편 콩웡 쵸우웡 웡원하오 우웡지 웡셍이 암퀑 퀑퀑 수퀑 훵덩하다 훵하다 달꿩 꿩고사릿과 꿩의장옷 꿩마능 꿩채 꿩토렴 들뤗 뭣하다 무웟 훳뒷볼 훳돈 훳뒷측 불웝 셜웝하다 실궘 둼간 머그웜프 갈웜 콘볼류트웜 웜부팅 시디웜 인볼류트웜 스웜프맨 궉진 붝고무래 붝정지 붝앙지 웍더글웍더글하다 풋웍 어웍새 눈꿕 꿕꿕 괭이자루 숨괭이 탯괭이 좀괭이수염 괭이갈매기 뇅이 삭됑이 둥투럭쇙애지 난쇙이 왱가당왱가당 왱강왱강 쇠왱간 좽이그물 좽이질 쵕경 수쾡이 쾡가리 암쾡이 살쾡이좌 퇭마루 꽃봉퇭이 횅하다 횅댕그렁 횅창 옥수꽹이 꽹과리 꽹나무 괫대 됏마루 엿쇗날 쇗대 왯굴 왯도리 좻돌 쾟돈 등쾟줄 횃불 횃대 횃놀이 횃소리 다쐣날 여쐣날 왭스터 됍니까 봽새 웃쇔 좸좸 움쾜 쐠지 괠다 괠띠 왤케 왤지 괜시리 괜스레 괜찮다 됀장 왠수 왠통 꽨새기 꽨사 뙌장 괜게채잏다 괙괙 쇅쇅대다 쇅경 왝땍왝땍 왝왝거리다 구왝구왝 좩병 홱홱 홱보기 꽥꽥이 홱꽥 쐑히다 쐑소리 멩롕 몡이 솅겐조약 솅커시스템 콧구옝 옝기청 옝일학 두아옝 폥구 볭자임 뼹아리 뎽쳥 눈물곕다 곕시다 솁킨 체르니솁스키 프로코피옙스크 도스토옙스키 옙하다 졥다 양녬장 옘병 옘집 옘돌이 자이옘 아옘용액 본톔 혬수 몔치 클램셸버킷 라로셸공성전 셸락바니시 라셸레이스 몽생미셸섬 로셸염 옐로페이지 보옐디외 에옐링 옐리네크 녠치 올뎬 저우커우뎬유적 화뎬 욜뎬 샬뎬 치롄산맥 다롄 롄윈강 화롄 옌볜 시루볜 그로셴 데크레셴도 에셴바흐 부르셴샤프트 셴괴 왕셴첸 조셴코 옌타이갱 아옌데 옌센부등식 옌샤두유적 옌센디바이스 옌워 쥐옌한간 샬뗸 올뗸 쏀뚱이 쏀베락 쏀지 톈진조약 펑톈파 다이톈추 란톈산 정녝 구녝 셱게 곡셱 셱우 넁중 성넁이통 섕킹 스레드섕크 섕크의추측 드릴섕크 에비고얭 꼬쟹 오얫 떗꾸 꺳닢 썟삥 걧단 레프트쟵 뱹새 퍱시 첍터 얍썝이 섐브레이 피터섐리본 피터섐코삭스 섐블즈 비얨 뉴햼프셔 먬먬 걤블러 컘프 얠미릅다 섈리의법칙 첄린지 뱰런스 썔쭉 퍨월드 얜시 봉얜 쟨테보기 첀들러 댼디 쟨말놀이 디즈니럔드 썍쌔기판 전술햭 부산댹 빅먝 아이스퍡 컉터스 얙막이".split())
    words.update("까자쵸크 쵸바굼이 쵸우웡 쵸콜릿 쫘르륵 쫘락쫘락 차이쨔 쓔시다 쑈리 쑈이 엎드려쏴 쏴락쏴락 쏴라 앉아쏴 쌰구재 귀쌰머리 쀼쭉 쀼루퉁".split())
    words.update("궁둥줘배기  줘뜯다  줘짜다 나구쟤 얘쟤 따꼽쟤 산졔  졔티  졔날 고졔니  좨기  좨치다 나좨  좨주  붜이  붜리  볘울눈이  볘룻독 다볘산맥  쫴우다  쫴기  쫴꼼  뺴끼다 감춰진 들춰갈이 들춰나다 엇맞춰이음  폐가식  폐동맥 은폐용  폐루프계 지형차폐  폐증기 쇄폐  폐기물재활용  폐품  폐쇄연접 황폐화  폐원자로 뱨홍동 봬요 자오쭤시 쭤궁현 쨰릿쨰릿 즈드랏스부이쪠 이뿨이뿨 뼤쩨르부르크 뽸어남 챼플 쳬셔 쵀탁동시 풔리웡 퍠피 퐤포".split())
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

def alt_gen_fixed(alts):
    return "a1a2 b1b2 c1c2 d1d2 a1a2a1a2 b1b2b1b2 c1c2c1c2 d1d2d1d2 a1b1a2b2 c1d1c2d2 b1b2d1d2 d1d2a1a2" \
    .replace('a1', alts[0][0]) \
    .replace('a2', alts[0][1]) \
    .replace('b1', alts[1][0]) \
    .replace('b2', alts[1][1]) \
    .replace('c1', alts[2][0]) \
    .replace('c2', alts[2][1]) \
    .replace('d1', alts[3][0]) \
    .replace('d2', alts[3][1]) \
    .split()

# %%
import re

def cands_repat(cands_seqs):
    return '|'.join(''.join('[' + ''.join(cands) + ']' for cands in cands_seq) for cands_seq in cands_seqs)

def cands_labels(cands_seqs):
    def cands_labels_rec(i, cands_seq):
        if i >= len(cands_seq):
            yield ''
        else:
            for head in cands_seq[i]:
                for rest in cands_labels_rec(i+1, cands_seq):
                    yield head + rest

    for cand_seq in cands_seqs:
        yield from cands_labels_rec(0, cand_seq)

def check_danwoe_(criterion, jamos):
    match criterion[0]:
        case 'Covered':
            allowed = criterion[1]
            return all(jamo in allowed for jamo in jamos)

        case 'IncludeCombs':
            cands_seqs = criterion[1]
            pat = cands_repat(cands_seqs)
            return re.findall(pat, jamos)

        case 'ExcludeComb':
            cands_seq = criterion[1]
            pat = cands_repat([cands_seq])
            return not re.search(pat, jamos)

        case _:
            raise Exception(f"Unrecognized criterion type: {criterion[0]}")

def check_danwoe(criteria, word):
    jamos = jamo.h2j(word)
    found = set()
    for criterion in criteria:
        ret = check_danwoe_(criterion, jamos)
        if not ret: return None
        if not isinstance(ret, bool):
            found.update(ret)
    return found

def filter_words(words, criteria):
    for word in words:
        found = check_danwoe(criteria, word)
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
        wordsets,
        criteria,
        alpha=10.0, temp=1.0,
        misc=None,
    ):

    wordset_all = set()
    for wordset in wordsets:
        wordset_all.update(wordset)

    req_list = set()
    for criterion in criteria:
        match criterion[0]:
            case 'IncludeCombs':
                cands_seqs = criterion[1]
                for seq in cands_labels(cands_seqs):
                    req_list.add(seq)
                print(f"∋ {cands_repat(cands_seqs)}")
            case 'ExcludeComb':
                cands_seq = criterion[1]
                print(f"∌ {cands_repat([cands_seq])}")
    req_list = list(req_list)

    words, founds = zip(*filter_words(wordset_all, criteria))
    req_stat = Counter(req_list[req_list.index(seq)] for found in founds for seq in found)

    word_props = [
        [ req_list.index(seq) for seq in found ]
        for found in founds
    ]

    sel_indexes, cnt = balanced_sample_rand(word_props, len(req_list), misc[1], alpha, initial_temperature=temp)

    print(f"{misc[1]}/{len(words)}")
    print([f"{words[idx]} {n if n > 1 else ''}" for idx, n in sorted(rle(sorted(sel_indexes)), key=lambda x: x[1], reverse=True)])
    print(', '.join(
        f"{lab}: {n}/{m}"
        for n, m, lab in sorted(map(lambda nlab: (nlab[0], req_stat[nlab[1]], nlab[1]), zip(cnt, req_list)), reverse=True)
    ))

    return [ words[idx] for idx in sorted(sel_indexes) ]

# %%
def practice_set_from_wordset(*args, **kwargs):
    view_practice_set(*args, **kwargs)

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
        wordsets, criteria,
        alpha=10.0, temp=1.0,
        misc=None
    ):

        def ser_criterion(criterion):
            match criterion[0]:
                case 'Covered':
                    allowed = criterion[1]
                    return f"C{''.join(list(sorted(set(allowed))))}"

                case 'IncludeCombs':
                    cands_seqs = criterion[1]
                    return f"I{cands_repat(cands_seqs).replace('][', ' ').replace(']|[', '|')[1:-1]}"

                case 'ExcludeComb':
                    cands_seq = criterion[1]
                    return f"E{cands_repat([cands_seq]).replace('][', ' ').replace(']|[', '|')[1:-1]}"

                case _:
                    raise Exception(f"Unrecognized criterion type: {criterion[0]}")

        self.practices.append({
            'ty': 'words',
            'ti': misc[0],
            'nu': misc[1],
            'cr': list(map(ser_criterion, criteria)),
            'al': alpha,
            'te': temp,
        })

    def add_fixed_words(self, title, words):
        self.practices.append({
            'ty': 'fixed_gulza',
            'ti': title,
            'nu': len(words),
            'wo': ' '.join(words),
        })

    def add_rand_gulza(self, title, num, gulzas):
        self.practices.append({
            'ty': 'rand_gulza',
            'ti': title,
            'nu': num,
            'gu': ''.join(gulzas),
        })

def practice_set_from_wordset(*args, **kwargs):
    view_practice_set(*args, **kwargs)
    practice.add_practice_set(*args, **kwargs)

def practice_set_from_fixed(title, gulzas):
    print(gulzas)
    practice.add_fixed_words(title, gulzas)

def practice_set_from_rand(title, num, gulzas,):
    print(gulzas)
    practice.add_rand_gulza(title, num, gulzas)


# %% =================================================================================================================yy
practice = Practice("세모e 2018")

# %% =====================================================================
# 단타입력

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가')),
    ('IncludeCombs', [[pureo('이가')[::2]], [pureo('이가')[1::2]]]),
    ], misc=("ㅇㄱ + ㅣㅏ [j k + d f]", 20)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가하자')),
    ('IncludeCombs', [[pureo('이가하자')[::2]], [pureo('이가하자')[1::2]]]),
    ], temp=0.1, misc=("ㅎㅇㄱㅈ + ㅣㅏ [h j k l + d f]", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장')),
    ('IncludeCombs', [[pureo('한장')[2::3]]]),
    ], misc=("+/ㅇㄴ [a s]", 30)
)

# %% ----------------------------------------------
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장')),
    ('IncludeCombs', [[pureo('인강한장')[::3]], [pureo('인강한장')[1::3]], [pureo('인강한장')[2::3]]]),
    ], misc=("ㅎㅇㄱㅈ +ㅣㅏ +/ㅇㄴ", 60)
)

# %%
practice_set_from_fixed("(자리) ㅁㄴ [y u]", shufle_gen_fixed('마나'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장마나')),
    ('IncludeCombs', [[pureo('머녀')[0::2]]]),
    ], misc=("+ㅁㄴ", 40)
)

# %%
practice_set_from_fixed('(자리) ㅓㅕ [r t]', shufle_gen_fixed('어여'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장어여')),
    ('IncludeCombs', [[pureo('어여')[1::2]]]),
    ], misc=("+ㅓㅕ", 40)
)

# %% -----------------------------------------------
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀')),
    ('IncludeCombs', [[pureo('머녀')[0::2]]]),
    ('IncludeCombs', [[pureo('머녀')[1::2]]]),
    ('ExcludeComb', [pureo('머녀')[0::2], pureo('어여')[1::2]]),
    ], misc=("+ㅁㄴㅓㅕ ①", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀')),
    ('IncludeCombs', [[pureo('머녀')[0::2], pureo('어여')[1::2]]]),
    ], misc=("+ㅁㄴㅓㅕ ②", 60)
)

# %%
practice_set_from_fixed('(자리) ㅅㄹ [n m]', shufle_gen_fixed('사라'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장사라')),
    ('IncludeCombs', [[pureo('사라')[::2]]]),
    ], misc=("+ㅅㄹ", 30)
)

# %%
practice_set_from_fixed('(자리) ㅗㅜ [v b]', shufle_gen_fixed('오우'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장오우')),
    ('IncludeCombs', [[pureo('오우')[1::2]]]),
    ], misc=("+ㅗㅜ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀')),
    ('IncludeCombs', [[pureo('머녀')[0::2]]]),
    ('IncludeCombs', [[pureo('어여')[1::2]]]),
    ], misc=("+ㅁㄴㅓㅕ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀사라')),
    ('IncludeCombs', [[pureo('사라')[::2]]]),
    ], misc=("+ㅁㄴㅅㄹ +ㅓㅕ", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀오우')),
    ('IncludeCombs', [[pureo('오우')[1::2]]]),
    ], misc=("+ㅁㄴ +ㅓㅕㅗㅜ", 60)
)

# %% -------------------------------------------------------
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루')),
    ('IncludeCombs', [[pureo('사라')[0::2]]]),
    ('IncludeCombs', [[pureo('오우')[1::2]]]),
    ('ExcludeComb', [pureo('사라')[0::2], pureo('오우')[1::2]]),
    ], misc=("+ㅁㄴㅅㄹ+ㅓㅕㅗㅜ ①", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루')),
    ('IncludeCombs', [[pureo('사라')[0::2], pureo('오우')[1::2]]]),
    ], misc=("+ㅁㄴㅅㄹ+ㅓㅕㅗㅜ ②", 60)
)

# %%
practice_set_from_fixed('(자리) ㄷㅂ [i o]', shufle_gen_fixed('다바'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루다바')),
    ('IncludeCombs', [[pureo('다바')[::2]]]),
    ], misc=("+ㄷㅂ", 30)
)

# %%
practice_set_from_fixed('(자리) /ㄹㄱ [e x]', shufle_gen_fixed('알악'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박')),
    ('IncludeCombs', [[pureo('알악')[2::3]]]),
    ('ExcludeComb', [pureo('오우어여이')[1::2], pureo('알악')[2::3]]),
    ], misc=("+/ㄹㄱ -ㅗㅜㅓㅕㅣ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박')),
    ('IncludeCombs', [[pureo('어여')[1::2], pureo('알')[2]]]),
    ('ExcludeComb', [pureo('오우')[1::2], pureo('악')[2]]),
    ('ExcludeComb', [pureo('오우')[1::2], pureo('알')[2]]),
    ('ExcludeComb', [pureo('어여')[1::2], pureo('악')[2]]),
    ('ExcludeComb', [pureo('일')[1], pureo('일익')[2::3]]),
    ], misc=("+/ㄹ +ㅓㅕ ②", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박')),
    ('ExcludeComb', [pureo('어여')[1::2], pureo('알')[2]]),
    ('IncludeCombs', [[pureo('오우')[1::2], pureo('악')[2]]]),
    ('ExcludeComb', [pureo('오우')[1::2], pureo('알')[2]]),
    ('ExcludeComb', [pureo('어여')[1::2], pureo('악')[2]]),
    ('ExcludeComb', [pureo('일')[1], pureo('일익')[2::3]]),
    ], misc=("+/ㄱ +ㅗㅜ ②", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박')),
    ('ExcludeComb', [pureo('어여')[1::2], pureo('알')[2]]),
    ('ExcludeComb', [pureo('오우')[1::2], pureo('악')[2]]),
    ('IncludeCombs', [[pureo('오우')[1::2], pureo('알')[2]]]),
    ('ExcludeComb', [pureo('어여')[1::2], pureo('악')[2]]),
    ('ExcludeComb', [pureo('일')[1], pureo('일익')[2::3]]),
    ], misc=("+/ㄹ +ㅗㅜ ②", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박')),
    ('ExcludeComb', [pureo('어여')[1::2], pureo('알')[2]]),
    ('ExcludeComb', [pureo('오우')[1::2], pureo('악')[2]]),
    ('ExcludeComb', [pureo('오우')[1::2], pureo('알')[2]]),
    ('IncludeCombs', [[pureo('어여')[1::2], pureo('악')[2]]]),
    ('ExcludeComb', [pureo('일')[1], pureo('일익')[2::3]]),
    ], misc=("+/ㄱ +ㅓㅕ ②", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박')),
    ('ExcludeComb', [pureo('어여')[1::2], pureo('알')[2]]),
    ('ExcludeComb', [pureo('오우')[1::2], pureo('악')[2]]),
    ('ExcludeComb', [pureo('오우')[1::2], pureo('알')[2]]),
    ('ExcludeComb', [pureo('어여')[1::2], pureo('악')[2]]),
    ('IncludeCombs', [[pureo('일')[1], pureo('일익')[2::3]]]),
    ], misc=("+/ㄹㄱ +ㅣ ②", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박')),
    ('IncludeCombs', [
        [pureo('어여')[1::2], pureo('알')[2]],
        [pureo('오우')[1::2], pureo('악')[2]],
        [pureo('오우')[1::2], pureo('알')[2]],
        [pureo('어여')[1::2], pureo('악')[2]],
        [pureo('일')[1], pureo('일익')[2::3]],
    ]),
    ], misc=("+/ㄹㄱ +ㅗㅜㅓㅕㅣ", 60)
)

# %%
practice_set_from_fixed('(자리) /ㅅㅂㅁ [q w z]', shufle_gen_fixed('앗압암'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박앗압암')),
    ('IncludeCombs', [[pureo('어여아')[1::2], pureo('앗압암')[2::3]]]),
    ('ExcludeComb', [pureo('이오우')[1::2], pureo('앗압암')[2::3]]),
    ], misc=("+/ㅅㅂㅁ +ㅏㅓㅕ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박앗압암')),
    ('ExcludeComb', [pureo('어여아')[1::2], pureo('앗압암')[2::3]]),
    ('IncludeCombs', [[pureo('이오우')[1::2], pureo('앗압암')[2::3]]]),
    ], misc=("+/ㅅㅂㅁ +ㅣㅗㅜ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박앗압암')),
    ('IncludeCombs', [[pureo('어여아오우')[1::2], pureo('압')[2::3]]]),
    ('IncludeCombs', [[pureo('어여아오우')[1::2], pureo('알')[2::3]]]),
    ], misc=("+/ㄹㅂ +ㅓㅕㅣㅏㅗㅜ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박앗압암')),
    ('IncludeCombs', [
        [pureo('어여아')[1::2], pureo('앗압암')[2::3]],
        [pureo('이오우')[1::2], pureo('앗압암')[2::3]],
    ]),
    ], misc=("+/ㅅㅂㅁ", 60)
)

# %%
practice_set_from_fixed('(자리) ㅔㅡ [c g]', shufle_gen_fixed('에으'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박앗읍암')),
    ('IncludeCombs', [[pureo('음')[1::3], pureo('응은음윽읏읍을')[2::3]]]),
    ], misc=("+ㅡ +/ㅇㄴㅁㄱㅅㅂㄹ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박엣압암')),
    ('IncludeCombs', [[pureo('엠')[1::3], pureo('엥엔엠엑')[2::3]]]),
    ('ExcludeComb', [pureo('엣')[1::2], pureo('앗압알')[2::3]]),
    ], misc=("+ㅔ +/ㅇㄴㅁㄱ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박엣압암')),
    ('ExcludeComb', [pureo('엠')[1::3], pureo('엥엔엠엑')[2::3]]),
    ('IncludeCombs', [[pureo('엣')[1::3], pureo('앗압알')[2::3]]]),
    ], misc=("+ㅔ +/ㅅㅂㄹ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박엣읍암')),
    ('IncludeCombs', [[pureo('에으')[1::2], pureo('앙안암악앗압알')[2::3]]]),
    ], misc=("+ㅔㅡ +/ㅇㄴㅁㄱㅅㅂㄹ", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박엣읍암')),
    ('IncludeCombs', [
        [pureo('어여')[1::2], pureo('알')[2]],
        [pureo('오우')[1::2], pureo('악')[2]],
        [pureo('오우')[1::2], pureo('알')[2]],
        [pureo('어여')[1::2], pureo('악')[2]],
        [pureo('일')[1], pureo('일익')[2::3]],
        [pureo('에으')[1::2], pureo('앙안암악앗압알')[2::3]]
    ]),
    ], misc=("+/ㄹㄱ, +ㅔㅡ", 60)
)

# %% =====================================================================
# 복타입력

# %%
practice_set_from_fixed('(자리) ㅊㅋㅌㅍ [hl hk hi ho]', shufle_gen_fixed('차카타파'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이아안앙머녀소루알악에으앗압암차카타파')),
    ('IncludeCombs', [[pureo('차카타파')[::2]]]),
    ], misc=("+ㅊㅋㅌㅍ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암차카타파')),
    ('IncludeCombs', [[pureo('차카타파')[::2]]]),
    ('IncludeCombs', [[pureo('자가다바하')[::2]]]),
    ], misc=("+ㅊㅋㅌㅍ +ㅈㄱㄷㅂ", 60)
)

# %%
practice_set_from_fixed('(자리) ㅐㅢㅟㅚ [df dg dc,db dv]', shufle_gen_fixed('애의위외')) # ㅚ = ㅜ + ㅣ = ㅔ + ㅣ

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암애의위외')),
    ('IncludeCombs', [[pureo('애의위외')[1::2]]]),
    ('ExcludeComb', [pureo('이아어여오우에으')[1::2]]),
    ('ExcludeComb', [pureo('애의위외')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], alpha=2.0,
    misc=("+ㅐㅢㅟㅚ -단모음 -받침 -/ㄹ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암애의위외')),
    ('IncludeCombs', [[pureo('애의위외')[1::2]]]),
    ('IncludeCombs', [[pureo('이아어여오우에으')[1::2]]]),
    ('ExcludeComb', [pureo('애의위외')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], misc=("+ㅐㅢㅟㅚ +단모음 -받침 -/ㄹ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암애의위외')),
    ('IncludeCombs', [[pureo('애의위외')[1::2], pureo('한장박앗압암')[2::3]]]),
    ('ExcludeComb', [pureo('애의위외')[1::2], pureo('달')[2::3]]),
    ], alpha=2.0,
    misc=("+ㅐㅢㅟㅚ +단모음 +받침 -/ㄹ", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암애의위외')),
    ('IncludeCombs', [[pureo('애의위외')[1::2], pureo('달')[2::3]]]),
    ], alpha=2.0,
    misc=("+ㅐㅢㅟㅚ +/ㄹ", 30)
)

# %% =========================================================
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀')),
    ('IncludeCombs', [[pureo('차카타파')[0::2]]]),
    ('IncludeCombs', [[pureo('애의위외')[1::2]]]),
    ('ExcludeComb', [pureo('차카타파')[::2], pureo('애의위외')[1::2]]),
    ], misc=("+ㅊㅋㅌㅍ +ㅐㅢㅟㅚ ①", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀')),
    ('IncludeCombs', [[pureo('차카타파')[::2], pureo('애의위외')[1::2]]]),
    ('ExcludeComb', [pureo('애의위외')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], misc=("+ㅊㅋㅌㅍ +ㅐㅢㅟㅚ ② -받침", 30)
)

# %%
# help, not enough words to cover all cases!
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀')),
    ('IncludeCombs', [[pureo('차카타파')[::2], pureo('애의위외')[1::2], pureo('한장달박앗압암')[2::3]]]),
    ], misc=("+ㅊㅋㅌㅍ +ㅐㅢㅟㅚ ② +받침", 30)
)

# %%
practice_set_from_fixed('(자리) ㄲㄸㅆㅉㅃ [jk ji jn jl jo]', shufle_gen_fixed('까따싸짜빠'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암애의위외까따싸짜빠')),
    ('IncludeCombs', [[pureo('까따싸짜빠')[::2]]]),
    ], misc=("+ㄲㄸㅆㅉㅃ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀까따싸짜빠')),
    ('IncludeCombs', [[pureo('까따싸짜빠')[::2]]]),
    ('IncludeCombs', [[pureo('차카타파')[::2]]]),
    ], alpha=2.0, misc=("+ㄲㄸㅆㅉㅃ +ㅊㅋㅌㅍ", 60)
)

# %%
practice_set_from_fixed('(자리) ㅘㅛㅠㅑ [.f .v .b .g]', shufle_gen_fixed('와요유야'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암애의위외와요유야')),
    ('IncludeCombs', [[pureo('와요유야')[1::2]]]),
    ('ExcludeComb', [pureo('애의위외')[1::2]]),
    ('ExcludeComb', [pureo('자바')[0::2], pureo('와요유야')[1::2]]),
    ('ExcludeComb', [pureo('와요유야')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], misc=("+ㅘㅛㅠㅑ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸')),
    ('IncludeCombs', [[pureo('와요유야')[1::2]]]),
    ('IncludeCombs', [[pureo('애의위외')[1::2]]]),
    ('ExcludeComb', [pureo('카타까따자바차파짜빠싸')[0::2], pureo('와요유야')[1::2]]),
    ('ExcludeComb', [pureo('와요유야')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], misc=("+ㅘㅛㅠㅑ +ㅐㅢㅟㅚ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸')),
    ('IncludeCombs', [[pureo('와요유야')[1::2], pureo('한장달박앗압암')[2::3]]]),
    ('ExcludeComb', [pureo('자바차파짜빠싸')[0::2], pureo('와요유야')[1::2]]),
    ], misc=("+ㅘㅛㅠㅑ +받침", 60)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸')),
    ('IncludeCombs', [[pureo('카타까따')[0::2], pureo('와요유야')[1::2]]]),
    ('ExcludeComb', [pureo('자바차파짜빠싸')[0::2], pureo('와요유야')[1::2]]),
    ('ExcludeComb', [pureo('카타까따')[0::2], pureo('와요유야')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], misc=("+ㅘㅛㅠㅑ +ㄲㄸ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸')),
    ('IncludeCombs', [[pureo('자바')[0::2], pureo('와요유야')[1::2]]]),
    ('ExcludeComb', [pureo('차파짜빠싸')[0::2], pureo('와요유야')[1::2]]),
    ('ExcludeComb', [pureo('자바')[0::2], pureo('와요유야')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], misc=("+ㅘㅛㅠㅑ +ㅈㅂ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸')),
    ('IncludeCombs', [[pureo('차파짜빠싸')[0::2], pureo('와요유야')[1::2]]]),
    ('ExcludeComb', [pureo('차파짜빠싸')[0::2], pureo('와요유야')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], misc=("+ㅘㅛㅠㅑ +ㅊㅍㅉㅃㅆ", 30)
)

# %% TODO
# practice_set_from_wordset([onyong_words, text_words, "촤라락 퍄티고르스키 액츄에이터 시츄에이션 위츄라 크리스챠니아 플란챠 켄챠야자 미니쮸 쬬꼼 뾰족코 뾰족뒤쥐 뾰로통 뾰루지 뺘드득 뺘무리".split()], [
#     ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸')),
#     ('IncludeCombs', [[pureo('자바차파짜빠싸')[0::2], pureo('와요유야')[1::2], pureo('한장달박앗압암')[2::3]]]),
#     ], misc=("+ㅘㅛㅠㅑ +ㅈㅂㅊㅍㅉㅃㅆ +받침", 30)
# )

# %%
practice_set_from_fixed('(자리) ㅝㅒㅖㅙ [.r .t .c .df]', shufle_gen_fixed('워얘예왜'))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸워얘예왜')),
    ('IncludeCombs', [[pureo('워얘예왜')[1::2]]]),
    ('ExcludeComb', [pureo('와요유야')[1::2]]),
    ('ExcludeComb', [pureo('자바짜빠차파')[0::2], pureo('와요유야워얘예왜')[1::2]]),
    ('ExcludeComb', [pureo('와요유야워얘예왜')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], alpha=2.0,
    misc=("+ㅝㅒㅖㅙ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸워얘예왜')),
    ('IncludeCombs', [[pureo('워얘예왜')[1::2]]]),
    ('IncludeCombs', [[pureo('와요유야')[1::2]]]),
    ('ExcludeComb', [pureo('자바짜빠차파')[0::2], pureo('와요유야워얘예왜')[1::2]]),
    ('ExcludeComb', [pureo('와요유야워얘예왜')[1::2], pureo('한장달박앗압암')[2::3]]),
    ], alpha=2.0,
    misc=("+ㅝㅒㅖㅙ +ㅘㅛㅠㅑ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸워얘예왜')),
    ('IncludeCombs', [[pureo('워얘예왜')[1::2], pureo('한장달박앗압암')[2::3]]]),
    ('ExcludeComb', [pureo('자바짜빠차파')[0::2], pureo('와요유야워얘예왜')[1::2]]),
    ], alpha=2.0,
    misc=("+ㅝㅒㅖㅙ +받침", 70)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸워얘예왜')),
    ('IncludeCombs', [[pureo('자바짜빠차파')[0::2], pureo('워얘예왜')[1::2]]]),
    ], alpha = 2.0,
    misc=("+ㅝㅒㅖㅙ +ㅈㅂ", 60)
)

# %%
# practice_set_from_fixed('+ㅝㅒㅖㅙ 1 ②', [ jamo.j2h(c,v) for c in pureo('뱌자빠짜')[::2] for v in pureo('워얘예왜')[1::2] ])
# practice_set_from_rand('+ㅝㅒㅖㅙ 2 ②', 90, [ jamo.j2h(c,v,j) for c in pureo('뱌자빠짜')[::2] for v in pureo('워얘예왜')[1::2] for j in pureo('안앙알악앗압암')[2::3]+[None]])

# %%
practice_set_from_fixed('(자리) /ㅆㅊㅍㅈ [; ;q ;w ;e]', alt_gen_fixed('아았 앗앛 압앞 알앚'.split()))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웠얯옢왲')),
    ('IncludeCombs', [[pureo('았앛앞앚')[2::3]]]),
    ('ExcludeComb', [pureo('와요유야워얘예왜')[1::2], pureo('았앛앞앚')[2::3]])
    ], misc=("+/ㅆㅊㅍㅈ", 30)
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웠얯옢왲')),
    ('IncludeCombs', [[pureo('와요유야워얘예왜')[1::2], pureo('았앛앞앚')[2::3]]])
    ], misc=("+/ㅆㅊㅍㅈ +.모음", 30)
)

# %%
practice_set_from_fixed('(자리) /ㄷㅋㅎㅀ [;z ;x ;s ;a]', alt_gen_fixed('암앋 악앜 안앟 앙앓'.split()))

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웓얰옣왫')),
    ('IncludeCombs', [[pureo('앋앜앟앓')[2::3]]]),
    ('ExcludeComb', [pureo('와요유야워얘예왜')[1::2], pureo('앋앜앟앓')[2::3]])
    ], alpha=2.0,
    misc=("+/ㄷㅋㅎㅀ", 30)
)

# %% TODO
# practice_set_from_wordset([onyong_words, text_words], [
#     ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웓얰옣왫')),
#     ('IncludeCombs', [[pureo('와요유야워얘예왜')[1::2], pureo('앋앜앟앓')[2::3]]])
#     ], alpha=2.0,
#     misc=("+/ㄷㅋㅎㅀ +.", 30)
# )

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웠얯옢왲웓얰옣왫')),
    ('IncludeCombs', [[pureo('았앛앞앚')[2::3]], [pureo('앋앜앟앓')[2::3]]]),
    ], alpha=2.0,
    misc=("+/ㅆㅊㅍㅈ +/ㄷㅋㅎㅀ ⓪", 30)
)

# %% ==================================================================
practice_set_from_rand('복모음/겹자음 랜덤글자', 120, [
    jamo.j2h(c,v,j)
    for c in pureo('아가하자마나사라다바차카타파까따싸짜빠')[::2]
    for v in pureo('와요유야워얘예왜')[1::2]
    for j in pureo('았앛앞앚앋앜앟앓')[2::3]
])

# %%
# '앆앍' ㅇㄱ ㅁㄱ
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웠얯옢왲웓얰옣왫앆앍')),
    ('IncludeCombs', [[pureo('앆앍')[2::3]]]),
    ], misc=('/ㄲㄺ [ax zx]', 20)
)

# %%
# '앏앐앖' ㄹㅂ ㄹㅅ ㅂㅅ
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웠얯옢왲웓얰옣왫앏앐앖')),
    ('IncludeCombs', [[pureo('앏앐앖')[2::3]]]),
    ], misc=('/ㄼㄽㅄ [ew eq wq]', 30)
)

# %%
# '앉않앝' ㄴㄹ ㄴㅇ ㄴㅁ/ㄹㅂㅆ
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웠얯옢왲웓얰옣왫앉않앝')),
    ('IncludeCombs', [[pureo('앉않앝')[2::3]]]),
    ], misc=('/ㄵㄶㅌ [se sa zs,ew;]', 30)
)

# %%
# '앑앒' ㅇㅁ ㅇㅂ
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웠얯옢왲웓얰옣왫앑앒')),
    ('IncludeCombs', [[pureo('앑앒')[2::3]]]),
    ], misc=('/ㄾㄿ [az aw]', 20)
)

# %%
# '앇앎' ㄱㅁㅆ ㅂㅅㅆ/ㄹㅁ
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('이가한장머녀소루달박에으앗압암채킈튀푀꽈뚀쮸뺘싸웠얯옢왲웓얰옣왫앇앎')),
    ('IncludeCombs', [[pureo('앇앎')[2::3]]]),
    ], misc=('/ㄳㄻ [xz; wq;]', 20)
)

# %%
with open("../assets/data/practices_semoe2018.json", "wt") as f:
    json.dump(practice.practices, f, ensure_ascii=False)


# %% =================================================================================================================yy
practice = Practice('공세벌식 390')

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아기')),
    ('IncludeCombs', [[pureo('아기')[0::2],pureo('아기')[1::2]]]),
    ], misc=('ㅇㄱ + ㅏㅣ', 30),
)

#%%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아기자바')),
    ('IncludeCombs', [[pureo('자바')[::2]]]),
    ], misc=('+ㅈㅂ', 30),
)

#%%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아기자바인잉')),
    ('IncludeCombs', [[pureo('인잉')[2::3]]]),
    ], misc=('+/ㄴㅇ', 30),
)

#%%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아기자바인잉')),
    ('IncludeCombs', [[pureo('아기자바')[0::2], pureo('아기자바')[1::2], pureo('인잉')[2::3]]]),
    ], misc=('기본자리', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가자바인잉느트')),
    ('IncludeCombs', [[pureo('느트')[0::2]], [pureo('느트')[1::2]]]),
    ], misc=('가운뎃줄', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가자바인잉느트오우')),
    ('IncludeCombs', [[pureo('오우')[1::2]]]),
    ], misc=('ㅗㅜ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트오우')),
    ('IncludeCombs', [[pureo('까짜빠')[::2]]]),
    ], misc=('ㄲㅉㅃ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉리디띠')),
    ('IncludeCombs', [[pureo('리디띠')[::2]]]),
    ], misc=('ㄹㄷ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠')),
    ('IncludeCombs', [[pureo('리디띠')[::2]]]),
    ('IncludeCombs', [[pureo('느트')[0::2]], [pureo('느트')[1::2]]]),
    ], misc=('ㄹㄷ+ㄴㅌㅡ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트오우리디띠')),
    ('IncludeCombs', [[pureo('리디띠')[::2], pureo('오우')[1::2]]]),
    ], misc=('ㄹㄷ+ㅗㅜ', 20),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉미치파')),
    ('IncludeCombs', [[pureo('미치파')[::2]]]),
    ], misc=('ㅁㅊㅍ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치파')),
    ('IncludeCombs', [[pureo('미치파')[::2]]]),
    ('IncludeCombs', [[pureo('느트리디띠')[::2]]]),
    ], misc=('ㅁㅊㅍ+ㄴㅌㄹㄷ+ㅡ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느타오우리디띠미치파')),
    ('IncludeCombs', [[pureo('미치파')[::2], pureo('오우')[1::2]]]),
    ], misc=('ㅁㅊㅍ+ㅗㅜ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉여애어에')),
    ('IncludeCombs', [[pureo('여애어에')[1::2]]]),
    ], misc=('ㅕㅐㅓㅔ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트여애어에')),
    ('IncludeCombs', [[pureo('여애어에')[1::2]]]),
    ('IncludeCombs', [[pureo('느트')[0::2]], pureo('느트')[1::2]]),
    ], misc=('ㅕㅐㅓㅔ+ㄴㅌㅡ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠여애어에')),
    ('IncludeCombs', [[pureo('리디띠')[::2], pureo('여애어에')[1::2]]]),
    ], misc=('ㅕㅐㅓㅔ+ㄹㄷ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피여애어에')),
    ('IncludeCombs', [[pureo('미치피')[::2], pureo('여애어에')[1::2]]]),
    ], misc=('ㅕㅐㅓㅔ+ㅁㅊㅍ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트오우여애어에')),
    ('IncludeCombs', [[pureo('여애어에')[1::2]]]),
    ('IncludeCombs', [[pureo('오우')[1::2]]]),
    ], misc=('ㅕㅐㅓㅔ+ㅗㅜ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에')),
    ('IncludeCombs', [[pureo('라다마차파')[::2], pureo('여애어에오우')[1::2]]]),
    ], misc=('ㅕㅐㅓㅔ+ㅗㅜ+ㄹㄷㅁㅊㅍ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉사싸하')),
    ('IncludeCombs', [[pureo('사싸하')[::2]]]),
    ], misc=('ㅅㅎ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피사싸하')),
    ('IncludeCombs', [[pureo('사싸하')[::2]]]),
    ('IncludeCombs', [[pureo('느트리디띠미치피')[::2]]]),
    ], misc=('ㅅㅎ+ㄴㅌ+ㄹㄷㅁㅊㅍ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하')),
    ('IncludeCombs', [[pureo('사싸하')[::2], pureo('오우여애어에')[1::2]]]),
    ], misc=('ㅅㅎ+ㅗㅜ+ㅕㅐㅓㅔ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트암악')),
    ('IncludeCombs', [[pureo('암악')[2::3]]]),
    ], misc=('/ㅁㄱ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피사싸하암악')),
    ('IncludeCombs', [[pureo('암악')[2::3]]]),
    ('IncludeCombs', [[pureo('리디띠미치피사싸하')[::2]]]),
    ], misc=('/ㅁㄱ+ㄹㄷㅁㅊㅍㅅㅎ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악')),
    ('IncludeCombs', [[pureo('오우여애어에')[1::2], pureo('암악')[2::3]]]),
    ], misc=('/ㅁㄱ+ㅗㅜㅕㅐㅓㅔ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트앗알')),
    ('IncludeCombs', [[pureo('앗알')[2::3]]]),
    ], misc=('/ㅅㄹ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피사싸하앗알')),
    ('IncludeCombs', [[pureo('앗알')[2::3]]]),
    ('IncludeCombs', [[pureo('리디띠미치피사싸하')[::2]]]),
    ], misc=('/ㅅㄹ+ㄹㄷㅁㅊㅍㅅㅎ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앗알')),
    ('IncludeCombs', [[pureo('오우여애어에')[1::2], pureo('앗알')[2::3]]]),
    ], misc=('/ㅅㄹ+ㅗㅜㅕㅐㅓㅔ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앋앛')),
    ('IncludeCombs', [[pureo('앋앛')[2::3]]]),
    ], misc=('/ㄷㅊ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앞앝앜')),
    ('IncludeCombs', [[pureo('앞앝앜')[2::3]]]),
    ], misc=('/ㅍㅌㅋ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앋앛앞앝앜')),
    ('IncludeCombs', [[pureo('앋앛앞앝앜')[2::3]]]),
    ], misc=('/ㄷㅊㅍㅌㅋ', 30),
)

# %%
# practice_set_from_wordset([onyong_words, text_words],
#     pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜'),
#     [ pureo('암악앗알앋앛')[2::3], pureo('앞앝앜')[2::3], ],
#     misc=('/ㅁㄱㅅㄹㄷㅊ+/ㅍㅌㅋ', 10),
# )

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜')),
    ('IncludeCombs', [[ pureo('암악앗알앋앛앞앝앜')[2::3], ]]),
    ], misc=('/ㅁㄱ+/ㅅㄹ+/ㄷㅊ+/ㅍㅌㅋ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하앟았압')),
    ('IncludeCombs', [[pureo('앟았압')[2::3]]]),
    ], misc=('/ㅎㅆㅂ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앟았압')),
    ('IncludeCombs', [[pureo('앟았압')[2::3]]]),
    ('IncludeCombs', [[pureo('암악앗알')[2::3]]]),
    ], misc=('/ㅎㅆㅂ+/ㅁㄱㅅㄹ', 30),
)

# %%
# practice_set_from_wordset([onyong_words, text_words],
#     pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압'),
#     [pureo('앟았압')[2::3], pureo('앞앝앜')[2::3]],
#     misc=('/ㅎㅆㅂ+/앞앝앜', 60),
# )

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피사싸하요유야')),
    ('IncludeCombs', [[pureo('요유야')[1::2]]]),
    ], misc=('ㅛㅠㅑ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하요유야')),
    ('IncludeCombs', [[pureo('요유야')[1::2]]]),
    ('IncludeCombs', [[pureo('오우여애어에')[1::2]]]),
    ], misc=('ㅛㅠㅑ+ㅗㅜㅕㅐㅓㅔ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알요유야')),
    ('IncludeCombs', [[pureo('요유야')[1::2], pureo('암악앗알')[2::3]]]),
    ], misc=('ㅛㅠㅑ+/ㅁㄱㅅㄹ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야')),
    ('IncludeCombs', [[pureo('요유야')[1::2], pureo('앋앛앟았압')[2::3]]]),
    ], misc=('ㅛㅠㅑ+/ㄷㅊㅍㅌㅋㅎㅆㅂ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('컞')[:1]),
    ('IncludeCombs', [[pureo('컞')[0]]]),
    ], misc=('ㅋ', 15),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('컞')[:2]),
    ('IncludeCombs', [[pureo('컞')[1]]]),
    ], misc=('ㅒ', 15),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('콎')[:2]),
    ('IncludeCombs', [[pureo('콎')[1]]]),
    ], misc=('ㅖ', 15),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야') + pureo('콎')[:3]),
    ('IncludeCombs', [[pureo('콎')[2]]]),
    ], misc=('/ㅈ', 15),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎')),
    ('IncludeCombs', [[pureo('컞')[0]], [pureo('컞')[1]], [pureo('콎')[1]], [pureo('콎')[2]]]),
    ], misc=('ㅋ ㅒ ㅖ /ㅈ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위')),
    ('IncludeCombs', [[pureo('와외위')[1::2]]]),
    ], misc=('ㅘㅚㅟ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎왜워웨')),
    ('IncludeCombs', [[pureo('왜워웨')[1::2]]]),
    ], misc=('ㅙㅝㅞ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨')),
    ('IncludeCombs', [[pureo('와외위')[1::2]]]),
    ('IncludeCombs', [[pureo('왜워웨')[1::2]]]),
    ], misc=('ㅘㅚㅟ+ㅙㅝㅞ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의')),
    ('IncludeCombs', [[pureo('의')[1::2]]]),
    ], misc=('ㅢ', 15),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의')),
    ('IncludeCombs', [[pureo('의')[1::2]]]),
    ('IncludeCombs', [[pureo('와외위왜워웨')[1::2]]]),
    ], misc=('ㅢ+ㅘㅚㅟㅙㅝㅞ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆')),
    ('IncludeCombs', [[pureo('않앍앆')[2::3]]]),
    ], misc=('ㄶㄺㄲ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의앖앎앓')),
    ('IncludeCombs', [[pureo('앖앎앓')[2::3]]]),
    ], misc=('ㅄㄻㅀ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆앖앎앓읷앉앏')),
    ('IncludeCombs', [[pureo('앇앉앏')[2::3]]]),
    ], misc=('ㄳㄵㄼ', 30),
)

# %%
practice_set_from_wordset([onyong_words, text_words], [
    ('Covered', pureo('아가까자짜바빠인잉느트리디띠미치피오우여애어에사싸하암악앗알앋앛앞앝앜앟았압요유야컞콎와외위왜워웨의않앍앆앖앎앓읷앉앏')),
    ('IncludeCombs', [[pureo('암악앗알았압')[2::3]]]),
    ('IncludeCombs', [[pureo('앋앛앟앞앝앜앚')[2::3]]]),
    ], misc=('/ㄷㅊㅎㅍㅌㅋㅈ++', 30),
)

# %%
pi = """
3.1415926535 8979323846 2643383279 5028841971 6939937510
  5820974944 5923078164 0628620899 8628034825 3421170679
  8214808651 3282306647 0938446095 5058223172 5359408128
  4811174502 8410270193 8521105559 6446229489 5493038196
"""
#  4428810975 6659334461 2847564823 3786783165 2712019091
#  4564856692 3460348610 4543266482 1339360726 0249141273
#  7245870066 0631558817 4881520920 9628292540 9171536436
#  7892590360 0113305305 4882046652 1384146951 9415116094
#  3305727036 5759591953 0921861173 8193261179 3105118548
#  0744623799 6274956735 1885752724 8912279381 8301194912

pi = pi.replace(' ', '').replace('\n', '')[2:]

from itertools import batched
import random

puncs = ''';<>/':"!,.'''

pi_words = [
    ''.join(chunk[:3] + (random.choice(puncs),) + chunk[3:] + (random.choice(puncs),))
    for chunk in batched(pi, 6)
]

# practice_set_from_fixed('π500', pi_words)
practice_set_from_fixed('π200', pi_words)

# %%
with open("../assets/data/practices_kong390.json", "wt") as f:
    json.dump(practice.practices, f, ensure_ascii=False)
