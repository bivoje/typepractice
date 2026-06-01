use dioxus_desktop::{Config, WindowBuilder, LogicalSize};
use dioxus::LaunchBuilder;
use dioxus::prelude::desktop;

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
    const DEFAULT_DB: &[u8] = include_bytes!("../../assets/app.db");

    use std::sync::{Arc, Mutex};
    type Result<T> = std::result::Result<T, Error>;
    use crate::utils::{Status, ResultSummary, UserConfig};

    #[derive(Clone)]
    pub struct Database(Arc<Mutex<rusqlite::Connection>>);

    #[derive(Debug, thiserror::Error)]
    pub enum Error {
        #[error("{0}")] IO (#[from] std::io::Error),
        #[error("{0}")] Sql(#[from] rusqlite::Error),
        #[error("{0}")] Str(String),
    }

    impl From<String> for Error { fn from(value: String) -> Self { Error::Str(value) } }

    impl Database {
        pub async fn open() -> Result<Self> {
            let app_dir = if let Some(data_dir) = dirs::data_dir() {
                data_dir.join("typepractice")
            } else { std::path::Path::new(".").to_path_buf() };
            std::fs::create_dir_all(&app_dir)?;
            let db_path = app_dir.join("app.db");

            if ! db_path.exists() {
                std::fs::write(&db_path, DEFAULT_DB)?;
            }

            let conn = rusqlite::Connection::open(db_path)?;
            conn.execute("PRAGMA foreign_keys = ON;", [])?;
            Ok(Database(Arc::new(Mutex::new(conn))))
        }

        pub async fn get_practice_content(&self, id: u32) -> Result<(String, String, usize)> {
            let conn = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            let mut stmt = conn.prepare(
                "SELECT title, content, num_words FROM practice WHERE id = ?1 LIMIT 1"
            )?;
            let mut rows= stmt.query_map([id], |row| {
                let title = row.get::<usize, String>(0)?;
                let content = row.get::<usize, String>(1)?;
                let num_words = row.get::<usize, u32>(2)? as usize;
                Ok((title, content, num_words))
            })?;
            let ret = rows.next().ok_or(format!("no practice with id {id}"))??;
            Ok(ret)
        }

        pub async fn put_practice_result(&self, id: u32, config: UserConfig, status: Status) -> Result<()> {
            let conn = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            let now = match super::time::UNIX_EPOCH.elapsed() {
                Ok(after) => after.as_secs() as i32,
                Err(before) => - (before.duration().as_secs() as i32),
            };

            conn.execute("
                INSERT INTO practice_history (
                    practice_id, created_at,
                    wrong_cnt, word_cnt, millis, typing_cnt, points,
                    allow_del, word_time
                ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)
                ", (
                    id, now,
                    status.wrong, status.finished, status.millis as u32, status.typed, status.points,
                    config.allow_del, config.word_time,
                )
            )?;

            Ok(())
        }

        pub async fn get_best_practice_result(&self, id: u32, config: UserConfig) -> Result<Option<Status>> {
            let conn = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            let mut stmt = conn.prepare("
                SELECT
                    wrong_cnt, word_cnt, millis, typing_cnt, points
                FROM practice_history
                WHERE practice_id = ?1 AND allow_del = ?2 AND word_time = ?3
                ORDER BY created_at DESC
                LIMIT 1
                "
            )?;

            let mut rows = stmt.query_map((id, config.allow_del, config.word_time), |row| {
                let wrong = row.get(0)?;
                let finished = row.get(1)?;
                let millis = row.get::<usize, u32>(2)? as u128;
                let typed = row.get(3)?;
                let points = row.get(4)?;
                Ok(Status {
                    wrong, finished, millis, typed, points, time_active: false,
                })
            })?;

            let ret = rows.next().transpose()?;
            Ok(ret)
        }

        pub async fn get_all_practice_result_summaries(&self, config: UserConfig) -> Result<Vec<ResultSummary>> {
            let conn = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            let mut stmt = conn.prepare("
                SELECT
                    p.id,
                    p.title,
                    p.num_words,
                    ranked.points,
                    ranked.created_at
                FROM practice p
                LEFT JOIN (
                    SELECT *
                    FROM (
                        SELECT 
                            ph.*,
                            ROW_NUMBER() OVER (
                                PARTITION BY practice_id
                                ORDER BY points DESC, created_at DESC
                            ) AS rn
                        FROM practice_history ph
                        WHERE allow_del = ?1 AND word_time = ?2
                    )
                    WHERE rn = 1
                ) ranked
                ON p.id = ranked.practice_id
                ORDER BY p.id ASC;
                "
            )?;

            fn extract_result_summary(row: &rusqlite::Row) -> std::result::Result<ResultSummary, rusqlite::Error> {
                let id = row.get::<_, u32>(0)?;
                let title = row.get::<_, String>(1)?;
                let num_words = row.get::<_, u32>(2)?;
                let points = row.get::<_, Option<u32>>(3)?;
                let date = row.get::<_, Option<i32>>(4)?
                    .and_then(|date| chrono::DateTime::from_timestamp_secs(date as i64))
                    .map(|date| date.with_timezone(&chrono::Local));
                Ok(ResultSummary { id, title, num_words, points, date })
            }

            let rows = stmt.query_map([config.allow_del, config.word_time], extract_result_summary)?;
            let data = rows.collect::<std::result::Result<Vec<_>,_>>()?;
            Ok(data)
        }

        pub async fn clear_practice_history(&self, config: UserConfig) -> Result<()> {
            let conn = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            conn.execute("
                DELETE FROM practice_history
                WHERE allow_del = ?1 AND word_time = ?2
            ", (config.allow_del, config.word_time))?;

            Ok(())
        }

        pub async fn get_userconfig(&self) -> Result<Option<UserConfig>> {
            let conn = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            let mut stmt = conn.prepare("
                SELECT
                    allow_del, word_time, max_speed
                FROM user_config
                WHERE id = ?1
                LIMIT 1
                "
            )?;

            let mut rows = stmt.query_map((1,), |row| {
                let allow_del = row.get(0)?;
                let word_time = row.get(1)?;
                let max_speed = row.get(2)?;
                Ok(UserConfig { allow_del, word_time, max_speed })
            })?;
            
            let ret = rows.next().transpose()?;
            Ok(ret)
        }

        pub async fn put_userconfig(&self, config: UserConfig) -> Result<()> {
            let conn = self.0.lock()
                .map_err(|e| format!("DB mutex poisoned: {e}"))?;

            conn.execute("
                INSERT OR REPLACE INTO user_config (
                    id, allow_del, word_time, max_speed
                ) VALUES (?1, ?2, ?3, ?4)
                ", (
                    1, config.allow_del, config.word_time, config.max_speed,
                )
            )?;

            Ok(())
        }
    }
}