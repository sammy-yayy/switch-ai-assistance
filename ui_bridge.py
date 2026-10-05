from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import urllib.request
import json

app = Flask(__name__)
CORS(app)

current_state = "idle"


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify({"state": current_state})


@app.route("/state", methods=["POST"])
def set_state():
    global current_state

    data = request.get_json(silent=True) or {}
    state = data.get("state")

    valid_states = [
        "idle",
        "listening",
        "thinking",
        "speaking",
        "sleeping",
        "exiting"
    ]

    if state in valid_states:

        # Do not allow the "Going to sleep" speech
        # to overwrite the sleeping state.
        if (
            current_state == "sleeping"
            and state == "speaking"
        ):
            return jsonify({
                "state": current_state
            })

        # Do not allow the goodbye speech
        # to overwrite the exiting state.
        if (
            current_state == "exiting"
            and state == "speaking"
        ):
            return jsonify({
                "state": current_state
            })

        current_state = state

    return jsonify({
        "state": current_state
    })


def start_ui_server():
    server_thread = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )

    server_thread.start()


def set_ui_state(state):
    try:
        data = json.dumps({
            "state": state
        }).encode("utf-8")

        request = urllib.request.Request(
            "http://127.0.0.1:5000/state",
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        urllib.request.urlopen(
            request,
            timeout=0.2
        )

    except Exception:
        pass