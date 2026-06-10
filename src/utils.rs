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
        println!("from route seg: {route}");
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

const  CHO_DEC_BASE: u32 = 0x1100;
const JUNG_DEC_BASE: u32 = 0x1161;
const JONG_DEC_BASE: u32 = 0x11A7;

const  CHO_TASU: [u32; 19] = [1,2,1,1,2,1,1,1,2,1,2,1,1,2,1,1,1,1,1];
const JUNG_TASU: [u32; 21] = [1,1,1,2,1,1,1,1,1,2,2,2,1,1,2,2,2,1,1,1,1];
const JONG_TASU: [u32; 28] = [0,1,2,2,1,3,1,2,1,2,2,2,2,3,3,2,1,1,2,1,1,1,2,2,2,2,2,1];

fn gulza_decompose(c: char) -> Option<(char, char, Option<char>)> { unsafe {
    let codepoint = c as u32;
    if ! (0xAC00..=0xD7A3).contains(&codepoint) { return None; }

    let ord = codepoint - 0xAC00;
    let cho = ord / 588;
    let jung = (ord % 588) / 28;
    let jong = ord % 28;

    Some((
        char::from_u32_unchecked(cho + CHO_DEC_BASE),
        char::from_u32_unchecked(jung + JUNG_DEC_BASE),
        if jong > 0 {
            Some(char::from_u32_unchecked(jong + JONG_DEC_BASE))
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
    match c as u32 {
        codepoint if ( CHO_DEC_BASE.. CHO_TASU.len() as u32).contains(&codepoint) =>  CHO_TASU[(codepoint -  CHO_DEC_BASE) as usize],
        codepoint if (JUNG_DEC_BASE..JUNG_TASU.len() as u32).contains(&codepoint) => JUNG_TASU[(codepoint - JUNG_DEC_BASE) as usize],
        codepoint if (JONG_DEC_BASE..JONG_TASU.len() as u32).contains(&codepoint) => JONG_TASU[(codepoint - JONG_DEC_BASE) as usize],
        _ => 1,
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
    pub title: String,
    pub num: u32,
    #[serde(flatten)]
    content: PracticeContent,
}

#[derive(Debug, Clone, serde::Deserialize)]
#[serde(tag = "type")]
enum PracticeContent {
    #[serde(rename = "words")]
    Sampling(PracticeContentSampling),
    #[serde(rename = "fixed_gulza")]
    Fixed(PracticeContentFixed),
    #[serde(rename = "rand_gulza")]
    Rand(PracticeContentRand),
}

#[derive(Debug, Clone, serde::Deserialize)]
struct PracticeContentSampling {
    #[serde(deserialize_with = "postprocess_string_chars")]
    allowed: Vec<char>,
    #[serde(deserialize_with = "postprocess_string_chars")]
    required: Vec<char>,
    alpha: f32,
    temp: f32,
    mc_min: u32,
    mc_max: u32,
}

#[derive(Debug, Clone, serde::Deserialize)]
struct PracticeContentFixed {
    words: String,
}

#[derive(Debug, Clone, serde::Deserialize)]
struct PracticeContentRand {
    #[serde(rename = "gulzas")]
    chars: String,
}

fn postprocess_string_chars<'de, D>(deser: D) -> Result<Vec<char>, D::Error>
    where D: serde::Deserializer<'de>
{
    use serde::Deserialize;
    let s = String::deserialize(deser)?;
    Ok(s.chars().collect())
}

use rand::distr::{Distribution, weighted::WeightedIndex};
use rand::rngs::SmallRng;
use rand::SeedableRng;

fn balanced_sample_rand(
    elements: &[u64], // u64 acts as bitvector of booleans
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

fn check_danwoe(
    allowed: &[char],
    required: &[&[char]],
    word: &str,
    max_coupled_range: (usize, usize),
) -> u64 {
    let (min_coupled, max_coupled) = max_coupled_range;

    // ---- allowed check ----
    if ! allowed.is_empty() {
        for gulsoe in hangul_decompose(word) {
            if !allowed.contains(&gulsoe) {
                return 0;
            }
        }
    }

    // ---- generate signatures ----
    let mut gulza_sigs_by_req: SmallVec<[_; 3]>= smallvec![];
    let mut req_idx_base = 0;
    for req in required {
        // 95% of the words are leq 5 chars long
        let gulza_sigs: SmallVec<[u64; 5]> = word.chars().map(|gulza| {
            let Some((cho, jung, jong)) = gulza_decompose(gulza) else { return 0; };

            let mut signature = 0;
            let mut set_sig_on = |c|
                if let Some(i) = req.iter().position(|&x| x == c) {
                    assert!(i + req_idx_base < 64);
                    signature |= 1 << (i + req_idx_base);
                }
            ;

            set_sig_on(cho);
            set_sig_on(jung);
            if let Some(jong) = jong { set_sig_on(jong); }

            signature
        }).collect();

        gulza_sigs_by_req.push(gulza_sigs);
        req_idx_base += req.len();
    }

    // ---- coupled count per gulza ----
    let coupled = word.chars().enumerate().map(|(i, _c)| {
        // for each gulza, count the # of passed_reqs
        let passed_req_num = gulza_sigs_by_req.iter().filter(|gulza_sigs|
            gulza_sigs[i] > 0
        ).count();
        passed_req_num
    });

    if !required.is_empty() {
        if let Some(max_val) = coupled.max() {
            if max_val < min_coupled || max_val > max_coupled {
                return 0;
            }
        }
    }

    // ---- ensure all requirements satisfied at least once ----
    let mut passed_reqs: SmallVec<[bool; 3]> = smallvec![false; required.len()];

    for (i, gulza_sigs) in gulza_sigs_by_req.iter().enumerate() {
        for signature in gulza_sigs {
            passed_reqs[i] |= *signature > 0;
        }
    }

    if ! passed_reqs.into_iter().all(|b| b) {
        return 0;
    }

    // ---- collect found gulsoe ----
    let mut word_signature = 0;

    for gulza_sigs in gulza_sigs_by_req {
        for signature in gulza_sigs {
            word_signature |= signature;
        }
    }

    word_signature
}

impl Practice {
    pub fn sample_words(self: &Practice, words: &str, rng: &mut impl rand::Rng) -> Vec<String> {
        match &self.content {
            PracticeContent::Sampling(pcs) => {
                let required: SmallVec<[_; 3]> = pcs.required.split(|&c| c == ' ').collect();
                let k = required.iter().map(|req| req.len()).sum();
                let reqlist: Vec<char> = required.iter().flat_map(|req| req.iter().cloned()).collect();
                // let mut cnt = 0;

                let mut collected = vec![];
                let mut signatures = vec![];
                for word in words.lines() {
                    let signature = check_danwoe(
                        &pcs.allowed,
                        &required,
                        word,
                        (pcs.mc_min as usize, pcs.mc_max as usize),
                    );

                    if signature == 0 { continue; }
                    collected.push(word);
                    signatures.push(signature);

                    // cnt += 1;
                    // print!("{cnt} {word} ({signature:b}): ");
                    // for i in 0 .. k {
                    //     if (signature >> i) & 1 == 1 {
                    //         print!("'{}' ", reqlist[i]);
                    //     }
                    // }
                    // println!();
                }

                let (mut selected_indices, property_counts) = balanced_sample_rand(&signatures, k, self.num as usize, pcs.alpha, pcs.temp, rng);

                // let mut cnts = if ! selected_indices.is_empty() {
                //     selected_indices.sort();

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

                // let mut pcrl: Vec<_> = property_counts.iter().zip(reqlist.iter()).collect();
                // pcrl.sort();
                // for (pc, rl) in pcrl.iter().rev() {
                //     print!("'{}: {}', ", rl, pc);
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