#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Status {
    // used in status line display
    pub wrong: u32,
    pub finished: u32,
    pub millis: u128,
    pub time_active: bool,
    pub typed: u32,
    pub points: u32,
}

impl Status {
    pub fn set_points(&mut self) {
        let speed = self.speed();
        let coef = self.accuracy_coef();
        self.points = (speed * coef) as u32;
    }

    pub fn speed(&self) -> f32 {
        let elapsed = if self.millis > 0 { self.millis } else { 1 };
        self.typed as f32 / (elapsed as f32 / 1000.0) * 60.0
    }

    pub fn accuracy_coef(&self) -> f32 {
        let accuracy = self.accuracy();
        1.0 - (1.0 - accuracy.powi(4)).sqrt()
    }

    pub fn accuracy(&self) -> f32 {
        if self.typed > 0 {
            self.typed.saturating_sub(self.wrong) as f32 / self.typed as f32
        } else { 1.0 }
    }
}

use dioxus_router::routable;

impl routable::FromRouteSegment for Status {
    type Err = String;

    fn from_route_segment(route: &str) -> Result<Self,Self::Err> {
        // println!("from route seg: {route}");
        let mut it = route.split(',');
        Ok(Self {
            wrong:      it.next().unwrap().parse().unwrap(),
            finished:   it.next().unwrap().parse().unwrap(),
            millis:     it.next().unwrap().parse().unwrap(),
            time_active:it.next().unwrap().parse().unwrap(),
            typed:      it.next().unwrap().parse().unwrap(),
            points:     it.next().unwrap().parse().unwrap(),
        })
    }
}

impl routable::ToRouteSegments for Status {
    fn display_route_segments(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{},{},{},{},{},{}", self.wrong, self.finished, self.millis, self.time_active, self.typed, self.points)
    }
}

impl std::fmt::Display for Status {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{},{},{},{},{},{}", self.wrong, self.finished, self.millis, self.time_active, self.typed, self.points)
    }
}

#[derive(Clone, Debug, serde::Serialize, serde::Deserialize)]
pub struct PracticeHistoryRecord {
    pub practice_id: u32,
    pub created_at: i32,
    pub wrong_cnt: u32,
    pub word_cnt: u32,
    pub millis: u128,
    pub typing_cnt: u32,
    pub points: u32,
}

impl PracticeHistoryRecord {
    pub fn from_status(id: u32, time: i32, status: &Status) -> Self {
        Self {
            practice_id: id,
            created_at: time,
            wrong_cnt: status.wrong,
            word_cnt: status.finished,
            millis: status.millis,
            typing_cnt: status.typed,
            points: status.points,
        }
    }

    pub fn to_status(&self) -> Status {
        Status {
            wrong: self.wrong_cnt,
            finished: self.word_cnt,
            millis: self.millis,
            time_active: false,
            typed: self.typing_cnt,
            points: self.points,
        }
    }
}


pub struct ResultSummary {
    pub id: u32,
    pub title: String,
    pub num_words: u32,
    pub points: Option<u32>,
    pub date: Option<chrono::DateTime<chrono::Local>>,
}

pub fn progress_coef(points: u32, max: u32) -> f32 {
    // this quintic polynoial maps points to progress coefficient
    // it was selected after hand-tuning for desirable curve shape with following criteria
    // - maps [0, max_speed] to [0,1]
    // - steep with low points to encourage beginners
    // - steep with high points to raise discrimination
    // Note that the returned value may go outside the unit range; the caller should appropriately clamp it.

    // the polynomial is specifically calculated to go through points
    // (15, 0.1), (45, 0.9) (100, 1), be odd
    // then translated, scaled to fit in the range
    let x = points as f64 / max as f64 - 0.5;
    let a = 680_000.0 / 140_049.0;
    let b =  19_900.0 / 140_049.0;
    let c =  10_286.0 /  15_561.0;

    (a * x.powi(5) + b * x.powi(3) + c * x) as f32 + 0.5
}

pub fn progress_bar(coef: f32, num: usize) -> (usize, f32) {
    if coef >= 1.0 {
        (num-1, 1.0)
    } else {
        let interval = 1.0 / num as f32;
        let v = coef / interval;
        (v.floor() as usize, v.fract())
    }
}

