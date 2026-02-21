# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import argparse
import random
import sys
import os
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')

import flask
from flask import Flask, request, send_from_directory, session
from flask import stream_with_context, Response

import webbrowser
import threading
from functools import wraps
import numpy as np
import datetime
import time

import logging
from flask_cors import CORS
import jwt as pyjwt

import json
from pathlib import Path

from vega_datasets import data as vega_data

from dotenv import load_dotenv
import secrets
import base64

APP_ROOT = Path(os.path.join(Path(__file__).parent)).absolute()

import os

# blueprints
from data_formulator.tables_routes import tables_bp
from data_formulator.agent_routes import agent_bp

app = Flask(__name__, static_url_path='', static_folder=os.path.join(APP_ROOT, "dist"))
app.secret_key = secrets.token_hex(16)  # Generate a random secret key for sessions

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        if isinstance(obj, (bytes, bytearray)):
            return base64.b64encode(obj).decode('ascii')
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Load env files early
load_dotenv(os.path.join(APP_ROOT, "..", "..", 'api-keys.env'))
load_dotenv(os.path.join(APP_ROOT, 'api-keys.env'))
load_dotenv(os.path.join(APP_ROOT, '.env'))

# Add this line to store args at app level
app.config['CLI_ARGS'] = {
    'exec_python_in_subprocess': os.environ.get('EXEC_PYTHON_IN_SUBPROCESS', 'false').lower() == 'true',
    'disable_display_keys': os.environ.get('DISABLE_DISPLAY_KEYS', 'false').lower() == 'true'
}

# CORS setup
# When ALLOWED_ORIGINS is not set (e.g., Vercel+Railway deployment),
# allow all origins so the frontend can call the API cross-origin.
# When ALLOWED_ORIGINS is explicitly set, restrict to those origins and
# enable credentials (cookies) for session support.
_ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "")
if _ALLOWED_ORIGINS_ENV:
    CORS(app, origins=_ALLOWED_ORIGINS_ENV.split(","), supports_credentials=True)
else:
    CORS(app, origins="*")

# Supabase JWT auth
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not SUPABASE_JWT_SECRET:  # ローカル開発時はスキップ
            return f(*args, **kwargs)
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return flask.jsonify({'error': 'Missing token'}), 401
        try:
            pyjwt.decode(auth.split(' ', 1)[1], SUPABASE_JWT_SECRET,
                         algorithms=["HS256"], options={"verify_aud": False})
        except pyjwt.InvalidTokenError as e:
            return flask.jsonify({'error': str(e)}), 401
        return f(*args, **kwargs)
    return decorated

# register blueprints
app.register_blueprint(tables_bp)
app.register_blueprint(agent_bp)

print(APP_ROOT)

# Configure root logger for general application logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Get logger for this module
logger = logging.getLogger(__name__)

# Configure Flask app logger to use the same settings
app.logger.handlers = []
for handler in logging.getLogger().handlers:
    app.logger.addHandler(handler)

# Example usage:
logger.info("Application level log")  # General application logging
app.logger.info("Flask specific log") # Web request related logging

@app.route('/health')
def health_check():
    return flask.jsonify({'status': 'ok'}), 200

