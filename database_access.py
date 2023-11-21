import sqlite3

def add_primary_key_column(table_name):
    # Connect to the SQLite database
    connection = sqlite3.connect('data_base.db')
    cursor = connection.cursor()

    # Fetch the table schema
    #cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
    #table_schema = cursor.description
    cursor.execute(f'PRAGMA TABLE_INFO({table_name})')
    table_schema = cursor.fetchall()
    print('schema')
    print(table_schema)

    # Create a temporary table with the desired schema
    temp_table_name = f'{table_name}_temp'
    cursor.execute(f"CREATE TABLE {temp_table_name} AS SELECT * FROM {table_name}")

    # Drop the original table
    cursor.execute(f"DROP TABLE {table_name}")

    # Construct the new table creation query with the primary key column
    create_query = f"CREATE TABLE {table_name} (entry INTEGER PRIMARY KEY, "
    create_query += ", ".join([f'"{column[1]}" {column[2]}' for column in table_schema])
    create_query += ")"

    # Create the new table with the primary key column
    print(create_query)
    cursor.execute(create_query)

    # Copy data from the temporary table to the new table
    cursor.execute(f"INSERT INTO {table_name} SELECT NULL, * FROM {temp_table_name}")

    # Drop the temporary table
    cursor.execute(f"DROP TABLE {temp_table_name}")

    # Commit the changes and close the connection
    connection.commit()
    connection.close()

connection = sqlite3.connect('data_base.db')
cursor = connection.cursor()

'''data = ('user', 'user_name/;first_name/;last_name/;email')
cursor.execute('INSERT INTO table_metadata (table_name, show_in_summary) VALUES (?, ?)', data)'''

'''table_name = 'user'
add_primary_key_column(table_name)
table_name = 'project'
add_primary_key_column(table_name)
table_name = 'client'
add_primary_key_column(table_name)
table_name = 'discipline'
add_primary_key_column(table_name)
table_name = 'activity'
add_primary_key_column(table_name)'''

#cursor.execute('CREATE TABLE project (entry INTEGER PRIMARY KEY, project_name TEXT, lsd TEXT, owner TEXT, project_manager TEXT, project_engineer TEXT, stress_engineer TEXT, civil_engineer TEXT, electrical_engineer TEXT, drafting_lead TEXT)')
#connection.commit()
#cursor.execute('CREATE TABLE validation_setting (entry INTEGER PRIMARY KEY, target TEXT, source TEXT, criteria_1 TEXT, filter_1 TEXT, criteria_2 TEXT, filter_2 TEXT, criteria_3 TEXT, filter_3 TEXT, criteria_4 TEXT, filter_4 TEXT)')

#cursor.execute('CREATE TABLE table_metadata (entry INTEGER PRIMARY KEY, table_name TEXT, show_in_summary TEXT)')
#cursor.execute('DROP TABLE table_metadata')
#cursor.execute('CREATE TABLE table_metadata (entry INTEGER PRIMARY KEY, table_name TEXT, show_in_summary TEXT)')
#cursor.executemany('INSERT INTO table_metadata (table_name,show_in_summary) VALUES (?, ?)', [('user', ''), ('project', ''), ('client', ''), ('activity', ''), ('discipline', ''), ('group', '')])

#cursor.execute('SELECT * FROM time_sheet WHERE strftime("%Y-%m-%d", "submit_date") = strftime("%Y-%m-%d", "2023-05-19")')
#cursor.execute('ALTER TABLE validation_setting ADD COLUMN dropdown_list_type')

'''cursor.execute('UPDATE project SET project_manager = "user1/;admin" WHERE entry = "5"')
cursor.execute('SELECT * FROM project')'''
#print(cursor.fetchall())

#cursor.execute('ALTER TABLE time_sheet RENAME COLUMN None TO entry')
#connection.commit()
#cursor.execute('ALTER TABLE validation_setting RENAME TO dropdown_list_setting')

#cursor.execute('ALTER TABLE time_sheet RENAME COLUMN username TO user_name')
#connection.commit()

#cursor.execute('ALTER TABLE time_sheet RENAME COLUMN None TO entry')
#connection.commit()

'''for rowid in range(1, len(validation_data), 1):
    cursor.execute(f'DELETE FROM validation_setting WHERE entry = {rowid}')
connection.commit()'''
#cursor.execute('DROP TABLE datatype_setting')
#cursor.execute('CREATE TABLE datatype_setting (entry INTEGER PRIMARY KEY, "column_reference" TEXT, "datatype" TEXT, "uniqueness" TEXT, "special_type" TEXT)')
#cursor.execute('INSERT INTO table_metadata (table_name, show_in_summary) VALUES (?, ?)', ('time_sheet', 'hours/;comment'))
#cursor.execute('ALTER TABLE user DROP COLUMN "group"')

