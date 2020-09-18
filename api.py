import json

import pika
from flask import Flask, request, jsonify
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

import utils

app = Flask(__name__)
# if development:
#     app.secret_key = b'0'
# else:
#     app.secret_key = urandom(12)

client = MongoClient("mongodb://localhost:27017")
db = client["cdn"]

# Collections
zones = db["zones"]
zones.create_index([("zone", ASCENDING)], unique=True)

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue="cdn_updates")


def add_queue_message(operation, args):
    channel.basic_publish(exchange="", routing_key="cdn_updates", body=json.dumps({"operation": operation, "args": args}))


def get_args(*args):
    payload = []

    for arg in args:
        try:
            arg_val = request.json[arg]
        except KeyError:
            raise ValueError("required argument \"" + str(arg) + "\" not supplied.")
        else:
            payload.append(arg_val)

    if len(payload) == 1:
        return payload[0]
    else:
        return tuple(payload)


@app.route("/zones/add", methods=["POST"])
def zones_add():
    try:
        zone = get_args("zone")
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)})

    try:
        zones.insert_one({
            "zone": zone,
            "records": [],
            "serial": utils.get_current_serial()
        })
    except DuplicateKeyError:
        return jsonify({"success": False, "message": "Zone already exists"})
    else:
        add_queue_message("refresh_zones", args=None)
        add_queue_message("refresh_single_zone", {"zone": zone})

        return jsonify({"success": True, "message": "Added " + zone})


@app.route("/zones/delete", methods=["POST"])
def zones_delete():
    try:
        zone = get_args("zone")
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)})

    delete_op = zones.delete_one({"zone": zone})

    if delete_op.deleted_count > 0:
        add_queue_message("refresh_zones", args=None)
        return jsonify({"success": True, "message": "Deleted " + zone})
    else:
        return jsonify({"success": True, "message": "Zone " + zone + " doesn't exist"})


# Record management

@app.route("/records/add", methods=["POST"])
def records_add():
    try:
        zone, record_domain, record_ttl, record_type, record_value = get_args("zone", "domain", "ttl", "type", "value")
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)})

    zones.update_one({"zone": zone}, {"$push": {"records": {
        "domain": record_domain,
        "ttl": record_ttl,
        "type": record_type,
        "value": record_value
    }}})

    zones.update_one({"zone": zone}, {"$set": {"serial": utils.get_current_serial()}})

    add_queue_message("refresh_single_zone", {"zone": zone})

    return jsonify({"success": True, "message": "Added " + record_domain + " to " + zone})


@app.route("/records/delete", methods=["POST"])
def record_delete():
    try:
        zone, record_index = get_args("zone", "record_index")
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)})

    current_records = zones.find_one({"zone": zone})["records"]

    # Remove the record
    try:
        current_records.pop(int(record_index))
    except IndexError:
        return jsonify({"success": True, "message": "Record at index " + str(record_index) + " doesn't exist in " + zone})

    # Set the modified records
    zones.update_one({"zone": zone}, {"$set": {
        "records": current_records,
        "serial": utils.get_current_serial()
    }})

    add_queue_message("refresh_single_zone", {"zone": zone})

    return jsonify({"success": True, "message": "Deleted record index " + str(record_index) + " from " + zone})


@app.route("/debug/refresh_zones")
def refresh_zones():
    add_queue_message("refresh_zones", args=None)
    return "0"


@app.route("/debug/refresh_single_zone/<zone>")
def refresh_single_zone(zone):
    add_queue_message("refresh_single_zone", {"zone": zone})
    return "0"


if __name__ == "__main__":
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        connection.close()