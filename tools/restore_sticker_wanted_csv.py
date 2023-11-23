import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect('site.sqlite')
cursor = conn.cursor()

def import_csv_data():
    with open('sticker_wanted_data.csv', 'r', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row['user_id'], row['team_name'], row['sticker_name']

def restore_data_to_db():
    for user_id, team_name, sticker_name in import_csv_data():
        #print(user_id, team_name, sticker_name)
        # Insert data into the database
        cursor.execute(('INSERT INTO sticker_wanted (user_id, sticker_id) VALUES '
                        '(?, (SELECT id FROM sticker WHERE name = ? AND team_id = (SELECT id FROM team WHERE name = ?)))'), 
                       (user_id, sticker_name, team_name))

    # Commit the changes
    conn.commit()

def delete_all_and_reset_index():
    cursor.execute('DELETE FROM sticker_wanted')
    #for x in cursor.execute('SELECT name FROM sqlite_sequence'):
    #    print(x)
    #cursor.execute('DELETE FROM sqlite_sequence WHERE name = "sticker_wanted"')
    conn.commit()


if __name__ == '__main__':
    delete_all_and_reset_index()
    restore_data_to_db()

# Close the connection
conn.close()