@app.route('/api/vega-datasets')
@require_auth
def get_example_dataset_list():
    dataset_names = vega_data.list_datasets()
    example_datasets = [
        {"name": "gapminder", "challenges": [
            {
                "text": "各国の平均寿命（the life expectancy）の推移を時系列の折れ線グラフで作成してください。",
                "difficulty": "easy"
            },
            {
                "text": "2005年の平均寿命（the life expectancy）が最も高い上位10か国を可視化してください。",
                "difficulty": "medium"
            },
            {
                "text": "1955年と2005年の平均寿命（the life expectancy）の差が最も大きい上位10か国を見つけてください。",
                "difficulty": "hard"
            },
            {
                "text": "各国の10年ごとの平均人口をランキングし、2005年に人口が5000万人以上の国のみを表示してください。",
                "difficulty": "hard"
            }
        ]},
        {"name": "income", "challenges": [
            {
                "text": "各州の所得の推移を時系列の折れ線グラフで作成してください。",
                "difficulty": "easy"
            },
            {
                "text": "ワシントン州とカリフォルニア州の各年の所得グループごとの人口割合のみを表示してください。",
                "difficulty": "medium"
            },
            {
                "text": "2016年に高所得グループの割合が最も高い上位5州を見つけてください。",
                "difficulty": "hard"
            }
        ]},
        {"name": "disasters", "challenges": [
            {
                "text": "各年の災害タイプごとの死亡者数を示す散布図を作成してください。",
                "difficulty": "easy"
            },
            {
                "text": "データをフィルタリングし、洪水または干ばつによる年間死亡者数のみを表示してください。",
                "difficulty": "easy"
            },
            {
                "text": "各災害タイプごとの10年ごとの総死亡者数を示すヒートマップを作成してください。",
                "difficulty": "hard"
            },
            {
                "text": "前のヒートマップから「全自然災害」のカテゴリを除外してください。",
                "difficulty": "medium"
            }
        ]},
        {"name": "movies", "challenges": [
            {
                "text": "予算と世界興行収入の関係を示す散布図を作成してください。",
                "difficulty": "easy"
            },
            {
                "text": "2000年以降で最も利益が高い上位10本の映画を見つけ、棒グラフで視覚化してください。",
                "difficulty": "easy"
            },
            {
                "text": "各ジャンルの映画の中央値の利益率を視覚化してください。",
                "difficulty": "medium"
            },
            {
                "text": "利益とIMDB評価の関係を示す散布図を作成してください。",
                "difficulty": "medium"
            },
            {
                "text": "上記の散布図をヒートマップに変換し、IMDB評価と利益を区間ごとに分類し、各区間の映画の本数を色で表してください。",
                "difficulty": "hard"
            }
        ]},
        {"name": "unemployment-across-industries", "challenges": [
            {
                "text": "失業率と年の関係を示す散布図を作成してください。",
                "difficulty": "easy"
            },
            {
                "text": "各業界の年間平均失業率を示す折れ線グラフを作成してください。",
                "difficulty": "medium"
            },
            {
                "text": "2000年から2010年の間で失業率の変動が最も少ない5つの安定した業界を見つけ、それらの推移を折れ線グラフで視覚化してください。",
                "difficulty": "medium"
            },
            {
                "text": "2000年から2010年の失業率の変化を示す棒グラフを作成し、変動が最も少ない5つの安定した業界を強調表示してください。",
                "difficulty": "hard"
            }
        ]}
    ]
    dataset_info = []
    print(dataset_names)
    for dataset in example_datasets:
        name = dataset["name"]
        challenges = dataset["challenges"]
        try:
            info_obj = {'name': name, 'challenges': challenges, 'snapshot': vega_data(name).to_json(orient='records')}
            dataset_info.append(info_obj)
        except:
            pass

    return flask.jsonify(dataset_info)

@app.route('/api/vega-dataset/<path:path>')
@require_auth
def get_datasets(path):
    try:
        df = vega_data(path)
        # to_json is necessary for handle NaN issues
        data_object = df.to_json(None, 'records')
    except Exception as err:
        print(path)
        print(err)
        data_object = "[]"
    response = data_object
    return response

@app.route("/", defaults={"path": ""})
def index_alt(path):
    logger.info(app.static_folder)
    return send_from_directory(app.static_folder, "index.html")

@app.errorhandler(404)
def page_not_found(e):
    # your processing here
    logger.info(app.static_folder)
    return send_from_directory(app.static_folder, "index.html") #'Hello 404!' #send_from_directory(app.static_folder, "index.html")

###### test functions ######

