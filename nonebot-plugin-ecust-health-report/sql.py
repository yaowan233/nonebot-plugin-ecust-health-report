import sqlite3


def init():
    conn = sqlite3.connect("identifier.sqlite")
    cursor = conn.cursor()
    sql = """create table if not exists school_account(
        uid varchar primary key not null,
        id varchar not null,
        password varchar not null
    )
    """
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


def add_school_account(uid, school_account, password):
    init()
    conn = sqlite3.connect("identifier.sqlite")
    cursor = conn.cursor()
    sql = """insert into school_account values(?, ?, ?)"""
    cursor.execute(sql, (uid, school_account, password))
    conn.commit()
    cursor.close()
    conn.close()


def get_school_account():
    init()
    conn = sqlite3.connect("identifier.sqlite")
    cursor = conn.cursor()
    sql = """select * from school_account"""
    cursor.execute(sql)
    conn.commit()
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def delete_school_account(uid):
    init()
    conn = sqlite3.connect("identifier.sqlite")
    cursor = conn.cursor()
    sql = f'''delete from school_account where uid ={uid}'''
    cursor.execute(sql)
    cursor.close()
    conn.commit()
    conn.close()