pub const SCRIPT_CLEAR_INPUT_CONTENT: &str = r#"
    const el = document.getElementById('input');
    el.value = '';
"#;

pub const SCRIPT_FIX_INPUT_CURSOR_END: &str = r#"
    const el = document.getElementById('input');
    el.focus();
    const length = el.value.length;
    el.setSelectionRange(length, length);
"#;

const CHO_DEC_BASE: u32 = 0x1100;
const JUN_DEC_BASE: u32 = 0x1161;
const JON_DEC_BASE: u32 = 0x11A7;

const CHO_TASU: [u32; 19] = [1,2,1,1,2,1,1,1,2,1,2,1,1,2,1,1,1,1,1];
const JUN_TASU: [u32; 21] = [1,1,1,2,1,1,1,1,1,2,2,2,1,1,2,2,2,1,1,1,1];
const JON_TASU: [u32; 28] = [0,1,2,2,1,3,1,2,1,2,2,2,2,3,3,2,1,1,2,1,1,1,2,2,2,2,2,1];

#[derive(Debug, Clone, PartialOrd, Ord, PartialEq, Eq)]
enum JamoKind {
    Cho(u32), Jun(u32), Jon(u32)
}

impl JamoKind {
    fn reveal(c: char) -> Option<Self> {
        match c as u32 {
            codepoint if (CHO_DEC_BASE..CHO_DEC_BASE+CHO_TASU.len() as u32).contains(&codepoint) => Some(JamoKind::Cho(codepoint - CHO_DEC_BASE)),
            codepoint if (JUN_DEC_BASE..JUN_DEC_BASE+JUN_TASU.len() as u32).contains(&codepoint) => Some(JamoKind::Jun(codepoint - JUN_DEC_BASE)),
            codepoint if (JON_DEC_BASE..JON_DEC_BASE+JON_TASU.len() as u32).contains(&codepoint) => Some(JamoKind::Jon(codepoint - JON_DEC_BASE)),
            _ => None,
        }
    }
}

fn gulza_decompose(c: char) -> Option<(char, char, Option<char>)> { unsafe {
    let codepoint = c as u32;
    if ! (0xAC00..=0xD7A3).contains(&codepoint) { return None; }

    let ord = codepoint - 0xAC00;
    let cho = ord / 588;
    let jun = (ord % 588) / 28;
    let jon = ord % 28;

    Some((
        char::from_u32_unchecked(cho + CHO_DEC_BASE),
        char::from_u32_unchecked(jun + JUN_DEC_BASE),
        if jon > 0 {
            Some(char::from_u32_unchecked(jon + JON_DEC_BASE))
        } else { None }
    ))
}}

fn hangul_decompose(orig: &str) -> Vec<char> {
    let mut ret = vec![];

    for c in orig.chars() {
        if let Some((cho, jung, jong)) = gulza_decompose(c) {
            ret.push(cho); ret.push(jung);
            if let Some(jong) = jong {
                ret.push(jong)
            }
        } else {
            // put non-hangul char as is
            ret.push(c);
        }
    }

    ret
}

fn tasu_decomposed(c: char) -> u32 {
    match JamoKind::reveal(c) {
        Some(JamoKind::Cho(idx)) => CHO_TASU[idx as usize],
        Some(JamoKind::Jun(idx)) => JUN_TASU[idx as usize],
        Some(JamoKind::Jon(idx)) => JON_TASU[idx as usize],
        None => 1,
    }
}

