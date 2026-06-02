use rand::prelude::SliceRandom;
use rand::SeedableRng;

use dioxus::prelude::*;

#[derive(Debug, Clone, Routable, PartialEq)]
#[rustfmt::skip]
enum Route {
    // #[layout(Navbar)]

    #[route("/")]
    Home {},
    #[route("/3berlsik/list")]
    SeoberlsikList {},
    #[route("/3berlsik/practice/:id")]
    SeoberlsikPractice { id: u32 },
    #[route("/3berlsik/result/:id")]
    PracticeResult { id: u32 },
    #[route("/error/:errmsg")]
    ErrorPage { errmsg: String },
}

mod platform;
mod utils;

fn main() {
    platform::launch_builder().launch(DBProvider);
}

#[component]
fn LaunchError() -> Element {
    let errmsg = consume_context::<String>();
    rsx! {
        ErrorPage { errmsg }
    }
}

#[component]
fn DBProvider() -> Element {
    let db = use_resource(platform::DataFetch::open);

    let config: Resource<Result<Option<_>, platform::DataFetchError>> = use_resource(move || async move {
        let db = if let Some(Ok(db)) = &*db.read() {
            Some(db.clone())
        } else { None };
        Ok(if let Some(db) = db {
            Some(db.get_userconfig().await?.unwrap_or(utils::UserConfig::default()))
        } else { None })
    });

    let ret = match (&*db.read(), &*config.read()) {
        (Some(Ok(db)), Some(Ok(Some(config)))) => {
            use_context_provider(|| db.clone());
            let config = use_signal(|| config.clone());
            use_context_provider(|| config);

            rsx! {
                App {}
            }
        }

        (Some(Err(e)), _) => rsx! { ErrorPage { errmsg: e.to_string() } },
        (_, Some(Err(e))) => rsx! { ErrorPage { errmsg: e.to_string() } },
        _ => rsx! { "Loading" },
    }; ret
}

const FONT_SCHOOL_R: Asset = asset!("assets/fonts/HakgyoansimAllimjangTTF-R.woff2");
const FONT_SCHOOL_B: Asset = asset!("assets/fonts/HakgyoansimAllimjangTTF-B.woff2");
const FONT_OMYU:     Asset = asset!("assets/fonts/omyu_pretty.woff2");
const FONT_MATERIAL: Asset = asset!("assets/fonts/materialsymbolsoutlined_v339.woff2");

#[component]
fn App() -> Element {
    use_context_provider(|| Signal::new(0.0)); // list_scroll_y

    rsx! {
        document::Link { rel: "icon", href: asset!("assets/icons/favicon.ico") }

        // document::Link { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" }

        // we need this hardcoded font definitions to make font files dioxus assets
        style { "
            @font-face {{
                font-family: 'SchoolSafetyNotification';
                src: url('{FONT_SCHOOL_R}') format('woff2');
                font-weight: 400;
                font-display: swap;
            }}
            @font-face {{
                font-family: 'SchoolSafetyNotification';
                src: url('{FONT_SCHOOL_B}') format('woff2');
                font-weight: 700;
                font-display: swap;
            }}
            @font-face {{
                font-family: 'OmuDaye';
                src: url('{FONT_OMYU}') format('woff2');
                font-weight: normal;
                font-display: swap;
            }}
            @font-face {{
                font-family: 'Material Symbols Outlined';
                font-style: normal;
                font-weight: 400;
                src: url('{FONT_MATERIAL}') format('woff2');
            }}
            .material-symbols-outlined {{
                font-family: 'Material Symbols Outlined';
                font-weight: normal;
                font-style: normal;
                // font-size: 24px;
                line-height: 1;
                letter-spacing: normal;
                text-transform: none;
                display: inline-block;
                white-space: nowrap;
                word-wrap: normal;
                direction: ltr;
                -moz-font-feature-settings: 'liga';
                -moz-osx-font-smoothing: grayscale;
            }}
            "
        }

        document::Link { rel: "stylesheet", href: asset!("assets/css/practice.css") }
        document::Link { rel: "stylesheet", href: asset!("assets/css/datagrid.css") }
        document::Link { rel: "stylesheet", href: asset!("assets/css/misc.css") }

        document::Title { "typing practice" }

        Router::<Route> {}
    }
}

/// Home page
#[component]
fn Home() -> Element {
    let nav = use_navigator();
    nav.push(Route::SeoberlsikList {});
    rsx! {}
}

