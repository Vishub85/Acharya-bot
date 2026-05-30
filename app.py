from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
from responses import get_response

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    user_message = data.get("message") if data else None
    if not user_message:
        return jsonify({"response": "Please type a message."}), 400

    try:
        response = get_response(user_message)
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"response": "Sorry, I cannot answer right now."}), 500

    return jsonify({"response": response})


def save_submission(data):
    try:
        submission_file = Path(__file__).resolve().parent / "submissions.json"
        if submission_file.exists():
            with open(submission_file, "r", encoding="utf-8") as f:
                submitted = json.load(f)
        else:
            submitted = []

        submitted.append(data)
        with open(submission_file, "w", encoding="utf-8") as f:
            json.dump(submitted, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Failed to save application submission:", e)


@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        education = request.form.get("education", "").strip()
        contact = request.form.get("contact", "").strip()

        if not name or not education or not contact:
            return render_template(
                "apply.html",
                success=False,
                error="Please fill in all fields before submitting.",
                name=name,
                education=education,
                contact=contact,
            )

        save_submission({
            "name": name,
            "education": education,
            "contact": contact,
            "timestamp": int(__import__("time").time()),
        })

        return render_template("apply.html", success=True, name=name)

    return render_template("apply.html", success=False)


if __name__ == "__main__":
    app.run(debug=False)
