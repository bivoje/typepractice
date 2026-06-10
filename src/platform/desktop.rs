use dioxus_desktop::{Config, WindowBuilder, LogicalSize};
use dioxus::LaunchBuilder;
use dioxus::prelude::{desktop, Asset};

pub fn launch_builder() -> LaunchBuilder {
    dioxus::LaunchBuilder::new()
    .with_cfg(desktop! {
        Config::new()
        .with_menu(None)
        .with_window(
            WindowBuilder::new()
            .with_title("typepractice")
            .with_inner_size(LogicalSize::new(900, 600))
            .with_min_inner_size(LogicalSize::new(900, 600))
            // don't know why but min_inner_size.height being 20px smaller makes it correct fit
        )
    })
}

pub async fn sleep_future(delay_ms: time::Duration) {
    tokio::time::sleep(delay_ms).await
}

pub use std::time as time;

pub type DataFetch = db::Database;
pub type DataFetchError = db::Error;


mod db {
use std::sync::{Arc, Mutex};
    type Result<T> = std::result::Result<T, Error>;
    use crate::utils::{Status, PracticeHistoryRecord, ResultSummary, UserConfig, KeyboardLayout, PracticeSets, Practice};
    use std::collections::HashMap;

    #[derive(Clone)]
    pub struct Database(Arc<Mutex<Inner>>);
    type HistKey = (u32, bool, bool, KeyboardLayout);
    struct Inner {
        config_cache: Option<UserConfig>,
        hist_cache: HashMap<HistKey, PracticeHistoryRecord>,
    }

    #[derive(Debug, thiserror::Error)]
    pub enum Error {
        #[error("{0}")] IO  (#[from] std::io::Error),
        #[error("{0}")] Json(#[from] serde_json::Error),
        #[error("{0}")] Str (String),
    }

    impl From<String> for Error { fn from(value: String) -> Self { Error::Str(value) } }

    use std::fs::File;
    use std::io::Write;
    use std::path::PathBuf;

    impl Inner {
        fn paths() -> Result<(PathBuf, PathBuf)> {
            let app_dir = if let Some(data_dir) = dirs::data_dir() {
                data_dir.join("typepractice")
            } else { std::path::Path::new(".").to_path_buf() };
            std::fs::create_dir_all(&app_dir)?;

            let config_path = app_dir.join("config.json");
            let hist_path = app_dir.join("best_scores.json");

            Ok((config_path, hist_path))
        }

        fn histkey(id: u32, config: &UserConfig) -> HistKey {
            (id, config.allow_del, config.word_time, config.layout)
        }

        fn open() -> Result<Self> {
            let (config_path, hist_path) = Self::paths()?;

            let config_cache = if config_path.exists() {
                let file = File::open(config_path)?;
                Some(serde_json::from_reader(file)?)
            } else { None };

            let hist_cache = if hist_path.exists() {
                let file = File::open(hist_path)?;
                let hist_vec: Vec<_> = serde_json::from_reader(file)?;
                hist_vec.into_iter().collect()
            } else { HashMap::new() };

            Ok(Self { config_cache, hist_cache })
        }

        fn put_result(&mut self, id: u32, config: UserConfig, time: i32, status: Status) -> Result<bool> {
            let key = Self::histkey(id, &config);
            let val = PracticeHistoryRecord::from_status(id, time, &status);
            use std::collections::hash_map::Entry::*;
            let has_updated = match self.hist_cache.entry(key) {
                Vacant(e) => {
                    e.insert(val);
                    true
                }
                Occupied(mut e) if e.get().points < status.points => {
                    e.insert(val);
                    true
                }
                _ => false,
            };
            Ok(has_updated)
        }

        fn get_result(&self, id: u32, config: UserConfig) -> Result<Option<Status>> {
            let key = Self::histkey(id, &config);
            Ok(self.hist_cache.get(&key).map(PracticeHistoryRecord::to_status))
        }

