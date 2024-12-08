CREATE TABLE content_generation (user_id TEXT PRIMARY KEY,prompt TEXT,video_paths TEXT,image_paths TEXT,status TEXT,generated_at TIMESTAMP);

CREATE TABLE login_logs ( log_id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT,action TEXT,timestamp TIMESTAMP);


