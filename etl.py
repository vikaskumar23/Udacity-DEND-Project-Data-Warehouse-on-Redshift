import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
    Load staging tables by executing copy command on Redshift Database
    
    Args:
        (obj) cur - Cursor object to execute sql queries on Redshift Database
        (obj) conn - Connection object to interact with database
    
    Return:
        None
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
    Load data from staging tables, process it and inserts into Star Schema Tables.
    
    Args:
        (obj) cur - Cursor object to execute sql queries on Redshift Database
        (obj) conn - Connection object to interact with database
    
    Return:
        None
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
    Create Connection with Redshift Database and prepare load data in data warehouse.
    
    Args:
        None
    
    Return:
        None
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()