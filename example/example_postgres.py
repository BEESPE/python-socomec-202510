import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="tp_bdd",
    user="ton_utilisateur",
    password="ton_motdepasse"
)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    age INT
)
""")
conn.commit()

students = [("Alice", 25), ("Bob", 30), ("Charlie", 22)]
cur.executemany("INSERT INTO students (name, age) VALUES (%s, %s)", students)
conn.commit()

cur.execute("SELECT * FROM students")
for row in cur.fetchall():
    print(row)

cur.execute("UPDATE students SET age = %s WHERE name = %s", (23, "Charlie"))
conn.commit()

cur.execute("SELECT * FROM students ORDER BY age ASC")
print(cur.fetchall())

cur.execute("DELETE FROM students WHERE name = %s", ("Bob",))
conn.commit()

cur.close()
conn.close()
