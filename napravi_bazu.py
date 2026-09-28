import sqlite3
import random
from datetime import date, timedelta
random.seed(42)

conn = sqlite3.connect("prodaja.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prodaja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum TEXT,
    proizvod TEXT,
    kolicina INTEGER,
    cena REAL
)
""")

proizvodi = ["Šrafovi M6", "Lim 2mm", "Cevi 20mm", "Profil aluminijum", "Zavrtnji M8"]
pocetni_datum = date(2025, 1, 1)

redovi = []
for i in range(200):
    datum = pocetni_datum + timedelta(days=random.randint(0, 300))
    proizvod = random.choice(proizvodi)
    kolicina = random.randint(1, 50)
    cena = round(random.uniform(50, 500), 2)
    redovi.append((datum.isoformat(), proizvod, kolicina, cena))

cursor.executemany(
    "INSERT INTO prodaja (datum, proizvod, kolicina, cena) VALUES (?, ?, ?, ?)",
    redovi
)

conn.commit()
conn.close()
print("Baza napravljena, ubačeno", len(redovi), "redova.")