#
# Author:  Dlo Bagari
# created Date: 13-11-2019
import json
from flask import Flask, request, jsonify
from user_lib.logger import Logger
from user_lib.entity import Entity
from user_lib.const_values import ConstValues
from microsoft_graph.user_api import UserApi
from microsoft_graph.group_api import GroupApi
from user_lib.access_token import AccessToken
from user_lib.const_values import ConstValues

logger = Logger()
entity = Entity()
access_token = AccessToken()
user_api = UserApi(access_token, logger)
group_api = GroupApi(access_token, logger)
app = Flask(__name__)


@app.route("/user/<user_id>/groups")
def get_users_groups(user_id):
    error_code, groups = user_api.get_user_groups(user_id)
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", groups["message"])
        return jsonify({"error": groups["message"]}), 400
    else:
        return jsonify(groups), 200


@app.route("/user")
def get_user():
    error_code, users = user_api.get_user()
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", users["message"])
        return jsonify({"error": users}), 400
    else:
        return jsonify(users), 200


@app.route("/groups")
def get_groups():
    error_code, response = group_api.get_groups()
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", response["message"])
        return jsonify({"error": response}), 400
    else:
        return jsonify(response), 200



@app.route("/user/<user_id>")
def get_user_by_id(user_id):
    error_code, users = user_api.get_user(user_id)
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", users["message"])
        return jsonify({"error": users}), 400
    else:
        return jsonify(users), 200

# used
@app.route("/user/filter")
def filter_user():
    first_name = request.args.get("first_name", None)
    last_name = request.args.get("last_name", None)
    error_code, user = user_api.find_user_by_name(first_name, last_name)
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", user["message"])
        return jsonify({"error": user}), 400
    else:
        return jsonify(user), 200

# used
@app.route("/group/filter")
def filter_group_by_name():
    name = request.args.get("name", None)
    if name is None:
        return jsonify({"error": "missing parameter name"}), 400
    error_code, group = group_api.filter_group_by_name(name)
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", group["message"])
        return jsonify({"error": group["message"]}), 400
    else:
        return jsonify(group), 200


@app.route("/group/change", methods=["POST"])
def change_group():
    user_id = request.args.get("user_id")
    if user_id is None:
        return jsonify({"error": "missing parameter user_id"}), 400
    group_name = request.args.get("group_name")
    if group_name is None:
        return jsonify({"error": "missing parameter group_name"}), 400
    error_code, response = group_api.change_group(user_id, group_name)
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", response["message"])
        return jsonify({"error": response["message"]}), 400
    else:
        return jsonify(response), 200

@app.route("/groups/<group_id>/members")
def get_group_members(group_id):
    error_code, users = group_api.get_group_members(group_id)
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", users["message"])
        return jsonify({"error": users["message"]}), 400
    else:
        return jsonify(users), 200


@app.route("/groups/<group_id>/add/<user_id>")
def add_member(group_id, user_id):
    error_code, response = group_api.add_member(group_id, user_id)
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", response["message"])
        return jsonify({"error": response["message"]}), 400
    else:
        return jsonify(response), 200


@app.route("/groups/<group_id>/remove/<user_id>")
def remove_member(group_id, user_id):
    error_code, response = group_api.remove_member(group_id, user_id)
    if error_code != ConstValues.ERROR_CODE_ZERO:
        logger.error("API_REQUEST", response["message"])
        return jsonify({"error": response["message"]}), 400
    else:
        return jsonify(response), 200


# TODO: in process
@app.route("/entity", methods=["POST"])
def handle_entity():
    data = request.json
    error_code, result, entity_id = entity.handle_notification(data)
    if error_code == ConstValues.ERROR_CODE_ZERO and result is True:
        return jsonify({"entity_id": entity_id}), 201
    else:
        return jsonify({"error": "Failed in handling the request"}), 400