#[derive(Debug, Clone, PartialEq)]
enum HorizontalAlign {
    Left, Center, Right
}

#[derive(Debug, Clone, PartialEq)]
struct ColumnDecl {
    name: String,
    sort: i8,
    align: HorizontalAlign,
    width: usize,
}

#[derive(Debug, Clone, PartialEq)]
#[allow(unpredictable_function_pointer_comparisons)]
struct ColumnData<T> {
    inner: Vec<T>,
    render: fn(&T) -> Element,
}

#[derive(Debug, Clone, PartialEq)]
struct Column<T> {
    decl: ColumnDecl,
    data: ColumnData<T>,
}

#[derive(Debug, Clone, PartialEq)]
struct GridData {
    title: Column<(String, u32)>,
    num_words: Column<u32>,
    points: Column<(Option<u32>, u32)>,
    date: Column<Option<chrono::DateTime<chrono::Local>>>,
}

impl GridData {
    fn num_cols(&self) -> usize { 4 }
    fn num_rows(&self) -> usize { self.title.data.inner.len() }

    fn get_decl(&self, col_idx: usize) -> &ColumnDecl {
        match col_idx {
            0 => &self.title.decl,
            1 => &self.num_words.decl,
            2 => &self.points.decl,
            3 => &self.date.decl,
            _ => panic!(),
        }
    }

    fn get_render(&self, col_idx: usize, row_idx: usize) -> Element {
        match col_idx {
            0 => (self.title.data.render)(&self.title.data.inner[row_idx]),
            1 => (self.num_words.data.render)(&self.num_words.data.inner[row_idx]),
            2 => (self.points.data.render)(&self.points.data.inner[row_idx]),
            3 => (self.date.data.render)(&self.date.data.inner[row_idx]),
            _ => panic!(),
        }
    }

    fn verify(&self) {
        let num_rows = self.num_rows();
        assert_eq!(num_rows, self.title.data.inner.len());
        assert_eq!(num_rows, self.num_words.data.inner.len());
        assert_eq!(num_rows, self.points.data.inner.len());
        assert_eq!(num_rows, self.date.data.inner.len());
    }
}