// returns (str_a exclusive tasu count, common tasu count, str_b exclusive tasu count)
pub fn tasu_compare(str_a: &str, str_b: &str) -> (u32, u32, u32) {
    let str_a = hangul_decompose(str_a);
    let str_b = hangul_decompose(str_b);

    // lcs

    let m = str_a.len();
    let n = str_b.len();
    let mut dp = vec![vec![0usize; n + 1]; m + 1];

    for i in 0 ..m {
        for j in 0..n {
            dp[i+1][j+1] =
                if str_a[i] == str_b[j] {
                    dp[i][j] + 1
                } else {
                    dp[i+1][j].max(dp[i][j+1])
                };
        }
    }

    // backtrack

    let mut tasu_a = 0;
    let mut tasu_b = 0;
    let mut tasu_c = 0; // c for common

    let mut i = m;
    let mut j = n;

    while i > 0 && j > 0 {
        if str_a[i-1] == str_b[j-1] {
            tasu_c += tasu_decomposed(str_a[i-1]);
            i -= 1;
            j -= 1;
        } else if dp[i-1][j] >= dp[i][j-1] {
            tasu_a += tasu_decomposed(str_a[i-1]);
            i -= 1;
        } else {
            tasu_b += tasu_decomposed(str_b[j-1]);
            j -= 1;
        }
    }

    while i > 0 {
        tasu_a += tasu_decomposed(str_a[i-1]);
        i -= 1;
    }

    while j > 0 {
        tasu_b += tasu_decomposed(str_b[j-1]);
        j -= 1;
    }

    (tasu_a, tasu_c, tasu_b)
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, serde::Serialize, serde::Deserialize, Default, strum_macros::EnumIter, strum_macros::EnumString, strum_macros::Display)]
pub enum KeyboardLayout {
    #[strum(serialize = "공세벌식390")]
    Gong390,

    #[default]
    #[strum(serialize = "세모e2018")]
    Semoe2018,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct UserConfig {
    pub allow_del: bool,
    pub word_time: bool,
    pub max_speed: u32,
    pub layout: KeyboardLayout,
}

impl Default for UserConfig {
    fn default() -> Self {
        UserConfig {
            allow_del: true,
            word_time: false,
            max_speed: 600,
            layout: KeyboardLayout::default(),
        }
    }
}

pub struct PracticeSets {
    pub sets: Vec<Vec<Practice>>,
}

// impl PracticeSets {
//     fn load_all(file_mapping: fn(KeyboardLayout) -> std::path::PathBuf) -> std::io::Result<Self> {
//         todo!()
//     }
// }

#[derive(Debug, Clone, serde::Deserialize)]
pub struct Practice {
    #[serde(rename = "ti")]
    pub title: String,
    #[serde(rename = "nu")]
    pub num: u32,
    #[serde(flatten)]
    content: PracticeContent,
}

#[derive(Debug, Clone, serde::Deserialize)]
#[serde(tag = "ty")]
enum PracticeContent {
    #[serde(rename = "words")]
    Sampling(PracticeContentSampling),
    #[serde(rename = "fixed_gulza")]
    Fixed(PracticeContentFixed),
    #[serde(rename = "rand_gulza")]
    Rand(PracticeContentRand),
}

#[derive(Debug, Clone, serde::Deserialize)]
struct PracticeContentFixed {
    #[serde(rename = "wo")]
    words: String,
}

#[derive(Debug, Clone, serde::Deserialize)]
struct PracticeContentRand {
    #[serde(rename = "gu")]
    chars: String,
}

#[derive(Debug, Clone, serde::Deserialize)]
struct PracticeContentSampling {
    #[serde(rename = "cr")]
    criteria: Vec<Criterion>,
    #[serde(rename = "al")]
    alpha: f32,
    #[serde(rename = "te")]
    temp: f32,
}

type CombInst = (Option<char>, Option<char>, Option<char>);

fn show_comb_instant((cho, jun, jon): CombInst) -> String {
    let mut buf = String::new();
    if let Some(c) = cho { buf.push(c) }
    if let Some(c) = jun { buf.push(c) }
    if let Some(c) = jon { buf.push(c) }
    buf
}

impl PracticeContentSampling {
    pub fn check(&self, word: &str) -> Option<u128> {
        let mut sigidx_bottom = 0;
        let mut signature = 0;
        for criterion in &self.criteria {
            signature |= criterion.check(word, &mut sigidx_bottom)?;
        }
        Some(signature)
    }

    pub fn index_comb(&self, index: u8) -> Option<CombInst> {
        let mut comb_index = index;
        for criterion in &self.criteria {
            if let Some(x) = criterion.index_comb(comb_index) { return Some(x) }
            comb_index -= criterion.comb_size()
        }
        None
    }

