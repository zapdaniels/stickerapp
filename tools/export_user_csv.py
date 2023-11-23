import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect('site.sqlite')
cursor = conn.cursor()

def iter_rows():
    query = '''
    SELECT user.email, user.password FROM user
    '''

    cursor.execute(query)
    for row in cursor.fetchall():
        yield row

def generate_sticker_wanted_csv():
    with open('user_data.csv', 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ['user_email', 'user_password']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for user_email, user_password in iter_rows():
            writer.writerow({'user_email': user_email, 'user_password': user_password})

if __name__ == '__main__':
    generate_sticker_wanted_csv()

# Close the connection
conn.close()