#[component]
fn SeoberlsikList() -> Element {

    let nav = use_navigator();

    let mut config = use_context::<Signal<utils::UserConfig>>();

    let mut db_refresh_token = use_signal(|| 0);

    let db_a = consume_context::<platform::DataFetch>();
    let db_b = consume_context::<platform::DataFetch>();
    let db_c = consume_context::<platform::DataFetch>();
    let from_db: Resource<Result<_, platform::DataFetchError>> = use_resource(move || {
        let _ = db_refresh_token();

        let db = db_a.clone();
        async move {
            let summaries = db.get_all_practice_result_summaries(config()).await?;

            let mut title = vec![];
            let mut num_w = vec![];
            let mut points = vec![];
            let mut date = vec![];
            for summary in summaries {
                title.push((summary.title, summary.id));
                num_w.push(summary.num_words);
                points.push((summary.points, summary.id));
                date.push(summary.date);
            }

            Ok((title, num_w, points, date))
        }
    });

    let data: Memo<Option<Result<_,_>>> = use_memo(move || match &*from_db.read() {
        None => None,
        Some(Err(e)) => Some(Err(format!("{e}"))),
        Some(Ok((title, num_w, points, date))) => Some(Ok(GridData {
            title: Column {
                decl: ColumnDecl {
                    name: "Title".to_string(),
                    sort: 0,
                    align: HorizontalAlign::Left,
                    width: 30,
                },
                data: ColumnData {
                    inner: title.clone(),
                    render: |(title, id)| rsx! { Link {
                        to: Route::SeoberlsikPractice { id: *id },
                        class: "grid-cell-custom-title",
                        "{title}"
                        // span { class: "material-symbols-outlined", "backspace" } TODO
                    }}
                },
            },

            num_words: Column {
                decl: ColumnDecl {
                    name: "len".to_string(),
                    sort: 0,
                    align: HorizontalAlign::Right,
                    width: 3,
                },
                data: ColumnData {
                    inner: num_w.clone(),
                    render: |n| rsx! {
                        "{n}"
                    },
                }
            },

            points: Column {
                decl: ColumnDecl {
                    name: "points".to_string(),
                    sort: 0,
                    align: HorizontalAlign::Center,
                    width: 10,
                },
                data: ColumnData {
                    inner: points.clone(),
                    render: |(p, id)| rsx! { if let Some(p) = p {{
                        let coef = utils::progress_coef(*p);
                        let (level, c) = utils::progress_bar(coef, 5);
                        rsx! { Link {
                            to: Route::PracticeResult { id: *id },
                            class: "grid-cell-custom-points",
                            title: "{p}",
                            div {
                                class: "pointbar-level{level}",
                                div {
                                    class: "pointbar-level{level+1}",
                                    style: "--bar-percentage: {(c * 100.0) as u32}%",
                                }
                            }
                        }}
                    }}},
                },
            },

            date: Column {
                decl: ColumnDecl {
                    name: "date".to_string(),
                    sort: 0,
                    align: HorizontalAlign::Left,
                    width: 16,
                },
                data: ColumnData {
                    inner: date.clone(),
                    render: |d| rsx! {
                        if let Some(d) = d {{
                            format!("{}", d.format("%Y-%m-%d %H:%M"))
                        }}
                    },
                },
            },
        }))
    });

    const DEL_ICONS: [&str; 5] = ["delete", "heart_broken", "delete_sweep", "contract_delete", "delete_forever"];
    let mut del_confirm = use_signal(|| [false; DEL_ICONS.len()]);

    let confirm_level = del_confirm.read().iter().filter(|b|**b).count();

    let allow_del = config().allow_del;
    let word_time = config().word_time;

    let ret = match &*data.read() {
        None => rsx ! {},
        Some(Err(err)) => {
            nav.push(Route::ErrorPage { errmsg: err.to_string() });
            rsx! {}
        }
        Some(Ok(data)) => rsx! {
            div {
                class: "menubar",

                button {
                    class: if allow_del { "allow-del" } else { "disallow-del" },
                    title: if allow_del { "backspace enabled" } else { "backspace disabled" },
                    onclick: move |_| {
                        let db = db_b.clone();
                        async move {
                            config.write().allow_del = !allow_del;
                            if let Err(err) = db.put_userconfig(config()).await {
                                nav.push(Route::ErrorPage { errmsg: format!("{err}") });
                            }
                        }
                    },
                    "backspace"
                }

                button {
                    class: if word_time { "allow-del" } else { "disallow-del" },
                    title: if word_time { "ignore interval time" } else { "measure whole time" },
                    onclick: move |_| {
                        let db = db_c.clone();
                        async move {
                            config.write().word_time = !word_time;
                            if let Err(err) = db.put_userconfig(config()).await {
                                nav.push(Route::ErrorPage { errmsg: format!("{err}") });
                            }
                        }
                    },
                    "avg_pace"
                }

                for (i, icon) in DEL_ICONS.iter().enumerate() {
                    button {
                        style: "--shake-delay: {(i*6182)%100}ms",
                        class: if del_confirm.read()[i] { "frightened-icon{confirm_level}" } else { "frightened-icon0" },
                        title: "clear all progress {i+1}",
                        onclick: move |_| {
                            del_confirm.write()[i] ^= true;
                            async move {
                                if del_confirm.read().iter().all(|b|*b) {
                                    let db = consume_context::<platform::DataFetch>();
                                    if let Err(err) = db.clear_practice_history(config()).await {
                                        nav.push(Route::ErrorPage { errmsg: format!("{err}") });
                                    }
                                    del_confirm.write().iter_mut().for_each(|b| *b = false);
                                    db_refresh_token += 1;
                                }
                            }
                        },
                        "{icon}"
                    }
                }
            }
            DataGrid { data: data.clone(), }
        }
    };

    return ret;
}

