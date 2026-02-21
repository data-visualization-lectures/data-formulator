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
from flask import Flask, request, send_from_directory, redirect, url_for
from flask import stream_with_context, Response
import html
import pandas as pd

import webbrowser
import threading
from functools import wraps

from flask_cors import CORS
import jwt as pyjwt

import json
import time
from pathlib import Path

from vega_datasets import data as vega_data

from data_formulator.agents.agent_concept_derive import ConceptDeriveAgent
from data_formulator.agents.agent_data_transform_v2 import DataTransformationAgentV2
from data_formulator.agents.agent_data_rec import DataRecAgent

from data_formulator.agents.agent_sort_data import SortDataAgent
from data_formulator.agents.agent_data_load import DataLoadAgent
from data_formulator.agents.agent_data_clean import DataCleanAgent
from data_formulator.agents.agent_code_explanation import CodeExplanationAgent

from data_formulator.agents.client_utils import get_client

from dotenv import load_dotenv

APP_ROOT = Path(os.path.join(Path(__file__).parent)).absolute()

print(APP_ROOT)

# try to look for stored openAI keys information from the ROOT dir, 
# this file might be in one of the two locations
load_dotenv(os.path.join(APP_ROOT, "..", "..", 'openai-keys.env'))
load_dotenv(os.path.join(APP_ROOT, 'openai-keys.env'))

import os

app = Flask(__name__, static_url_path='', static_folder=os.path.join(APP_ROOT, "dist"))

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5000").split(",")
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

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

@app.route('/health')
def health_check():
    return flask.jsonify({'status': 'ok'}), 200

@app.route('/vega-datasets')
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

@app.route('/vega-dataset/<path:path>')
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

@app.route('/check-available-models', methods=['GET', 'POST'])
@require_auth
def check_available_models():

    results = []

    # dont need to check if it's empty
    if os.getenv("ENDPOINT") is None:
        return json.dumps(results)

    client = get_client(os.getenv("ENDPOINT"), "")
    models = [model.strip() for model in os.getenv("MODELS").split(',')]

    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Respond 'I can hear you.' if you can hear me. Do not say anything other than 'I can hear you.'"},
                ]
            )

            print(f"model: {model}")
            print(f"welcome message: {response.choices[0].message.content}")

            if "I can hear you." in response.choices[0].message.content:
                results.append({
                    "endpoint": "default",
                    "key": "",
                    "model": model
                })
        except:
            pass

    return json.dumps(results)

@app.route('/test-model', methods=['GET', 'POST'])
@require_auth
def test_model():
    
    if request.is_json:
        app.logger.info("# code query: ")
        content = request.get_json()
        endpoint = html.escape(content['endpoint'].strip())
        key = html.escape(f"{content['key']}".strip())

        print(content)

        client = get_client(endpoint, key)
        model = html.escape(content['model'].strip())

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Respond 'I can hear you.' if you can hear me. Do not say anything other than 'I can hear you.'"},
                ]
            )

            print(f"model: {model}")
            print(f"welcome message: {response.choices[0].message.content}")

            if "I can hear you." in response.choices[0].message.content:
                result = {
                    "endpoint": endpoint,
                    "key": key,
                    "model": model,
                    "status": 'ok',
                    "message": ""
                }
        except Exception as e:
            print(f"Error: {e}")
            error_message = str(e)
            result = {
                "endpoint": endpoint,
                "key": key,
                "model": model,
                "status": 'error',
                "message": error_message,
            }
    else:
        {'status': 'error'}
    
    return json.dumps(result)

@app.route("/", defaults={"path": ""})
def index_alt(path):
    print(app.static_folder)
    return send_from_directory(app.static_folder, "index.html")

@app.errorhandler(404)
def page_not_found(e):
    # your processing here
    print(app.static_folder)
    return send_from_directory(app.static_folder, "index.html") #'Hello 404!' #send_from_directory(app.static_folder, "index.html")

###### test functions ######

@app.route('/hello')
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


@app.route('/hello-stream')
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


###### agent related functions ######

@app.route('/process-data-on-load', methods=['GET', 'POST'])
@require_auth
def process_data_on_load_request():

    if request.is_json:
        app.logger.info("# process data query: ")
        content = request.get_json()
        token = content["token"]

        client = get_client(content['model']['endpoint'], content['model']['key'])
        model = content['model']['model']
        app.logger.info(f" model: {content['model']}")
        
        agent = DataLoadAgent(client=client, model=model)
        candidates = agent.run(content["input_data"])
        
        candidates = [c['content'] for c in candidates if c['status'] == 'ok']

        response = flask.jsonify({ "status": "ok", "token": token, "result": candidates })
    else:
        response = flask.jsonify({ "token": -1, "status": "error", "result": [] })

    return response


@app.route('/derive-concept-request', methods=['GET', 'POST'])
@require_auth
def derive_concept_request():

    if request.is_json:
        app.logger.info("# code query: ")
        content = request.get_json()
        token = content["token"]

        client = get_client(content['model']['endpoint'], content['model']['key'])
        model = content['model']['model']
        app.logger.info(f" model: {content['model']}")
        
        agent = ConceptDeriveAgent(client=client, model=model)

        #print(content["input_data"])

        candidates = agent.run(content["input_data"], [f['name'] for f in content["input_fields"]], 
                                       content["output_name"], content["description"])
        
        candidates = [c['code'] for c in candidates if c['status'] == 'ok']

        response = flask.jsonify({ "status": "ok", "token": token, "result": candidates })
    else:
        response = flask.jsonify({ "token": -1, "status": "error", "result": [] })

    return response