@app.route('/api/hello')
def hello():
    values = [
            {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43},
            {"a": "D", "b": 91}, {"a": "E", "b": 81}, {"a": "F", "b": 53},
            {"a": "G", "b": 19}, {"a": "H", "b": 87}, {"a": "I", "b": 52}
        ]
    spec =  {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "A simple bar chart with embedded data.",
        "data": { "values": values },
        "mark": "bar",
        "encoding": {
            "x": {"field": "a", "type": "nominal", "axis": {"labelAngle": 0}},
            "y": {"field": "b", "type": "quantitative"}
        }
    }
    return json.dumps(spec)


@app.route('/api/hello-stream')
def streamed_response():
    def generate():
        values = [
            {"a": "A", "b": 28}, {"a": "B", "b": 55}, {"a": "C", "b": 43},
            {"a": "D", "b": 91}, {"a": "E", "b": 81}, {"a": "F", "b": 53},
            {"a": "G", "b": 19}, {"a": "H", "b": 87}, {"a": "I", "b": 52}
        ]
        spec =  {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "A simple bar chart with embedded data.",
            "data": { "values": [] },
            "mark": "bar",
            "encoding": {
                "x": {"field": "a", "type": "nominal", "axis": {"labelAngle": 0}},
                "y": {"field": "b", "type": "quantitative"}
            }
        }
        for i in range(3):
            time.sleep(3)
            spec["data"]["values"] = values[i:]
            yield json.dumps(spec)
    return Response(stream_with_context(generate()))

@app.route('/api/get-session-id', methods=['GET', 'POST'])
def get_session_id():
    """Endpoint to get or confirm a session ID from the client"""
    # if it is a POST request, we expect a session_id in the body
    # if it is a GET request, we do not expect a session_id in the query params

    current_session_id = None
    if request.is_json:
        content = request.get_json()
        current_session_id = content.get("session_id", None)

    # Create session if it doesn't exist
    if current_session_id is None:
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)
            session.permanent = True
            logger.info(f"Created new session: {session['session_id']}")
    else:
        # override the session_id
        session['session_id'] = current_session_id
        session.permanent = True

    return flask.jsonify({
        "status": "ok",
        "session_id": session['session_id']
    })

@app.route('/api/app-config', methods=['GET'])
def get_app_config():
    """Provide frontend configuration settings from CLI arguments"""
    args = app.config['CLI_ARGS']
    config = {
        "EXEC_PYTHON_IN_SUBPROCESS": args['exec_python_in_subprocess'],
        "DISABLE_DISPLAY_KEYS": args['disable_display_keys'],
        "SESSION_ID": session.get('session_id', None)
    }
    return flask.jsonify(config)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Data Formulator")
    parser.add_argument("-p", "--port", type=int, default=5000, help="The port number you want to use")
    parser.add_argument("-e", "--exec-python-in-subprocess", action='store_true', default=False,
        help="Whether to execute python in subprocess, it makes the app more secure (reducing the chance for the model to access the local machine), but increases the time of response")
    parser.add_argument("-d", "--disable-display-keys", action='store_true', default=False,
        help="Whether disable displaying keys in the frontend UI, recommended to turn on if you host the app not just for yourself.")
    return parser.parse_args()


def run_app():
    args = parse_args()
    # Override CLI args from actual args
    app.config['CLI_ARGS'] = {
        'exec_python_in_subprocess': args.exec_python_in_subprocess,
        'disable_display_keys': args.disable_display_keys
    }
    port = args.port or int(os.getenv("PORT", 5000))
    is_cloud = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT")
    if not is_cloud:
        url = "http://localhost:{0}".format(port)
        threading.Timer(2, lambda: webbrowser.open(url, new=2)).start()
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=port, threaded=True, debug=debug)

if __name__ == '__main__':
    #app.run(debug=True, host='127.0.0.1', port=5000)
    #use 0.0.0.0 for public
    run_app()
