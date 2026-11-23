/* Para las pruebas he creado la base de datos y las tablas con sus columans directamente en DBeaver
pero he visto que es una buena práctica guardar el schema para migraciones */

CREATE DATABASE IF NOT EXISTS ue_02_01_apis_rest_twitch
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ue_02_01_apis_rest_twitch;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    first_surname VARCHAR(100) NOT NULL,
    second_surname VARCHAR(100) NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    favorite_category VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS favorite_streamers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    twitch_streamer_id VARCHAR(50) NOT NULL,
    twitch_streamer_login VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    UNIQUE KEY unique_user_streamer (user_id, twitch_streamer_id),
    CONSTRAINT fk_favorites_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS playlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT fk_playlists_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS playlist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id INT NOT NULL,
    twitch_video_id VARCHAR(50) NOT NULL,
    video_title VARCHAR(255) NOT NULL,
    streamer_login VARCHAR(100) NOT NULL,
    video_url VARCHAR(255) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
    UNIQUE KEY unique_playlist_video (playlist_id, twitch_video_id)
);