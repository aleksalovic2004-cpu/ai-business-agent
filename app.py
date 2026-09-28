import os
import hmac

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, render_template, session, redirect, url_for

# Na serveru baza ne postoji dok se ne napravi, pa je pravimo pri prvom pokretanju
if not os.path.exists("prodaja.db"):
    import napravi_bazu  # noqa: F401

from agent_langchain import agent

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "lokalni-tajni-kljuc")
PRISTUPNA_SIFRA = os.getenv("APP_PASSWORD")


@app.route("/login", methods=["GET", "POST"])
def login():
    greska = None
    if request.method == "POST":
        uneto = request.form.get("sifra", "")
        if PRISTUPNA_SIFRA and hmac.compare_digest(uneto, PRISTUPNA_SIFRA):
            session["ulogovan"] = True
            return redirect(url_for("pocetna"))
        greska = "Pogrešna šifra."
    return render_template("login.html", greska=greska)


@app.route("/")
def pocetna():
    if not session.get("ulogovan"):
        return redirect(url_for("login"))
    session["istorija"] = []
    return render_template("index.html")


@app.route("/pitaj", methods=["POST"])
def pitaj():
    if not session.get("ulogovan"):
        return jsonify({"greska": "Nisi prijavljen."}), 401

    podaci = request.get_json()
    pitanje = podaci.get("pitanje", "")
    if not pitanje:
        return jsonify({"greska": "Pitanje ne sme biti prazno."}), 400

    # Čuvamo samo poslednjih 7 poruka jer se istorija čuva u kolačiću (limit ~4 KB)
    istorija = (session.get("istorija", []) + [{"role": "user", "content": pitanje}])[-7:]

    rezultat = agent.invoke({"messages": istorija})
    odgovor = rezultat["messages"][-1].content

    istorija.append({"role": "assistant", "content": odgovor})
    session["istorija"] = istorija

    return jsonify({"odgovor": odgovor})


if __name__ == "__main__":
    app.run(debug=True)