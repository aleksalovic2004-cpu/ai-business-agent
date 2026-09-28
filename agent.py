from dotenv import load_dotenv
import os

load_dotenv()
from google import genai
import sqlite3

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def pitanje_u_sql(pitanje: str) -> str:
    prompt = f"""
Imaš SQLite tabelu 'prodaja' sa kolonama: id, datum (format YYYY-MM-DD), proizvod (tekst), kolicina (broj), cena (broj, cena po komadu u dinarima).

Na osnovu pitanja korisnika, vrati ISKLJUČIVO SQL upit koji odgovara na to pitanje. Ne objašnjavaj, ne dodaj tekst pre ili posle, samo čist SQL bez markdown formatiranja.

Pitanje: {pitanje}
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={"temperature": 0}
    )
    sql = response.text.strip().replace("```sql", "").replace("```", "").strip()
    return sql


def izvrsi_sql(sql: str):
    sql_provera = sql.strip().upper()
    if not sql_provera.startswith("SELECT"):
        raise ValueError("Odbijen upit koji nije SELECT — samo čitanje podataka je dozvoljeno.")

    conn = sqlite3.connect("prodaja.db")
    cursor = conn.cursor()
    cursor.execute(sql)
    rezultat = cursor.fetchall()
    conn.close()
    return rezultat

def odgovori_na_pitanje(pitanje: str) -> str:
    sql = pitanje_u_sql(pitanje)
    print("Generisani SQL:", sql)  # korisno za proveru, kasnije obriši
    rezultat = izvrsi_sql(sql)

    prompt_odgovor = f"""
Korisnik je postavio pitanje: "{pitanje}"
Rezultat upita nad bazom je: {rezultat}

Formuliši kratak, prirodan odgovor na srpskom jeziku na osnovu ovih podataka. Uvek navedi valutu (dinara) kada se radi o novčanom iznosu. Ne pominji SQL niti bazu podataka.
Ne koristi markdown formatiranje (bez zvezdica, bez tabela) — piši običnim tekstom.
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt_odgovor,
        config={"temperature": 0.3}
    )
    return response.text


if __name__ == "__main__":
    while True:
        pitanje = input("\nPostavi pitanje (ili 'kraj' za izlaz): ")
        if pitanje.lower() == "kraj":
            break
        print(odgovori_na_pitanje(pitanje))