#[component]
fn DataGrid(data: GridData) -> Element {
    data.verify();

    let column_widths: String = 
        (0 .. data.num_cols()).map(|col_idx|
            format!("{}ch ", data.get_decl(col_idx).width + 2)
        ).collect();

    let mut scroll_y = use_context::<Signal<f64>>();

    rsx! {
        div {
            class: "grid-shell",
            role: "table",
            "data-density": "comfortable",
            style: "--column-widths: {column_widths}",

            div {
                class: "grid-scroll",

                onscroll: move |e| {
                    let y = e.data().scroll_top();
                    scroll_y.set(y);
                },

                onmounted: move |e| {
                    spawn(async move {
                        _ = e.data().scroll(
                            euclid::Vector2D::new(0.0, scroll_y()),
                            ScrollBehavior::Instant,
                        ).await;
                    });
                },

                class: "markdown-mode",
                div {
                    class: "grid-top",

                    div {
                        class: "grid-header",
                        role: "row",

                        div  {
                            class: "grid-gutter",
                        }

                        div {
                            class: "grid-content",

                            for col_idx in 0 .. data.num_cols() {{
                                let column = data.get_decl(col_idx);
                                rsx! {
                                    div {
                                        class: "grid-header-cell",
                                        class: if column.align == HorizontalAlign::Left     { "text-left" },
                                        class: if column.align == HorizontalAlign::Center   { "text-center" },
                                        class: if column.align == HorizontalAlign::Right    { "text-right" },
                                        
                                        "{column.name}"
                                        if column.sort > 0 {" ↑"}
                                        if column.sort < 0 {" ↓"}
                                    }
                                }
                            }}
                        }
                    }

                    div {
                        class: "grid-divider",
                        "aria-hidden": "true",

                        div {
                            class: "grid-gutter",
                        }
                        div {
                            class: "grid-content",

                            for col_idx in 0 .. data.num_cols() {{
                                let column = data.get_decl(col_idx);
                                rsx! {
                                    div {
                                        class: "grid-divider-cell",
                                        class: "grid-divider-line",
                                        {"-".repeat(column.width)}
                                    }
                                }
                            }}
                        }
                    }
                }
            
                for row_idx in 0 .. data.num_rows() {
                    div {
                        class: "grid-row",

                        div {
                            class: "grid-gutter",
                            "{row_idx+1}"
                        }

                        div {
                            class: "grid-content",

                            for col_idx in 0 .. data.num_cols() {{
                                let elem = data.get_render(col_idx, row_idx);
                                let column = data.get_decl(col_idx);
                                rsx! {
                                    div {
                                        class: "grid-cell",
                                        class: if column.align == HorizontalAlign::Left     { "text-left" },
                                        class: if column.align == HorizontalAlign::Center   { "text-center" },
                                        class: if column.align == HorizontalAlign::Right    { "text-right" },
                                        {elem}
                                    }
                                }
                            }}
                        }
                    }
                }
            }
        }
    }
}


#[derive(Clone, PartialEq, Props)]
struct WordViewerProps {
    prev: Option<String>,
    next: Option<String>,
    current: Option<String>,
    prev_answer: String,
    prev_speed: u32,

    onsubmit: EventHandler<String>,
    oninput: EventHandler,
    onreset: EventHandler,
}

// use tokio::time::{sleep, Duration};
use platform::time::{Instant, Duration};
use platform::sleep_future;

