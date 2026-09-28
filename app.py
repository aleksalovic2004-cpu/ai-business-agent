from flask import Flask, request, jsonify, render_template, session
from agent_langchain import agent

app = Flask(__name__)
app.secret_key = "promeni-ovo-u-nesto-tajno"  # potrebno za session

@app.route("/")
def pocetna():
    session["istorija"] = []
    return render_template("index.html")

@app.route("/pitaj", methods=["POST"])
def pitaj():
    podaci = request.get_json()
    pitanje = podaci.get("pitanje", "")
    if not pitanje:
        return jsonify({"greska": "Pitanje ne sme biti prazno."}), 400

    istorija = session.get("istorija", [])
    istorija.append({"role": "user", "content": pitanje})

    rezultat = agent.invoke({"messages": istorija})
    odgovor = rezultat["messages"][-1].content

    istorija.append({"role": "assistant", "content": odgovor})
    session["istorija"] = istorija

    return jsonify({"odgovor": odgovor})

if __name__ == "__main__":
    app.run(debug=True)