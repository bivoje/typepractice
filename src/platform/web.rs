use dioxus::LaunchBuilder;

pub fn launch_builder() -> LaunchBuilder {
    dioxus::LaunchBuilder::new()
}

pub async fn sleep_future(duration: time::Duration) {
    gloo_timers::future::TimeoutFuture::new(duration.as_millis() as u32).await
}

pub use web_time as time;

pub type DataFetch = db::DB;
pub type DataFetchError = db::Error;

mod db {

    use crate::utils::{Status, ResultSummary, UserConfig};
    type Result<T> = std::result::Result<T, Error>;
    use indexed_db_futures::prelude::*;
    use indexed_db_futures::{database::Database, transaction::TransactionMode, BuildSerde, KeyPath};

    #[derive(Clone)]
    pub struct DB {
        idb: Database,
        content: Vec<(u32, String, String, u32)>, // (id, title, words, num_words); must be sorted asc by id
    }

    #[derive(Debug, thiserror::Error)]
    pub enum Error {
        #[error("{0}")] Ode (#[from] indexed_db_futures::error::OpenDbError),
        #[error("{0}")] E   (#[from] indexed_db_futures::error::Error),
        #[error("{0}")] Json(#[from] serde_json::Error),
        #[error("{0}")] Str(String),
    }

    impl From<String> for Error { fn from(value: String) -> Self { Error::Str(value) } }

    #[derive(Clone, Debug, serde::Serialize, serde::Deserialize)]
    struct PracticeHistoryRecord {
        pub practice_id: u32,
        pub created_at: i32,
        pub wrong_cnt: u32,
        pub word_cnt: u32,
        pub millis: u128,
        pub typing_cnt: u32,
        pub points: u32,
    }

    // since app.db is only 84kb, it's reasonable to just include_bytes!("practice.json")
    // desktop version will still use db though.
    // use indexed db for userdata
    impl DB {
        pub async fn open() -> Result<Self> {
            let idb = Database::open("db")
                .with_version(1u8)
                .with_on_upgrade_needed(|_event, db| {
                    if db.object_store_names().find(|s| s == "history_allowdel_wordtime").is_none() {
                        db.create_object_store("history_allowdel_wordtime")
                            .with_key_path(KeyPath::One("practice_id"))
                            .build()?;
                    }
                    if db.object_store_names().find(|s| s == "history_disallowdel_wordtime").is_none() {
                        db.create_object_store("history_disallowdel_wordtime")
                            .with_key_path(KeyPath::One("practice_id"))
                            .build()?;
                    }
                    if db.object_store_names().find(|s| s == "history_allowdel_wholetime").is_none() {
                        db.create_object_store("history_allowdel_wholetime")
                            .with_key_path(KeyPath::One("practice_id"))
                            .build()?;
                    }
                    if db.object_store_names().find(|s| s == "history_disallowdel_wholetime").is_none() {
                        db.create_object_store("history_disallowdel_wholetime")
                            .with_key_path(KeyPath::One("practice_id"))
                            .build()?;
                    }

                    if db.object_store_names().find(|s| s == "user_config").is_none() {
                        db.create_object_store("user_config")
                            .build()?;
                    }
                    Ok(())
                })
                .build().unwrap()
                .await?;

            let content = serde_json::from_slice(&include_bytes!("../../assets/appdb.json")[..])?;

            Ok(Self { idb, content })
        }

        fn storename(config: UserConfig) -> &'static str {
            match (config.allow_del, config.word_time) {
                ( true,  true) => "history_allowdel_wordtime",
                (false,  true) => "history_disallowdel_wordtime",
                ( true, false) => "history_allowdel_wholetime",
                (false, false) => "history_disallowdel_wholetime",
            }
        }

