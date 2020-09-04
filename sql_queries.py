import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
    CREATE TABLE IF NOT EXISTS staging_events (
    artist varchar,
    auth varchar,
    firstName varchar,
    gender varchar,
    itemInSession int,
    lastName varchar,
    length decimal,
    level varchar,
    location varchar,
    method varchar,
    page varchar,
    registration varchar,
    sessionId int,
    song varchar,
    status int,
    ts bigint,
    userAgent varchar,
    userId int
    )
""")

staging_songs_table_create = ("""
    CREATE TABLE IF NOT EXISTS staging_songs(
    num_songs smallint,
    artist_id varchar,
    artist_latitude decimal,
    artist_longitude decimal,
    artist_location varchar,
    artist_name varchar,
    song_id varchar,
    title varchar,
    duration decimal,
    "year" smallint
    )
""")

songplay_table_create = ("""
    CREATE TABLE IF NOT EXISTS songplays(
    songplay_id int IDENTITY(0,1) PRIMARY KEY,
    start_time timestamp NOT NULL REFERENCES time(start_time) sortkey,
    user_id int NOT NULL REFERENCES users(user_id),
    level varchar NOT NULL,
    song_id varchar NOT NULL REFERENCES songs(song_id) distkey,
    artist_id varchar NOT NULL REFERENCES artists(artist_id),
    session_id int NOT NULL,
    location varchar NOT NULL,
    user_agent varchar NOT NULL
    )
""")

user_table_create = ("""
    CREATE TABLE IF NOT EXISTS users(
    user_id int PRIMARY KEY sortkey,
    first_name varchar NOT NULL,
    last_name varchar NOT NULL,
    gender varchar NOT NULL,
    level varchar NOT NULL
    )
""")

song_table_create = ("""
    CREATE TABLE IF NOT EXISTS songs(
    song_id varchar PRIMARY KEY SORTKEY distkey,
    title varchar NOT NULL,
    artist_id varchar NOT NULL,
    year smallint NOT NULL,
    duration decimal NOT NULL
    )
""")

artist_table_create = ("""
    CREATE TABLE IF NOT EXISTS artists(
    artist_id varchar PRIMARY KEY SORTKEY,
    name varchar NOT NULL,
    location varchar NOT NULL,
    latitude decimal NOT NULL,
    longitude decimal NOT NULL
    ) diststyle all;
""")

time_table_create = ("""
    CREATE TABLE IF NOT EXISTS time(
    start_time timestamp PRIMARY KEY SORTKEY,
    hour smallint NOT NULL,
    day smallint NOT NULL,
    week smallint NOT NULL,
    month smallint NOT NULL,
    year smallint NOT NULL,
    weekday smallint NOT NULL
    )
""")

# STAGING TABLES

staging_events_copy = ("""
    COPY staging_events FROM {}
    iam_role {}
    region 'us-west-2'
    JSON {};
""").format(config['S3']['LOG_DATA'], config['IAM_ROLE']['ARN'], config['S3']['LOG_JSONPATH'])

staging_songs_copy = ("""
    COPY staging_songs FROM {}
    iam_role {}
    region 'us-west-2'
    JSON 'auto';
""").format(config['S3']['SONG_DATA'], config['IAM_ROLE']['ARN'])

# FINAL TABLES

songplay_table_insert = ("""
    INSERT INTO songplays(start_time, user_id,level, song_id, artist_id, session_id, location, user_agent)
    SELECT DISTINCT timestamp 'epoch' + (ts/1000) * interval '1 second' as start_time,
    userId as user_id,
    level,
    staging_songs.song_id as song_id,
    staging_songs.artist_id,
    sessionId as session_id,
    location,
    userAgent as user_agent
    FROM staging_events
    JOIN staging_songs 
    ON
    staging_events.song = staging_songs.title
    AND
    staging_events.page='NextSong';
""")

user_table_insert = ("""
    INSERT INTO users(user_id, first_name, last_name, gender, level)
    SELECT DISTINCT 
    userId as user_id,
    firstName as first_name,
    lastName as last_name,
    gender,
    level
    FROM staging_events
    WHERE
    page='NextSong' AND user_id IS NOT NULL;
""")

song_table_insert = ("""
    INSERT INTO songs(song_id, title, artist_id, year, duration)
    SELECT 
    song_id,
    title,
    artist_id,
    year,
    duration
    FROM staging_songs
    WHERE
    song_id IS NOT NULL;
""")

artist_table_insert = ("""
    INSERT INTO artists(artist_id, name, location, latitude, longitude)
    SELECT DISTINCT 
    artist_id, 
    artist_name as name, 
    CASE WHEN artist_location IS NULL THEN '' ELSE artist_location END as location,
    CASE WHEN artist_latitude IS NULL THEN 0.0 ELSE artist_latitude END as latitude,
    CASE WHEN artist_longitude IS NULL THEN 0.0 ELSE artist_longitude END as longitude
    FROM staging_songs
    WHERE
    artist_id IS NOT NULL;
""")

time_table_insert = ("""
    INSERT INTO time(start_time , hour, day, week, month, year, weekday)
    SELECT DISTINCT timestamp 'epoch' + (ts/1000) * interval '1 second' as start_time,
    EXTRACT(hour from start_time) as hour,
    EXTRACT(day from start_time) as day,
    EXTRACT(week from start_time) as week,
    EXTRACT(month from start_time) as month,
    EXTRACT(year from start_time) as year,
    EXTRACT(dow from start_time) as weekday
    FROM staging_events WHERE page='NextSong';
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, user_table_create, song_table_create, artist_table_create, time_table_create, songplay_table_create,]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
