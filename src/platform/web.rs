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

    use crate::utils::{Status, ResultSummary, UserConfig, PracticeHistoryRecord, PracticeSets};
    type Result<T> = std::result::Result<T, Error>;
    use indexed_db_futures::prelude::*;
    use indexed_db_futures::{database::Database, transaction::TransactionMode, BuildSerde, KeyPath};

    #[derive(Clone)]
    pub struct DB {
        idb: Database,
    }

    #[derive(Debug, thiserror::Error)]
    pub enum Error {
        #[error("{0}")] Ode (#[from] indexed_db_futures::error::OpenDbError),
        #[error("{0}")] E   (#[from] indexed_db_futures::error::Error),
        #[error("{0}")] Json(#[from] serde_json::Error),
        #[error("{0}")] Str(String),
    }

    impl From<String> for Error { fn from(value: String) -> Self { Error::Str(value) } }

    // since app.db is only 84kb, it's reasonable to just include_bytes!("practice.json")
    // desktop version will still use db though.
    // use indexed db for userdata
    impl DB {
        pub async fn open() -> Result<Self> {
            let idb = Database::open("db")
                .with_version(1u8)
                .with_on_upgrade_needed(|_event, db| {
                    if db.object_store_names().find(|s| s == "history").is_none() {
                        db.create_object_store("history").build()?;
                    }

                    if db.object_store_names().find(|s| s == "user_config").is_none() {
                        db.create_object_store("user_config").build()?;
                    }
                    Ok(())
                })
                .build().unwrap()
                .await?;

            Ok(Self { idb })
        }

        fn histkey(id: u32, config: &UserConfig) -> String {
            format!("{}-{id}-{}{}",
                config.layout,
                if config.allow_del {1} else {0},
                if config.word_time {1} else {0},
            )
        }

        pub async fn put_practice_result(&self, id: u32, config: UserConfig, status: Status) -> Result<bool> {

            let now = super::time::UNIX_EPOCH
                .elapsed()
                .map(|d| d.as_secs() as i32)
                .unwrap_or_else(|e| -(e.duration().as_secs() as i32));

            let record = PracticeHistoryRecord::from_status(id, now, &status);

            let key = Self::histkey(id, &config);
            let tx = self.idb.transaction("history").with_mode(TransactionMode::Readwrite).build()?;
            let store = tx.object_store("history")?;

            let best_record: Option<PracticeHistoryRecord> = store.get(&key).serde()?.await?;

            let should_update = match best_record {
                Some(rec) => rec.points < record.points,
                None => true,
            };

            if should_update {
                store.put(&record).with_key(key).serde()?.await?;
            }

            tx.commit().await?;

            Ok(should_update)
        }

        pub async fn get_best_practice_result(&self, id: u32, config: UserConfig) -> Result<Option<Status>> {
            let key = Self::histkey(id, &config);
            let tx = self.idb.transaction("history").with_mode(TransactionMode::Readonly).build()?;
            let store = tx.object_store("history")?;

            let record: Option<PracticeHistoryRecord> = store.get(key).serde()?.await?;
            tx.commit().await?;

            Ok(record.as_ref().map(PracticeHistoryRecord::to_status))
        }

        pub async fn get_all_practice_result_summaries(&self, practice_sets: &PracticeSets, config: UserConfig) -> Result<Vec<ResultSummary>> {
            let tx = self.idb.transaction("history").with_mode(TransactionMode::Readonly).build()?;
            let store = tx.object_store("history")?;

            let mut ret = vec![];
            for (practice, id) in practice_sets.sets[config.layout as usize].iter().zip(0u32..) {
                let key = Self::histkey(id, &config);
                let record: Option<PracticeHistoryRecord> = store.get(key).serde()?.await?;
                let points = record.as_ref().map(|r| r.points);
                let date = record.map(|r| r.created_at)
                    .and_then(|date| chrono::DateTime::from_timestamp_secs(date as i64))
                    .map(|date| date.with_timezone(&chrono::Local));
                let title = practice.title.clone();
                let num_words = practice.num;
                ret.push(ResultSummary { id, title, num_words, points, date });
            }

            tx.commit().await?;
            Ok(ret)
        }

        // note that unlike desktop version, this will clear history for *ALL* practices, regardless of allowdel, wordtime and layout
        pub async fn clear_practice_history(&self, config: UserConfig) -> Result<()> {
            let tx = self.idb.transaction("history").with_mode(TransactionMode::Readonly).build()?;
            let store = tx.object_store("history")?;
            store.clear()?;
            tx.commit().await?;
            Ok(())
        }

        pub async fn get_userconfig(&self) -> Result<Option<UserConfig>> {
            let store_name = "user_config";
            let tx = self.idb.transaction("history").with_mode(TransactionMode::Readonly).build()?;
            let store = tx.object_store("history")?;

            let record: Option<UserConfig> = store.get(1).serde()?.await?;
            tx.commit().await?;
            Ok(record)
        }

        pub async fn put_userconfig(&self, config: UserConfig) -> Result<()> {
            let store_name = "user_config";
            let tx = self.idb.transaction("history").with_mode(TransactionMode::Readwrite).build()?;
            let store = tx.object_store("history")?;

            store.put(&config).with_key(1).serde()?.await?;

            tx.commit().await;

            Ok(())
        }
    }
}