    fn comb_size(&self) -> u8 {
        self.criteria.iter().map(Criterion::comb_size).sum()
    }

}

#[derive(Debug, Clone)]
enum Criterion {
    Covered(Vec<char>),
    IncludeCombs(SmallVec<[JamoCombination; 1]>),
    ExcludeComb(JamoCombination),
}

impl<'de> serde::Deserialize<'de> for Criterion {
    fn deserialize<D>(deser: D) -> Result<Self, D::Error>
    where D: serde::Deserializer<'de>
    {
        use serde::Deserialize;
        let s = String::deserialize(deser)?;

        fn parse_jamo_comb(comb: &str) -> Result<JamoCombination, String> {
            let mut jamo_comb = JamoCombination::new();
            let mut chojunjon = JamoKind::Cho(0);
            for seg in comb.split(' ') {
                let Some(c) = seg.chars().next() else {
                    return Err("null jamo combination segment".into());
                };

                let Some(k) = JamoKind::reveal(c) else {
                    return Err(format!("non-hangul jamo combination segment: {:?}", seg.chars().collect::<Vec<_>>()));
                };

                if k < chojunjon {
                    return Err(format!("out of order jamo combination segment: {:?}", seg.chars().collect::<Vec<_>>()));
                }

                if ! seg.chars().all(|c|
                    JamoKind::reveal(c).as_ref().map(std::mem::discriminant) == Some(std::mem::discriminant(&k))
                ) {
                    return Err(format!("non-uniform jamo combination segment: {:?}", seg.chars().collect::<Vec<_>>()));
                }

                let (jcw, chojunjon) = match k {
                    JamoKind::Cho(_) => (&mut jamo_comb.cho, JamoKind::Jun(0)),
                    JamoKind::Jun(_) => (&mut jamo_comb.jun, JamoKind::Jon(0)),
                    JamoKind::Jon(_) => (&mut jamo_comb.jon, JamoKind::Jon(u32::MAX)),
                };

                *jcw = Some(seg.chars().collect());
            }

            Ok(jamo_comb)
        }

        use serde::de::Error;
        match s.chars().next() {
            None => Err(serde::de::Error::custom("empty criterion")),
            Some('C') => {
                Ok(Criterion::Covered(s[1..].chars().collect()))
            }
            Some('I') => {
                let alts = s[1..].split('|').map(|comb|
                    parse_jamo_comb(comb).map_err(D::Error::custom)
                ).collect::<Result<_, D::Error>>()?;
                Ok(Criterion::IncludeCombs(alts))
            }
            Some('E') => {
                let comb = parse_jamo_comb(&s[1..]).map_err(D::Error::custom)?;
                Ok(Criterion::ExcludeComb(comb))
            }
            Some(c) => {
                Err(D::Error::custom("unrecognized criterion prefix"))
            }
        }
    }
}

impl Criterion {
    // check given word for the criterion, returns signature.
    // signature is a bitvector for IncludeCombination index.
    fn check(&self, word: &str, sigidx_bottom: &mut u8) -> Option<u128> {
        match self {
            Criterion::Covered(allowed) => {
                let pass = hangul_decompose(word).into_iter().all(|c| allowed.contains(&c));
                if pass { Some(0) } else { None }
            }
            Criterion::IncludeCombs(combs) => {
                let mut signature: u128 = 0;
                // check if any of the combinations found
                for comb in combs {
                    for gulza in word.chars() {
                        // fails for any word containing non-hangul
                        let decomposed = gulza_decompose(gulza)?;
                        // construct signature for any found jamo comb
                        if let Some(comb_idx) = comb.check(decomposed) {
                            signature |= 1 << (*sigidx_bottom + comb_idx);
                        }
                    }
                    *sigidx_bottom += comb.size();
                }
                if signature > 0 { Some(signature) } else { None }
            }
            Criterion::ExcludeComb(comb) => {
                for gulza in word.chars() {
                    // fails for any word containing non-hangul
                    let decomposed = gulza_decompose(gulza)?;
                    // fails if excluded combination pattern is found
                    if comb.check(decomposed).is_some() { return None; }
                }
                Some(0)
            }
        }
    }