        pub async fn get_practice_content(&self, id: u32) -> Result<(String, String, usize)> {
            let ret = self.content.binary_search_by_key(&id, |t| t.0)
                .map(|i| {
                    let (_, title, text, num) = self.content[i].clone();
                    (title, text, num as usize)
                })
                .map_err(|_|
                    format!("no practice with id {id}")
                )?;

            Ok(ret)
        }

        pub async fn put_practice_result(&self, id: u32, config: UserConfig, status: Status) -> Result<()> {
            let now = super::time::UNIX_EPOCH
                .elapsed()
                .map(|d| d.as_secs() as i32)
                .unwrap_or_else(|e| -(e.duration().as_secs() as i32));

            let record = PracticeHistoryRecord {
                practice_id: id,
                created_at: now,
                wrong_cnt: status.wrong,
                word_cnt: status.finished,
                millis: status.millis,
                typing_cnt: status.typed,
                points: status.points,
            };

            let store_name = Self::storename(config);
            let tx = self.idb.transaction(store_name).with_mode(TransactionMode::Readwrite).build()?;
            let store = tx.object_store(store_name)?;

            let best_record: Option<PracticeHistoryRecord> = store.get(id).serde()?.await?;

            let should_update = match best_record {
                Some(rec) => rec.points < record.points,
                None => true,
            };

            if should_update {
                store.put(&record).serde()?.await?;
            }

            tx.commit().await?;

            Ok(())
        }

        pub async fn get_best_practice_result(&self, id: u32, config: UserConfig) -> Result<Option<Status>> {
            let store_name = Self::storename(config);
            let tx = self.idb.transaction(store_name).with_mode(TransactionMode::Readonly).build()?;
            let store = tx.object_store(store_name)?;

            let record: Option<PracticeHistoryRecord> = store.get(id).serde()?.await?;
            tx.commit().await?;

            Ok(record.map(|rec| Status {
                wrong: rec.wrong_cnt,
                finished: rec.word_cnt,
                millis: rec.millis,
                time_active: false,
                typed: rec.typing_cnt,
                points: rec.points,
            }))
        }

        pub async fn get_all_practice_result_summaries(&self, config: UserConfig) -> Result<Vec<ResultSummary>> {
            let store_name = Self::storename(config);
            let tx = self.idb.transaction(store_name).with_mode(TransactionMode::Readonly).build()?;
            let store = tx.object_store(store_name)?;
            
            let mut ret = vec![];
            for (id, title, _, num_words) in self.content.iter().cloned() {
                let record: Option<PracticeHistoryRecord> = store.get(id).serde()?.await?;
                let points = record.as_ref().map(|r| r.points);
                let date = record.map(|r| r.created_at)
                    .and_then(|date| chrono::DateTime::from_timestamp_secs(date as i64))
                    .map(|date| date.with_timezone(&chrono::Local));
                ret.push(ResultSummary {
                    id, title, num_words, points, date
                });
            }

            tx.commit().await?;
            Ok(ret)
        }

        pub async fn clear_practice_history(&self, config: UserConfig) -> Result<()> {
            let store_name = Self::storename(config);
            let tx = self.idb.transaction(store_name).with_mode(TransactionMode::Readonly).build()?;
            let store = tx.object_store(store_name)?;
            store.clear()?;
            tx.commit().await?;
            Ok(())
        }

        pub async fn get_userconfig(&self) -> Result<Option<UserConfig>> {
            let store_name = "user_config";
            let tx = self.idb.transaction(store_name).with_mode(TransactionMode::Readonly).build()?;
            let store = tx.object_store(store_name)?;

            let record: Option<UserConfig> = store.get(1).serde()?.await?;
            tx.commit().await?;
            Ok(record)
        }

        pub async fn put_userconfig(&self, config: UserConfig) -> Result<()> {
            let store_name = "user_config";
            let tx = self.idb.transaction(store_name).with_mode(TransactionMode::Readwrite).build()?;
            let store = tx.object_store(store_name)?;

            store.put(&config).with_key(1).serde()?.await?;

            tx.commit().await;

            Ok(())
        }
    }
}