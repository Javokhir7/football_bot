import aiosqlite

DB_NAME = "football.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT,
            name TEXT UNIQUE,
            played INTEGER DEFAULT 0,
            goal_diff TEXT DEFAULT '0',
            points INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            team_name TEXT,
            goals INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_date TEXT,
            match_time TEXT,
            team1 TEXT,
            team2 TEXT
        )
        """)
        await db.commit()

async def get_standings(group_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT name, played, goal_diff, points 
            FROM teams 
            WHERE group_name = ? 
            ORDER BY points DESC
        """, (group_name,))
        return await cursor.fetchall()

async def get_top_scorers(limit: int = 15):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT name, team_name, goals 
            FROM players 
            WHERE goals > 0 
            ORDER BY goals DESC 
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()

async def get_upcoming_matches():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT match_date, match_time, team1, team2 
            FROM matches 
            ORDER BY id ASC
        """)
        return await cursor.fetchall()

async def seed_demo_data():
    async with aiosqlite.connect(DB_NAME) as db:
        # Takrorlanmasligi uchun eski yozuvlarni tozalab tashlaymiz
        await db.execute("DELETE FROM teams")
        await db.execute("DELETE FROM players")
        await db.execute("DELETE FROM matches")

        teams = [
            # Gruppa A
            ("A", "Mahalla", 4, "+9", 9),
            ("A", "2006", 4, "0", 9),
            ("A", "1993", 4, "+10", 7),
            ("A", "2003", 3, "+10", 6),
            ("A", "2009", 5, "-10", 6),
            ("A", "2004", 5, "-6", 5),
            ("A", "2009-23", 5, "-13", 1),

            # Gruppa B
            ("B", "1996-23", 4, "+5", 9),
            ("B", "2002-23", 5, "+3", 7),
            ("B", "1986", 4, "-2", 6),
            ("B", "2005", 4, "-10", 6),
            ("B", "2003-12", 4, "+5", 4),
            ("B", "1991-23", 3, "0", 4),
            ("B", "2002", 4, "-1", 4),

            # Gruppa C
            ("C", "1988", 5, "+10", 10),
            ("C", "2001", 4, "+6", 10),
            ("C", "1991", 3, "+12", 9),
            ("C", "1998-v", 4, "+6", 6),
            ("C", "1992-23", 4, "-7", 4),
            ("C", "2000", 4, "-14", 1),
            ("C", "2008-23", 4, "-13", 0),

            # Gruppa D
            ("D", "1997", 4, "+22", 12),
            ("D", "1994", 5, "+11", 10),
            ("D", "1995", 4, "+9", 7),
            ("D", "1998", 4, "+3", 7),
            ("D", "2007", 4, "-2", 4),
            ("D", "Obod-98", 4, "-10", 3),
            ("D", "1996", 5, "-33", 0),
        ]
        await db.executemany("""
            INSERT INTO teams (group_name, name, played, goal_diff, points)
            VALUES (?, ?, ?, ?, ?)
        """, teams)

        scorers = [
            ("Jahongir", "1997", 17),
            ("Sardor", "2001", 14),
            ("Islom", "1993", 13),
            ("Botir", "1998-v", 12),
            ("Xolyor", "2002-23", 11),
            ("Abdulaziz", "2007", 11),
            ("Botir", "2003", 9),
            ("Ravshan", "2005", 8),
            ("Lochin", "1998", 8),
            ("Farrux", "2002-23", 8),
        ]
        await db.executemany("""
            INSERT INTO players (name, team_name, goals)
            VALUES (?, ?, ?)
        """, scorers)

        matches = [
            ("9-Sentyabr (Chorshanba)", "19:00", "1986", "2005"),
            ("9-Sentyabr (Chorshanba)", "19:40", "2006", "2003"),
            ("9-Sentyabr (Chorshanba)", "20:20", "1997", "2007"),
            ("9-Sentyabr (Chorshanba)", "21:00", "1996-23", "1991-23"),
            ("9-Sentyabr (Chorshanba)", "21:40", "1991", "1998-v"),
            ("9-Sentyabr (Chorshanba)", "22:20", "2008-23", "1992-23"),
            ("9-Sentyabr (Chorshanba)", "23:00", "1995", "1998"),

            ("11-Sentyabr (Juma)", "19:00", "1991", "2001"),
            ("11-Sentyabr (Juma)", "19:40", "2000", "2008-23"),
            ("11-Sentyabr (Juma)", "20:20", "Mahalla", "2004"),
            ("11-Sentyabr (Juma)", "21:00", "1991-23", "2003-12"),
            ("11-Sentyabr (Juma)", "21:40", "2005", "2002"),
            ("11-Sentyabr (Juma)", "22:20", "Obod", "2007"),
            ("11-Sentyabr (Juma)", "23:00", "1993", "2003"),
        ]
        await db.executemany("""
            INSERT INTO matches (match_date, match_time, team1, team2)
            VALUES (?, ?, ?, ?)
        """, matches)

        await db.commit()