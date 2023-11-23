import sqlite3
import json

# Path to the SQLite database file
database_path = 'site.sqlite'

# Connect to the SQLite database
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Create the 'team' table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS team (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')

# Create the 'sticker' table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sticker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        team_id INTEGER,
        FOREIGN KEY (team_id) REFERENCES team (id)
    )
''')

cursor.execute('DELETE FROM sticker')
cursor.execute('DELETE FROM team')

# Dummy data for teams and stickers
with open("data/sticker.json", encoding="utf-8") as f:
    data = json.load(f)

# Dictionary to store team IDs
team_ids = {}

def iter_teams_and_names():
    for entry in data:
        if "teams" in entry:
            for team_name in entry["teams"]:
                for name in ["Oben-Links", "Oben-Rechts", "Unten-Links", "Unten-Rechts"]:
                    yield team_name, name
        else:
            team_name = entry['team']
            for name in entry["stickers"]:
                yield team_name, name

for team, name in iter_teams_and_names():
    if team not in team_ids:
        cursor.execute('INSERT INTO team (name) VALUES (?)', (team,))
        conn.commit()  # Commit changes to get the team ID
        team_ids[team] = cursor.lastrowid

    # Insert into 'sticker' table
    print(name, team, team_ids)
    cursor.execute(
        'INSERT INTO sticker (name, team_id) VALUES (?, ?)',
        (name, team_ids[team])
    )


# Commit the changes and close the connection
conn.commit()
conn.close()

print('Data loaded successfully.')
