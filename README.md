## Udacity DEND Project : Data Warehouse on Amazon Redshift
The objective of this project to create an anlytical data warehouse on Cloud with Amazon Redshift for a fictional music startup sparkify. The data warehouse is to identify which songs users are listening to and how people are interacting with the sparkify music listening app.

## Introduction
In this project a analytical relational database is created on Amazon Redshift. Redshift fetch the data from json files stored in S3 Bucket, transform it and save it in fact and dimensional tables for easy understanding and analysis.

## Redshift Overview
- Amazon Redshift is an enterprise-level, petabyte scale, fully managed data warehousing service.
- It is a columnar based MPP Database.
- We can start with just a few hundred gigabytes of data and scale to a petabyte or more. This enables us to use our data to acquire new insights for your business and customers. Regardless of the size of the data set, Amazon Redshift offers fast query performance using the same SQL-based tools and business intelligence applications that we use today.
- It is easy to setup, deploy, & manage. To read more about Redshift [click here](https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html)

## Project Goal
The analytics Team wants to analyze the behaviour of users on sparkify app.

Following things can be analyzed:

1. Most heared song
2. Most liked artist
3. Usage and Artist Distribution by country
4. No. of paid subscribers
5. Distribution of gender in users
6. Where more money needs to be invested to increase the engagement of users
7. How many paid and free subscribers
8. Average hours spend by users on app	
	... and many more
	
## Data Required for Project
Here we are working with two datasets that reside in S3 Bucket. Here are the S3 links for each:
* Song data: ```s3://udacity-dend/song_data```
* Log data: ```s3://udacity-dend/log_data```

**Log data json path**: ```s3://udacity-dend/log_json_path.json```

#### Song Dataset
The first dataset is a subset of real data from the [Million Song](https://labrosa.ee.columbia.edu/millionsong/) Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are filepaths to two files in this dataset:
```
song_data/A/B/C/TRABCEI128F424C983.json
song_data/A/A/B/TRAABJL12903CDCF1A.json
```
And below is an example of what a single song file, TRAABJL12903CDCF1A.json, looks like:
```
{"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}
```
#### Log Dataset
The second dataset consists of log files in JSON format generated by this [event simulator](https://github.com/Interana/eventsim) based on the songs in the dataset above. These simulate activity logs from a music streaming app based on specified configurations.

The log files in the dataset you'll be working with are partitioned by year and month. For example, here are filepaths to two files in this dataset:
```
log_data/2018/11/2018-11-12-events.json
log_data/2018/11/2018-11-13-events.json
```
## Data Model
Using the song and log datasets, data is transformed into Star Schema, so that it can be queries easily and understandable to analysts and business users.
First Data is fetched from S3 bucket to staging tables.
![Staging Taables](https://github.com/vikaskumar23/Udacity-DEND-Project-Data-Warehouse-on-Redshift/blob/master/staging_tables.PNG)

Then after some transformations data is loaded into star Schema. Some transformations include:
- Date data is divided in chunks to create date dimension.
- Data from songs table and events table is joined to create songplays fact table.
- Duplicate data is removed before inserting to star schema.

The resulting star schema consists of one fact table and four dimension tables.
![Data Model](https://github.com/vikaskumar23/Udacity-DEND-Project-Data-Warehouse-on-Redshift/blob/master/dbmodel.png)
##### Fact Table
- **songplays:** records in log data associated with song plays i.e. records with page ```NextSong```
    - **songplay_id:** unique id for each songplay event
    - **start_time:** start time of event (timestamp)
    - **user_id:** user_id of user
    - **level:** it shows user is paid subscriber or not
    - **song_id:** id of the played song
    - **artist_id:** id of artist
    - **session_id:** id of the current session
    - **location:** location of artist
    - **user_agent:** device/software to access sparkify app

##### Dimension Tables
- **users:** users in the app
    - **user_id:** unique id of user
    - **first_name:** first name of user
    - **last_name:** last name of user
    - **gender:** gender of user
    - **level:** it shows user is paid subscriber or not
- **songs:** songs in music database
    - **song_id:** unique id of song
    - **title:** name of the song
    - **artist_id:** id of artist
    - **year** year in which song is created
    - **duration:** duration of song in seconds
- **artists:** artists in music database
    - **artist_id:** unique id of artist
    - **name:** name of the artist
    - **location:** location of the artist
    - **latitude** latitude of artist location
    - **longitude:** longitude of artist location
- **time:** timestamps of records in songplays broken down into specific units
    - **start_time:** start time timestamp
    - **hour:** hour of event
    - **day:** day of event
    - **week** week of event
    - **month:** month of event
    - **year:** year of event
    - **weekday:** weekday of event

## Explanation for use of ```distkey``` and ```sortkey```
**DISTKEY**
> song_id of songplays and song_id of songs are taken as distkey, this allows data with same key value to lie at one slice, which results in less shuffling during join, as in many queries these two tables are joined. And diststyle all can't be applied to songs table as there are a large number of songs, so its better to use distkey here. Many times data is grouped by song name, so distkey is a better solution in that case.

**SORTKEY**
> song_id, artist_id, user_id, start_time are taken as sort key as many time we need to execute where search on dimension data, and in that scenario sortkey is a good option.

**DISTSTYLE ALL**
> Distribution Style All is choosen for artists table as it is used to join a lot with songsplay table, and the count of artists data is also less compared to songs tables so diststyle is a good option here than distkey.

## ETL Job
1. Staging, Fact and Dimension tables are created in database.
2. Then data from S3 bucket is copied into staging tables using **COPY** Command.
3. Then data is processed and loaded into star schema analytical tables.

## Project Files
The project includes five files:

1. **create_table.py :** To create fact and dimension tables for the star schema in Redshift.
2. **etl.py:** To load data from S3 Bucket into staging tables on Redshift and then process that data into analytics tables on Redshift.
3. **sql_queries.py:** To define the SQL statements, which will be imported into the two other files above.
4. **README.md:** Description of Project.
4. **dwh.cfg:** Contains all the configurations related to this project.

## Project Execution

#### Steps
1. Setup the Redshift Cluster on [Amazon Redshift](https://console.aws.amazon.com/redshiftv2/home)
2. Complete the config file ```dwh.cfg``` with all the aws ```iam arn``` and ```database``` credentials
3. Create all staging, fact and dimension tables:
	```
	python create_tables.py
	```
4. Execute ETL process to load data in analytical tables:
	```
	python etl.py
	```
5. Delete the Redshift Cluster when finished

## Analytical Queries

1. Number of session created : 279 Unique Sessions Created
	```
	select count(distinct session_id) from songplays;
	```

2. Number of times each song heard 
	```
	select songs.title, count(*) from songplays join songs on songplays.song_id=songs.song_id group by 1;
	```

## References

www.udacity.com

https://docs.aws.amazon.com/redshift/index.html

https://medium.com/@maskepravin02/why-distkey-and-sortkey-are-important-45ca94d12290





