    fn index_comb(&self, index: u8) -> Option<CombInst> {
        match self {
            Criterion::IncludeCombs(combs) => {
                let mut comb_inner_idx = index;
                for comb in combs {
                    if let Some(x) = comb.index(comb_inner_idx) { return Some(x) }
                    comb_inner_idx -= comb.size();
                }
                None
            }
            _ => None,
        }
    }

    fn comb_size(&self) -> u8 {
        match self {
            Criterion::IncludeCombs(combs) =>
                combs.iter().map(JamoCombination::size).sum(),
            _ => 0,
        }
    }
}

#[derive(Debug, Clone)]
struct JamoCombination {
    cho: Option<SmallVec<[char; 2]>>,
    jun: Option<SmallVec<[char; 2]>>,
    jon: Option<SmallVec<[char; 2]>>,
}

impl JamoCombination {
    fn new() -> Self { Self { cho: None, jun: None, jon: None } }

    fn size(&self) -> u8 {
        ( self.cho.as_ref().map(SmallVec::len).unwrap_or(1)
        * self.jun.as_ref().map(SmallVec::len).unwrap_or(1)
        * self.jon.as_ref().map(SmallVec::len).unwrap_or(1)
        ) as u8
    }

    // if pass, returns combination index
    fn check(&self, (cho, jun, jon): (char, char, Option<char>)) -> Option<u8> {
        let mut index = 0;

        if let Some(chos) = &self.cho {
            index *= chos.len();
            index += chos.iter().position(|&c| c == cho)?;
        }

        if let Some(juns) = &self.jun {
            index *= juns.len();
            index += juns.iter().position(|&c| c == jun)?;
        }

        if let Some(jons) = &self.jon {
            if let Some(jon) = jon {
                // jonsung present, check
                index *= jons.len();
                index += jons.iter().position(|&c| c == jon)?;
            } else {
                // some are required for jon but nothing present
                return None;
            }
        }

        Some(index as u8)
    }

    fn index(&self, index: u8) -> Option<CombInst> {
        let mut index = index as usize;

        let jon = if let Some(jons) = &self.jon {
            let idx = index % jons.len();
            index /= jons.len();
            Some(jons[idx])
        } else { None };

        let jun = if let Some(juns) = &self.jun {
            let idx = index % juns.len();
            index /= juns.len();
            Some(juns[idx])
        } else { None };

        let cho = if let Some(chos) = &self.cho {
            let idx = index % chos.len();
            index /= chos.len();
            Some(chos[idx])
        } else { None };

        if index == 0 {
            Some((cho, jun, jon))
        } else { None }
    }
}

use rand::distr::{Distribution, weighted::WeightedIndex};
use rand::rngs::SmallRng;
use rand::SeedableRng;

fn balanced_sample_rand(
    elements: &[u128], // u128 acts as bitvector of booleans
    k: usize,
    m: usize,
    alpha: f32,
    initial_temperature: f32,
    rng: &mut impl rand::Rng,
    // rand_seed: u64,
) -> (Vec<usize>, Vec<usize>) {
    let n = elements.len();

    // Average number of properties per element
    let avg_r: f32 =
        elements.iter().map(|e| e.count_ones() as f32).sum::<f32>() / n as f32;

    let target = m as f32 * avg_r / k as f32;

    let mut property_counts = vec![0usize; k];
    let mut usage_counts = vec![0usize; n];
    let mut selected_indices = Vec::with_capacity(m);

    for step in 0..m {
        let mut scores = Vec::with_capacity(n);

        // ---- compute scores ----
        for (i, props) in elements.iter().enumerate() {
            let mut delta_balance = 0.0;

            for j in 0 .. k {
                if (props >> j) & 1 == 0 { continue; }
                let before = property_counts[j] as f32 - target;
                let after = (property_counts[j] as f32 + 1.0) - target;
                delta_balance += after * after - before * before;
            }

            let dup_penalty =
                alpha * (usage_counts[i] as f32).powi(2);

            scores.push(delta_balance + dup_penalty);
        }

        // ---- softmax sampling ----
        let min_score = scores
            .iter()
            .cloned()
            .fold(f32::INFINITY, f32::min);

        let temperature =
            initial_temperature * 0.95f32.powi(step as i32);

        let weights: Vec<f32> = scores
            .iter()
            .map(|&s| {
                let shifted = s - min_score;
                (-shifted / temperature).exp()
            })
            .collect();

        let dist = WeightedIndex::new(&weights)
            .expect("Invalid weight distribution");

        let chosen = dist.sample(rng);

        // ---- update state ----
        selected_indices.push(chosen);
        usage_counts[chosen] += 1;

        for j in 0 .. k {
            if (elements[chosen] >> j) & 1 == 0 { continue }
            property_counts[j] += 1;
        }
    }

    (selected_indices, property_counts)
}

use std::collections::HashSet;
use smallvec::{SmallVec, smallvec};

impl Practice {
    pub fn check(&self, word: &str) -> Option<u128> {
        match &self.content {
            PracticeContent::Sampling(pcs) =>
                pcs.check(word),

            _ => None
        }
    }