#cursor.execute('SELECT * FROM time_sheet')
#cursor.execute('PRAGMA TABLE_INFO(user)')
#print(cursor.fetchall())
cursor.execute('SELECT * FROM activity')
print(cursor.fetchall())

#connection.commit()
cursor.close()
connection.close()
#cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN entry INTEGER PRIMARY KEY')
#cursor.execute('PRAGMA TABLE_INFO(time_sheet)')
#print(cursor.fetchall())

'''
cursor.execute('PRAGMA TABLE_INFO(people)')
print(cursor.fetchall())
#cursor.execute('CREATE TABLE people (entry INTEGER PRIMARY KEY, last_name TEXT, age INTEGER, email TEXT)')
#cursor.execute('SELECT * FROM people')
#print(cursor.fetchall())
#cursor.execute('ALTER TABLE people ADD COLUMN age')
#cursor.execute('DELETE FROM people WHERE last_name = "Durant"')
#connection.commit()
new_data = [('surname', 'entry', 'age', 'weight', 'email', 'attr2$rename(attribute)'),
            ('Paterson', 1, 10, 100, 'someone1', 'att1'),
            ('Lee', 2, 20, 200, 'someone2', 'att2'),
            ('Braun', 3, 30, 300, 'someone3', 'att3'),
            ('', 4, 40, 400, 'email4', 'att4')
            ]

save_uploaded('people', new_data)
#cursor.executemany('INSERT INTO people (entry, last_name, age, email) VALUES (?, ?, ?, ?)', data)

print('###############after#################################')
cursor.execute('PRAGMA TABLE_INFO(people)')
print(cursor.fetchall())
cursor.execute('SELECT * FROM people')
print(cursor.fetchall())
'''
#cursor.execute('CREATE TABLE time_sheet_1 (entry INTEGER PRIMARY KEY, user_name TEXT, submit_date DATE, client TEXT, project TEXT, discipline TEXT, activity TEXT, hours REAL, comment TEXT, status TEXT)')
#cursor.execute('INSERT INTO time_sheet_1 (entry, user_name, submit_date, client, project, discipline, activity, hours, comment, status) SELECT NULL, user_name, "date", client, project, discipline, activity, hours, comment, status FROM time_sheet')
#cursor.execute('ALTER TABLE time_sheet ADD COLUMN status TEXT')

#cursor.execute('SELECT * FROM time_sheet_1')
#print(cursor.fetchall())

#connection.commit()
#cursor.execute('DELETE FROM "time_sheet" WHERE strftime("%Y-%m-%d", "date") = strftime("%Y-%m-%d", "2023-05-05")')
#connection.commit()
#cursor.close()
#cursor.execute("ALTER TABLE time_sheet DROP COLUMN rowid")

'''cursor.execute(f'PRAGMA table_info(time_sheet)')
headers = [col[1] for col in cursor.fetchall()]
print(headers)
cursor.execute('SELECT * FROM time_sheet')

cursor.execute('DELETE FROM time_sheet WHERE CAST("entry"AS INTEGER) > CAST("1" AS INTEGER)')

cursor.execute('SELECT * FROM time_sheet')
print(cursor.fetchall())'''

'''print(data_fetched)
cursor.execute("SELECT * FROM time_sheet where  strftime('%Y-%m-%d', date) >= '2023-03-26' and  strftime('%Y-%m-%d', date) <= '2023-05-06' and date in ('05-01')")
data_fetched = cursor.fetchall()
print(data_fetched)'''

'''cursor.execute(f'PRAGMA table_info(users)')
headers = [col[1] for col in cursor.fetchall()]
print(headers)'''

'''cursor.execute("ALTER TABLE 'users' DROP COLUMN 'csrf_token'")
cursor.execute(f'PRAGMA table_info(users)')
headers = [col[1] for col in cursor.fetchall()]
print(headers)'''

#cursor.execute("SELECT * FROM 'users' WHERE username = 'user11'")
#print(cursor.fetchall())

'''cursor.execute('SELECT * FROM projects WHERE "project_name" = "05-01 Superpad"')
print(cursor.fetchall())'''

'''cursor.execute(f'PRAGMA table_info(projects)')
headers = [col[1] for col in cursor.fetchall()]
print(headers)'''

'''cursor.execute("alter table users add column first_name text")
cursor.execute("alter table users add column last_name text")
connection.commit()'''

'''cursor.execute("select * from users where username in ('user1')")
data_fetched = cursor.fetchall()'''

'''cursor.execute("update users set first_name = ?, last_name = ? where username = 'pzhong1'", ('Paul', 'Zhong1'))
connection.commit()'''