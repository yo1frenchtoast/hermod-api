#CREATE DATABASE hermod_api;
USE hermod_api;
SET AUTOCOMMIT=0;

CREATE TABLE users(
    name    TEXT UNIQUE NOT NULL,
    email   TEXT NOT NULL,
    phone   TEXT NOT NULL,
    sms_account     TEXT,
    telegrambot_token   TEXT,
    telegrambot_chatid  TEXT
);

CREATE TABLE routers(
    name        TEXT UNIQUE NOT NULL,
    loopback    TEXT NOT NULL,
    uptime      TEXT,
    architecture    TEXT,
    version         TEXT,
    last_seen       TEXT
);

CREATE TABLE hosts(
    name    TEXT UNIQUE NOT NULL,
    address TEXT NOT NULL,
    status      TEXT,
    last_down   TEXT,
    last_up     TEXT,
    duration    TEXT,
    witness     TEXT
);