@app.route('/clean-data', methods=['GET', 'POST'])
@require_auth
def clean_data_request():

    if request.is_json:
        app.logger.info("# data clean request")
        content = request.get_json()
        token = content["token"]

        client = get_client(content['model']['endpoint'], content['model']['key'])
        model = content['model']['model']

        app.logger.info(f" model: {content['model']}")
        
        agent = DataCleanAgent(client=client, model=model)

        candidates = agent.run(content['content_type'], content["raw_data"], content["image_cleaning_instruction"])
        
        candidates = [c for c in candidates if c['status'] == 'ok']

        response = flask.jsonify({ "status": "ok", "token": token, "result": candidates })
    else:
        response = flask.jsonify({ "token": -1, "status": "error", "result": [] })

    return response


@app.route('/codex-sort-request', methods=['GET', 'POST'])
@require_auth
def sort_data_request():

    if request.is_json:
        app.logger.info("# sort query: ")
        content = request.get_json()
        token = content["token"]

        client = get_client(content['model']['endpoint'], content['model']['key'])
        model = content['model']['model']
        app.logger.info(f" model: {content['model']}")

        agent = SortDataAgent(client=client, model=model)
        candidates = agent.run(content['field'], content['items'])

        #candidates, dialog = limbo_concept.call_codex_sort(content["items"], content["field"])
        candidates = candidates if candidates != None else []
        response = flask.jsonify({ "status": "ok", "token": token, "result": candidates })
    else:
        response = flask.jsonify({ "token": -1, "status": "error", "result": [] })

    return response


@app.route('/derive-data', methods=['GET', 'POST'])
@require_auth
def derive_data():

    if request.is_json:
        app.logger.info("# request data: ")
        content = request.get_json()        
        token = content["token"]

        client = get_client(content['model']['endpoint'], content['model']['key'])
        model = content['model']['model']
        app.logger.info(f" model: {content['model']}")

        # each table is a dict with {"name": xxx, "rows": [...]}
        input_tables = content["input_tables"]
        new_fields = content["new_fields"]
        instruction = content["extra_prompt"]

        print("spec------------------------------")
        print(new_fields)
        print(instruction)

        mode = "transform"
        if len(new_fields) == 0:
            mode = "recommendation"

        if mode == "recommendation":
            # now it's in recommendation mode
            agent = DataRecAgent(client, model)
            results = agent.run(input_tables, instruction)
        else:
            agent = DataTransformationAgentV2(client=client, model=model)
            results = agent.run(input_tables, instruction, [field['name'] for field in new_fields])

        repair_attempts = 0
        while results[0]['status'] == 'error' and repair_attempts == 0: # only try once
            error_message = results[0]['content']
            new_instruction = f"We run into the following problem executing the code, please fix it:\n\n{error_message}\n\nPlease think step by step, reflect why the error happens and fix the code so that no more errors would occur."

            prev_dialog = results[0]['dialog']

            if mode == "transform":
                results = agent.followup(input_tables, prev_dialog, [field['name'] for field in new_fields], new_instruction)
            if mode == "recommendation":
                results = agent.followup(input_tables, prev_dialog, new_instruction)

            repair_attempts += 1
        
        response = flask.jsonify({ "token": token, "status": "ok", "results": results })
    else:
        response = flask.jsonify({ "token": "", "status": "error", "results": [] })

    return response

@app.route('/refine-data', methods=['GET', 'POST'])
@require_auth
def refine_data():

    if request.is_json:
        app.logger.info("# request data: ")
        content = request.get_json()        
        token = content["token"]

        client = get_client(content['model']['endpoint'], content['model']['key'])
        model = content['model']['model']
        app.logger.info(f" model: {content['model']}")

        # each table is a dict with {"name": xxx, "rows": [...]}
        input_tables = content["input_tables"]
        output_fields = content["output_fields"]
        dialog = content["dialog"]
        new_instruction = content["new_instruction"]
        
        print("previous dialog")
        print(dialog)

        # always resort to the data transform agent       
        agent = DataTransformationAgentV2(client, model=model)
        results = agent.followup(input_tables, dialog, [field['name'] for field in output_fields], new_instruction)

        repair_attempts = 0
        while results[0]['status'] == 'error' and repair_attempts == 0: # only try once
            error_message = results[0]['content']
            new_instruction = f"We run into the following problem executing the code, please fix it:\n\n{error_message}\n\nPlease think step by step, reflect why the error happens and fix the code so that no more errors would occur."
            prev_dialog = results[0]['dialog']

            results = agent.followup(input_tables, prev_dialog, [field['name'] for field in output_fields], new_instruction)
            repair_attempts += 1

        response = flask.jsonify({ "token": token, "status": "ok", "results": results})
    else:
        response = flask.jsonify({ "token": "", "status": "error", "results": []})

    return response

@app.route('/code-expl', methods=['GET', 'POST'])
@require_auth
def request_code_expl():
    if request.is_json:
        app.logger.info("# request data: ")
        content = request.get_json()        
        token = content["token"]

        client = get_client(content['model']['endpoint'], content['model']['key'])
        model = content['model']['model']
        app.logger.info(f" model: {content['model']}")

        # each table is a dict with {"name": xxx, "rows": [...]}
        input_tables = content["input_tables"]
        code = content["code"]
        
        code_expl_agent = CodeExplanationAgent(client=client, model=model)
        expl = code_expl_agent.run(input_tables, code)
    else:
        expl = ""
    return expl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Data Formulator")
    parser.add_argument("-p", "--port", type=int, default=5000, help="The port number you want to use")
    return parser.parse_args()


def run_app():
    args = parse_args()
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
