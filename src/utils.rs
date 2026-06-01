#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Status {
    // used in status line display
    pub wrong: u32,
    pub finished: u32,
    pub secs: Option<u64>, // None when not started yet
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
        match self.secs {
            Some(secs) => {
                let elapsed = if secs > 0 { secs } else { 1 };
                self.typed as f32 / (elapsed as f32) * 60.0
            }
            _ => 0.0,
        }
    }

    pub fn accuracy_coef(&self) -> f32 {
        let accuracy = self.accuracy();
        1.0 - (1.0 - accuracy.powi(4)).sqrt()
    }

    pub fn accuracy(&self) -> f32 {
        if self.typed > 0 {
            (self.typed - self.wrong) as f32 / self.typed as f32
        } else { 1.0 }
    }
}

pub struct ResultSummary {
    pub id: u32,
    pub title: String,
    pub num_words: u32,
    pub points: Option<u32>,
    pub date: Option<chrono::DateTime<chrono::Local>>,
}

pub fn progress_coef(points: u32) -> f32 {
    // this quintic polynoial maps points to progress coefficient
    // it was selected after hand-tuning for desirable curve shape with following criteria
    // - maps [0,600] to [0,1]
    // - steep with low points to encourage beginners
    // - steep with high points to raise discrimination
    // Note that the returned value may go outside the unit range; the caller should appropriately clamp it.
    let x = points as f32;
    0.34 * (x - 300.0) / 302.0 + (0.7 * (x - 300.0) / 302.0).powi(5) + 0.5
}

pub fn progress_bar(coef: f32, num: usize) -> (usize, f32) {
    let interval = 1.0 / num as f32;
    let v = coef / interval;
    (v.floor() as usize, v.fract())
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

fn hangul_decompose(orig: &str) -> Vec<u32> {
    let mut ret = vec![];

    for c in orig.chars() {
        let codepoint = c as u32;
        if ! (0xAC00..=0xD7A3).contains(&codepoint) {
            // put non-hangul char as is
            ret.push(codepoint); continue;
        }

        let ord = codepoint - 0xAC00;
        let cho = ord / 588;
        let jung = (ord % 588) / 28;
        let jong = ord % 28;

        ret.push( cho +  CHO_DEC_BASE);
        ret.push(jung + JUNG_DEC_BASE);
        if jong > 0 {
            ret.push(jong + JONG_DEC_BASE);
        }
    }

    ret
}

fn tasu_decomposed(codepoint: u32) -> u32 {
    match codepoint {
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

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct UserConfig {
    pub allow_del: bool,
    pub word_time: bool,
    pub max_speed: u32,
}

impl Default for UserConfig {
    fn default() -> Self {
        UserConfig {
            allow_del: true,
            word_time: false,
            max_speed: 600,
        }
    }
}