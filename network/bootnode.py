from flask import Flask, request, jsonify
import time

app = Flask(__name__)

nodes = {}
TIMEOUT = 60

def cleanup():
    now = time.time()
    expired = [key for key, item in nodes.items() if now - item["last"] > TIMEOUT]
    for key in expired:
        del nodes[key]

#it will reutrn {"nodes": [ {"ip" : "xxxx", "port" : "xxx", "last" : "xxxx"} ]}
@app.route("/register", methods = ["POST"])
def register():
    cleanup()

    data = request.json
    ip = data["ip"]
    port = data["port"]

    key = f"{ip}:{port}" #becuase there may be serval connection which using the same IP but different port (local demo), we have to make a new key

    nodes[key] = {"ip" : ip, "port" : port, "last" : time.time()}

    other_nodes = [item for k, item in nodes.items() if k != key]

    node_list = []
    for node in other_nodes:
        info = {
            "ip" : node["ip"],
            "port" : node["port"]
        }
        node_list.append(info)

    response = {
        "nodes" : node_list
    }

    return jsonify(response)

@app.route("/report", methods = ["POST"])
def report():
    data = request.json
    ip = data["ip"]
    port = data["port"]
    key = f"{ip}:{port}"

    if key in nodes:
        nodes[key]["last"] = time.time()
    return jsonify({"ok" : True})

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 9000)