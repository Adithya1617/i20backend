import asyncio
from flask import Flask, request, jsonify
from futurehouse_client import FutureHouseClient, JobNames
from flask_cors import CORS
import os
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

load_dotenv()
API_KEY = os.getenv("API_KEY")


# Reusable client instance
def get_client():
    return FutureHouseClient(api_key=API_KEY)


# Async task creator
async def create_task():
    client = get_client()
    task_data = {
        "name": JobNames.OWL,
        "query": "How many species of birds are there?"
    }
    task = await client.acreate_task(task_data)
    return task.task_id if hasattr(task, 'task_id') else task


# Async task fetcher
async def fetch_answer(task_id):
    client = get_client()
    task = await client.aget_task(task_id)
    return getattr(task, 'answer', None)


# Route: create new task
@app.route("/api/create-task", methods=["POST"])
def create_task_route():
    task_id = asyncio.run(create_task())
    return jsonify({"task_id": task_id})


# Route: fetch result for given task_id
@app.route("/api/get-answer", methods=["GET"])
def get_answer_route():
    task_id = request.args.get("task_id")
    if not task_id:
        return jsonify({"error": "task_id query param required"}), 400

    answer = asyncio.run(fetch_answer(task_id))
    if answer:
        return jsonify({"answer": answer})
    else:
        return jsonify({"status": "pending or not found"}), 202


if __name__ == "__main__":
    app.run(debug=True)