        pub fn get_result_summaries(&self, practice_sets: &PracticeSets, config: UserConfig) -> Result<Vec<ResultSummary>> {
            Ok(practice_sets.sets[config.layout as usize].iter().zip(0u32..).map(|(practice, id)|
                ResultSummary {
                    id,
                    title: practice.title.clone(),
                    num_words: practice.num,
                    points: self.hist_cache.get(&Self::histkey(id, &config))
                        .map(|s| s.points),
                    date: self.hist_cache.get(&Self::histkey(id, &config))
                        .and_then(|s| chrono::DateTime::from_timestamp_secs(s.created_at as i64))
                        .map(|date| date.with_timezone(&chrono::Local)),
                }
            ).collect())
        }

        pub fn clear_hist(&mut self, config: UserConfig) -> Result<()> {
            self.hist_cache.retain(|key, _v| {
                let is_target = key.1 == config.allow_del && key.2 == config.word_time && key.3 == config.layout;
                ! is_target // leave only if not clearing target
            });
            Ok(())
        }

        pub fn del_hist(&mut self, id: u32, config: UserConfig) -> Result<Option<Status>> {
            let key = Self::histkey(id, &config);
            Ok(self.hist_cache.remove(&key).as_ref().map(PracticeHistoryRecord::to_status))
        }

        pub fn get_userconfig(&self) -> Result<Option<UserConfig>> {
            Ok(self.config_cache.clone())
        }

        pub fn put_userconfig(&mut self, config: UserConfig) -> Result<()> {
            self.config_cache = Some(config);
            Ok(())
        }

        fn commit(&self) -> Result<()> {
            let (config_path, hist_path) = Self::paths()?;

            if let Some(config_cache) = &self.config_cache {
                let dump = serde_json::to_string_pretty(config_cache)?;
                let mut file = File::create(config_path)?;
                file.write_all(dump.as_bytes())?;
            }

            let hist_vec: Vec<_> = self.hist_cache.iter().collect();
            let dump = serde_json::to_string_pretty(&hist_vec)?;
            let mut file = File::create(hist_path)?;
            file.write_all(dump.as_bytes())?;

            Ok(())
        }
    }

    impl Database {
        pub async fn open() -> Result<Self> {
            Ok(Database(Arc::new(Mutex::new(Inner::open()?))))
        }

        pub async fn put_practice_result(&self, id: u32, config: UserConfig, status: Status) -> Result<bool> {
            let mut inner = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            let now = match super::time::UNIX_EPOCH.elapsed() {
                Ok(after) => after.as_secs() as i32,
                Err(before) => - (before.duration().as_secs() as i32),
            };

            let has_updated = inner.put_result(id, config, now, status)?;
            inner.commit();
            Ok(has_updated)
        }

        pub async fn get_best_practice_result(&self, id: u32, config: UserConfig) -> Result<Option<Status>> {
            let inner = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            inner.get_result(id, config)
        }

        pub async fn get_all_practice_result_summaries(&self, practice_sets: &PracticeSets, config: UserConfig) -> Result<Vec<ResultSummary>> {
            let inner = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            inner.get_result_summaries(practice_sets, config)
        }

        pub async fn clear_practice_history(&self, config: UserConfig) -> Result<()> {
            let mut inner = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            inner.clear_hist(config)?;
            inner.commit()
        }

        pub async fn delete_practice_history(&self, id: u32, config: UserConfig) -> Result<Option<Status>> {
            let mut inner = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            let ret = inner.del_hist(id, config)?;
            inner.commit()?;
            Ok(ret)
        }

        pub async fn get_userconfig(&self) -> Result<Option<UserConfig>> {
            let inner = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            inner.get_userconfig()
        }

        pub async fn put_userconfig(&self, config: UserConfig) -> Result<()> {
            let mut inner = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            inner.put_userconfig(config)?;
            inner.commit()
        }

        pub async fn commit(&self) -> Result<()> {
            let mut inner = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            inner.commit()
        }
    }
}