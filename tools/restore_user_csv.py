import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect('site.sqlite')
cursor = conn.cursor()

def import_csv_data():
    with open('user_data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row['user_email'], row['user_password']

def restore_data_to_db():
    for user_email, user_password in import_csv_data():
        # Insert data into the database
        cursor.execute('INSERT INTO user (email, password) VALUES (?, ?)', 
                       (user_email, user_password))
    conn.commit()

def delete_all_and_reset_index():
    cursor.execute('DELETE FROM user')
    conn.commit()


if __name__ == '__main__':
    delete_all_and_reset_index()
    restore_data_to_db()

# Close the connection
conn.close()