    pub fn index_comb(&self, index: u8) -> Option<CombInst> {
        match &self.content {
            PracticeContent::Sampling(pcs) =>
                pcs.index_comb(index),

            _ => None
        }
    }

    pub fn signature_combs(&self, signature: u64) -> impl Iterator<Item=Result<CombInst, ()>> + use<'_> {
        (0 .. 64).scan(signature, |sig, i| Some({
            let mask = 1 << i;
            if *sig & mask > 0 {
                let ret = self.index_comb(i).ok_or(());
                *sig &= !mask;
                Some(ret)
            } else { None }
        })).flatten()
    }

    pub fn sample_words(self: &Practice, words: &str, rng: &mut impl rand::Rng) -> Vec<String> {
        match &self.content {
            PracticeContent::Sampling(pcs) => {
                // let mut cnt = 0;
                let k = pcs.comb_size();
                let mut collected = vec![];
                let mut signatures = vec![];
                for word in words.lines() {
                    let Some(signature) = pcs.check(word) else { continue };

                    collected.push(word);
                    signatures.push(signature);

                    // cnt += 1;
                    // print!("{cnt} {word} ({signature:b}): ");
                    // for i in 0 .. k {
                    //     if (signature >> i) & 1 == 1 {
                    //         print!("'{:?}' ", pcs.index_comb(i).map(show_comb_instant).unwrap());
                    //     }
                    // }
                    // println!();
                }

                let (mut selected_indices, property_counts) = balanced_sample_rand(&signatures, k as usize, self.num as usize, pcs.alpha, pcs.temp, rng);

                // println!("words: {}/{}", collected.len(), selected_indices.len());

                // let mut cnts = if ! selected_indices.is_empty() {
                //     selected_indices.sort();

                //     // lre
                //     let mut cnts = vec![];
                //     let mut cur = selected_indices[0];
                //     let mut cnt = 0;
                //     for &idx in selected_indices.iter() {
                //         if idx == cur { cnt += 1; }
                //         else {
                //             cnts.push((cnt, collected[cur]));
                //             cur = idx; cnt = 1;
                //         }
                //     }
                //     cnts.push((cnt, collected[cur]));
                //     cnts
                // } else { vec![] };

                // cnts.sort();
                // for (cnt,s) in cnts.iter().rev() {
                //     print!("'{}: {}', ", s, cnt);
                // }
                // println!();

                // let mut ipc: Vec<_> = property_counts.iter().enumerate().collect();
                // ipc.sort_by_key(|(_i,pc)| **pc);
                // for &(i, pc) in ipc.iter().rev() {
                //     print!("'{}: {}', ", pcs.index_comb(i as u8).map(show_comb_instant).unwrap(), pc);
                // }
                // println!();

                use rand::prelude::SliceRandom;
                selected_indices.shuffle(rng);

                selected_indices.into_iter().map(|i| collected[i].to_string()).collect()
            }

            PracticeContent::Fixed(pcf) => {
                pcf.words.split(' ').map(Into::into).collect()
            }

            PracticeContent::Rand(pcr) => {
                use rand::prelude::IteratorRandom;
                pcr.chars.chars().map(Into::into).choose_multiple(rng, self.num as usize)
            }
        }
    }
}