#[component]
fn SeoberlsikPractice(id: u32) -> Element {
    // let mut elapsed = use_signal(|| 0);
    let mut prev_answer = use_signal(|| "".to_string());
    let mut word_idx = use_signal(|| 0usize);
    let mut typing_count = use_signal(|| 0u32);
    let mut wrong_count = use_signal(|| 0u32);
    let mut prev_speed = use_signal(|| 0);

    let mut start_time: Signal<Option<Instant>> = use_signal(|| None);
    let mut cur_acc_time = use_signal(|| Duration::from_secs(0));
    let mut acc_time = use_signal(|| Duration::from_secs(0));

    let config = use_context::<Signal<utils::UserConfig>>();

    // timer spwaner
    // use_effect is rerun when rerender.
    // this hook does not depend on other dependencies, so dioxus will skip it.
    // letting it run once when the component mounts
    use_effect(move || {
        spawn(async move {
            loop {
                if let Some(start) = &*start_time.peek() {
                    cur_acc_time.set(start.elapsed());
                }

                sleep_future(Duration::from_millis(200)).await;
            }
        });
    });

    let db = consume_context::<platform::DataFetch>();
    // this too will be called only once
    let from_db: Resource<Result<_, platform::DataFetchError>> = use_resource(move || {
        let db = db.clone();
        async move {
            let (title, content, num_words) = db.get_practice_content(id).await?;
            let words = content.split_whitespace().map(|s| s.into()).collect::<Vec<String>>();
            Ok((title, words, num_words))
        }
    });

    let mut words_ord_seed = use_signal(rand::random);

    let words_ord = use_memo(move ||
        if let Some(Ok((_, words, num_words))) = &*from_db.read() {
            let mut rng = rand::rngs::SmallRng::seed_from_u64(words_ord_seed());
            let mut words_ord = vec![];
            while words_ord.len() < *num_words {
                words_ord.extend(0 .. words.len());
            }
            words_ord.shuffle(&mut rng);
            words_ord.truncate(*num_words);
            words_ord
        } else {
            vec![]
        }
    );

    let nav = use_navigator();

    let onreset = move || {
        prev_answer.set("".to_string());
        word_idx.set(0);
        typing_count.set(0);
        wrong_count.set(0);
        start_time.set(None);
        cur_acc_time.set(Duration::from_secs(0));
        acc_time.set(Duration::from_secs(0));
        prev_speed.set(0);
        document::eval(utils::SCRIPT_CLEAR_INPUT_CONTENT);

        words_ord_seed += 1;
    };

    let oninput = move || {
        if start_time().is_none() {
            start_time.set(Some(Instant::now()));
            // for some reason, on web version, when you press space to go to next practice on result page,
            // spacebar character is inserted into the input box.
            // this will ensure starting typing for a word with empty input box.
            document::eval(utils::SCRIPT_CLEAR_INPUT_CONTENT);
        } // un-pause timer
    };

    let status = utils::Status {
        wrong: wrong_count(),
        finished: word_idx() as u32,
        millis: (acc_time() + cur_acc_time()).as_millis(),
        time_active: start_time().is_some(),
        typed: typing_count(),
        points: 0,
    };

    rsx! {
        div {
            class: "package",
            onclick: |_| { document::eval(utils::SCRIPT_FIX_INPUT_CURSOR_END); },

            Toolbar { id, onreset },

            div {
                class: "practice-title",
                span {
                    class: "practice-title-inner",
                    if let Some(Ok((title, _, _))) = &*from_db.read() {
                        "{title}",
                    }
                    span { class: "material-symbols-outlined", class: if config().allow_del {"allow-del"} else {"disallow-del"}, "backspace" }
                }
            }

            StatusLine { status: status },

            { match &*from_db.read() {
                None => rsx! {},
                Some(Err(err)) => {
                    nav.push(Route::ErrorPage { errmsg: format!("{err}") });
                    rsx! {}
                }

                Some(Ok((_, words, _))) => {
                    let words_ord = words_ord.read();
                    let num_words = words_ord.len();

                    let idx = word_idx();
                    // cannot use words in onsubmit callback, so we prepare here 
                    let current = if idx < num_words { Some(words[words_ord[idx]].clone()) } else { None };
                    rsx! {
                        WordsViewer { 
                            prev: if idx > 0 { Some(words[words_ord[idx-1]].clone()) } else { None },
                            next: if idx + 1 < num_words { Some(words[words_ord[idx+1]].clone()) } else { None },
                            current: current.clone(),
                            prev_answer: prev_answer.read(),
                            prev_speed: prev_speed(),

                            onsubmit: move |s: String| {
                                if let Some(current) = current.as_ref() {
                                    let (left, common, right) = utils::tasu_compare(current.as_str(), s.as_str());
                                    let wrong = left.max(right);
                                    let cur_typed = common + right;
                                    *wrong_count.write() += wrong;
                                    *typing_count.write() += cur_typed;
                                    // Note for later: wpm = 5 * cpm

                                    word_idx.set(idx + 1);
                                    prev_answer.set(s);

                                    acc_time += cur_acc_time();
                                    prev_speed.set((cur_typed as f32 / cur_acc_time().as_millis() as f32 * 60_000.0) as u32);
                                    cur_acc_time.set(Duration::from_secs(0));

                                    if config().word_time {
                                        start_time.set(None); // pause timer
                                    } else {
                                        start_time.set(Some(Instant::now())); // pause timer
                                    }
                                }

                                async move {
                                    if idx == num_words - 1 {
                                        let mut status = utils::Status {
                                            wrong: wrong_count(),
                                            finished: word_idx() as u32,
                                            millis: (acc_time() + cur_acc_time()).as_millis(),
                                            time_active: start_time().is_some(),
                                            typed: typing_count(),
                                            points: 0,
                                        };
                                        status.set_points();

                                        let db = consume_context::<platform::DataFetch>();
                                        if let Err(err) = db.put_practice_result(id, config(), status).await {
                                            nav.push(Route::ErrorPage { errmsg: format!("{err}") });
                                        } else {
                                            nav.push(Route::PracticeResult { id });
                                        }
                                    }
                                }
                            },

                            oninput, onreset,
                        }
                    }
                }
            }}
        }
    }
}

