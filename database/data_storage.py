import sqlite3
import pickle


connection = sqlite3.connect('data.db')
cursor = connection.cursor()

#cursor.execute("create table gta (release_year integer, release_name text, city text)")
#cursor.execute("create table gta (object BLOB)")
#cursor.execute('CREATE TABLE mytable (id INTEGER PRIMARY KEY, myarray BLOB)')

x = [1, 2, 3]
x_binary = pickle.dumps(x)
x_binary_array = [x_binary, x_binary]

release_list = [
    (1997, "model1", "liberty city"),
    (2000, "model2", "New York")
]

#steralized = pickle.dumps(release_list)

#cursor.executemany("insert into gta values (?,?,?)", release_list)
#cursor.execute("alter table gta add column extra_column3 BLOB")
#cursor.execute("insert into gta values (?,?,?)", (1988, "model1", "some city"))
#cursor.execute("insert into gta values (?,?,?)", (1988, "model1", "some city"))
#cursor.execute("delete from gta where release_year = ?", (1988,))
#cursor.execute("update gta set extra_column3 = ? where release_year = ?", ('ab', 2000))
#cursor.execute("update gta set extra_column3 = ? where release_year = ?", ((sqlite3.Binary(x_binary),), 2000))
#cursor.execute("alter table gta add column extra_column4 BLOB")
#cursor.executemany('INSERT INTO gta (extra_column2) VALUES (?)', [(sqlite3.Binary(s),) for s in x_binary_array])
#cursor.execute("update gta set extra_column4 = ? where release_year = ?", ((sqlite3.Binary(x_binary)), 2000))
#cursor.execute("SELECT * FROM gta")

#gta_fetched = cursor.fetchall()

cursor.execute("SELECT extra_column4 FROM gta where release_year = ?", (2000,))
selected_binary = cursor.fetchone()
desterialized = pickle.loads(selected_binary[0])
print(desterialized)

#print(gta_fetched)



print('######################################')

'''cursor.execute("select * from gta where city=:a", {"a": "liberty city"})
gta_search = cursor.fetchall()
print(gta_search)

cursor.execute("create table cities (gta_city text, real_city text)")
cursor.execute("insert into cities values (?,?)", ("liberty city", "New York"))
cursor.execute("select * from cities where gta_city=:d", {"d": 'liberty city'})
cities_search = cursor.fetchall()
print('#######################################')

print(cities_search)


print('#######################################')
for n in gta_search:
    adjusted = [cities_search[0][1] if value==cities_search[0][0] else value for value in n]'''

cursor.close()
connection.commit()
connection.close()