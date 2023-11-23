import sqlite3
import csv

# Connect to the SQLite database
conn = sqlite3.connect('site.sqlite')
cursor = conn.cursor()

def iter_rows():
    query = '''
    SELECT user.id, team.name AS team_name, sticker.name AS sticker_name
    FROM user
    JOIN sticker_wanted ON user.id = sticker_wanted.user_id
    JOIN sticker ON sticker_wanted.sticker_id = sticker.id
    JOIN team ON sticker.team_id = team.id
    '''

    cursor.execute(query)
    for row in cursor.fetchall():
        yield row

def generate_sticker_wanted_csv():
    with open('sticker_wanted_data.csv', 'w', newline='', encoding="utf-8") as csvfile:
        fieldnames = ['user_id', 'team_name', 'sticker_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for user_id, team_name, sticker_name in iter_rows():
            writer.writerow({'user_id': user_id, 'team_name': team_name, 'sticker_name': sticker_name})

if __name__ == '__main__':
    generate_sticker_wanted_csv()

# Close the connection
conn.close()