#[component]
fn Toolbar(id: u32, onreset: EventHandler) -> Element {
    rsx! {
        div { class: "toolbar",
            Link { class: "material-symbols-outlined toolbar-list", to: Route::SeoberlsikList {}, "list" }
            // span { class: "material-symbols-outlined toolbar-back", onclick: move |_| {nav.push(Route::SeoberlsikPractice { id: id-1, allow_del });}, "arrow_back" }
            span { class: "material-symbols-outlined toolbar-restart", onclick: move |_| onreset.call(()), "refresh" }
            // Link { class: "material-symbols-outlined toolbar-next", to: Route::SeoberlsikPractice { id: id+1, allow_del }, "arrow_forward" }
        }
    }
}

#[component]
fn WordsViewer(props: WordViewerProps) -> Element {
    let mut input = use_signal(|| "".to_string());
    let config = use_context::<Signal<utils::UserConfig>>();

    let nav = use_navigator();

    let is_prev_wrong = props.prev.as_ref() != Some(&props.prev_answer);

    rsx! {
        div {
            id: "wai",
            class: "words-viewer",

            div { class: "word-and-input prev-word",
                class: if is_prev_wrong {
                    "wrong"
                },

                span {
                    class: "word_speed",
                    if props.prev_speed > 0 { "{props.prev_speed}" } else { "" }
                }
                span { class: "given",
                    {props.prev}
                }
                span { class: "answer",
                    {props.prev_answer}
                }
            }

            div { class: "word-and-input current",
                span { class: "given",
                    {props.current.unwrap_or("🔚".to_string())} // this placeholder will be used only if transition to next page is too slow
                }

                input { class: "answer",
                    id: "input",
                    autofocus: true,
                    autocomplete: "off",
                    // input's state is auto managed by the DOM for IME handling
                    // this will keep the mid-composition letters unerased.
                    //value: input,

                    // having this higher in the component hierarchy (e.g. .package) does not work.
                    // getElementById simply returns null;
                    onmounted: |_| {
                        document::eval(utils::SCRIPT_FIX_INPUT_CURSOR_END);
                    },

                    oninput: move |e| {
                        input.set(e.value());
                    },

                    onkeydown: move |e| {

                        let mut submit = || {
                            // oninput must be called `before` `onsubmit`
                            // to prevent overwriting start_timer set to None by onsubmit
                            props.oninput.call(()); 

                            if ! input().is_empty() {
                                props.onsubmit.call(input());
                                input.set("".to_string());
                                document::eval(utils::SCRIPT_CLEAR_INPUT_CONTENT);
                            }
                            e.prevent_default();
                        };

                        match e.code() {
                            // On backspace, we can't prevent IME's handling for it. So we just submit current (probably incorrect value)
                            Code::Backspace if !config().allow_del => submit(),

                            // ignore keys in mid-composition, especially backspace/enter
                            _ if e.key() == Key::Process => {
                                props.oninput.call(());
                            }

                            Code::ArrowLeft |
                            Code::ArrowRight |
                            Code::ArrowUp |
                            Code::ArrowDown |
                            Code::Home |
                            Code::End |
                            Code::PageUp |
                            Code::PageDown => {
                                e.prevent_default();
                                // ignore
                            }

                            Code::Escape => {
                                nav.push(Route::SeoberlsikList {});
                            }

                            Code::Space | Code::Enter if e.key() != Key::Process => submit(),

                            Code::F5 => {
                                input.set("".to_string());
                                // document::eval(utils::SCRIPT_CLEAR_INPUT_CONTENT); // done in onreset
                                props.onreset.call(());
                                e.prevent_default();
                                e.stop_propagation();
                            }

                            _ => props.oninput.call(()),
                        }
                    },
                }
            }

            div { class: "word-and-input next-word",
                span { class: "given",
                    {props.next}
                }
            }
        }
    }
}

