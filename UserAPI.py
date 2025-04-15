from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)
df = pd.read_excel("UserData.xlsx")
users_data = df.to_dict(orient="records")
@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(users_data)

if __name__ == "__main__":
    app.run(debug=True)