#[component]
fn StatusLine(status: utils::Status) -> Element {
    let accuracy = (status.accuracy() * 100.0) as u32;
    let speed = status.speed() as u32;

    rsx! {
        div {
            class: "status",

            div { class: "status-accuracy",
                "정확도 "
                span {
                    // id: "accuracy",
                    "{accuracy}%"
                }
            }

            div { class: "status-wrong",
                "오타 "
                span {
                    // id: "wrong",
                    "{status.wrong}/{status.finished}"
                }
            }

            div { class: "status-time",
                class: if ! status.time_active { "paused" },
                "시간 "
                span {{ // id: "time",
                    let decs = (status.millis % 1000) / 10;
                    let secs = status.millis / 1000;
                    let time_hrs = secs / 3600;
                    let time_min = secs / 60 % 60;
                    let time_sec = secs % 60;

                    if secs >= 3600 { format!("{time_hrs}:{time_min:02}:{time_sec:02}") }
                    else if secs >= 60 { format!("{time_min}:{time_sec:02}") }
                    else { format!("{time_sec}.{decs:02}") }
                }}
            }

            div { class: "status-speed",
                span { // id: speed
                    "{speed}"
                }
                " 타/분"
            }
        }
    }
}

#[component]
fn PracticeResult(id: u32) -> Element {
    let default_status = utils::Status {
        wrong: 0,
        finished: 0,
        millis: 0,
        time_active: false,
        typed: 0,
        points: 0,
    };

    let config = use_context::<Signal<utils::UserConfig>>();

    let nav = use_navigator();

    let o_status = use_resource(move || {
        let db = consume_context::<platform::DataFetch>();
        async move {
            db.get_best_practice_result(id, config()).await
        }
    });

    return rsx! {
        div { class: "package",

            tabindex: 0, // to make focusable

            onmounted: move |e| {
                spawn(async move {
                    _ = e.set_focus(true).await;
                });
            },

            onkeydown: move |e: Event<KeyboardData>| {
                match e.code() {
                    Code::Escape => {
                        nav.push(Route::SeoberlsikList {});
                    }
                    Code::Backspace => {
                        nav.push(Route::SeoberlsikPractice { id });
                    }
                    Code::Space => {
                        nav.push(Route::SeoberlsikPractice { id: id+1 });
                    }
                    _ => (),
                }
            },

            if let Some(o_status) = &*o_status.read() {
                // async loaded
                match o_status {
                    Ok(o_status) => {
                        // db query success
                        let mut status = o_status.unwrap_or(default_status); // in case no record
                        status.time_active = true;
                        rsx! {
                            StatusLine { status }
                            ResultViewer { id, status }
                        }
                    }
                    Err(err) => {
                        nav.push(Route::ErrorPage { errmsg: format!("{err}") });
                        rsx! {}
                    }
                }
            } // show nothing when not loaded
        }
    }
}

#[component]
fn ResultViewer(id: u32, status: utils::Status) -> Element {
    const NUM_BARS: usize = 5;
    let mut widths = [0; NUM_BARS];

    let coef = utils::progress_coef(status.points);
    let (last_bar, c) = utils::progress_bar(coef, NUM_BARS);
    for w in widths.iter_mut().take(last_bar.min(NUM_BARS)) {
        *w = 100;
    }
    if last_bar < NUM_BARS {
        widths[last_bar] = (100.0 * c) as u32;
    }

    let mut apply_width = use_signal(|| false);

    use_effect(move || {
        spawn(async move {
            sleep_future(Duration::from_millis(200)).await;
            apply_width.set(true);
        });
    });

    rsx! {
        div { class: "result-viewer",
            div { class: "points",
                "{status.speed() as u32} * {status.accuracy_coef():.2} = {status.points}"
            }
            div { class: "pointbar",
                for  i in 0 .. NUM_BARS {
                    div {
                        class: "pointbar-fill pointbar-level{i+1}",
                        class: if i == last_bar { "pointbar-last" },
                        style: if apply_width() {"width: {widths[i]}%"}
                    }
                }
            }
            div { class: "actions",
                Link { class: "action-list material-symbols-outlined", to: Route::SeoberlsikList {}, "list" }
                Link { class: "action-back material-symbols-outlined", to: Route::SeoberlsikPractice { id: id-1 }, "arrow_back" } // TODO conditionally disable?
                Link { class: "action-redo material-symbols-outlined", to: Route::SeoberlsikPractice { id }, "refresh" }
                Link { class: "action-next material-symbols-outlined", to: Route::SeoberlsikPractice { id: id+1 }, "arrow_forward" }
                // span { class: "action-next material-symbols-outlined", onclick: move |_| {
                //     apply_width.toggle();
                // },
                // "arrow_shape_up_stack"}
            }
        }
    }
}

#[component]
fn ErrorPage(errmsg: String) -> Element {
    rsx! {
        div {
            h1 { "Error!" }
            p { "{errmsg}" }
        }
    }
}