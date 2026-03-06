from flask import Flask, render_template, send_file
import requests
import csv
import io

app = Flask(__name__)

CHANNEL1_ID = "3271158"
CHANNEL2_ID = "3273029"
CHANNEL3_ID = "3285406"

READ_API_KEY_1 = "BUYHL98SRGZD2OK4"
READ_API_KEY_2 = "2DLTEU46Z7R2KXIS"
READ_API_KEY_3 = "S1TBFQP66JVMJGSF"


def get_last_hour(channel_id, read_key):
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}&results=60"
    response = requests.get(url)
    data = response.json()
    return data["feeds"]


@app.route("/")
def dashboard():

    electrical = get_last_hour(CHANNEL1_ID, READ_API_KEY_1)
    mechanical = get_last_hour(CHANNEL2_ID, READ_API_KEY_2)
    analytics = get_last_hour(CHANNEL3_ID, READ_API_KEY_3)

    return render_template(
        "index.html",
        electrical=electrical,
        mechanical=mechanical,
        analytics=analytics
    )


@app.route("/download")
def download_csv():

    analytics = get_last_hour(CHANNEL3_ID, READ_API_KEY_3)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Time", "Health", "RUL", "OEE", "Severity"])

    for row in analytics:
        writer.writerow([
            row["created_at"],
            row.get("field1"),
            row.get("field2"),
            row.get("field5"),
            row.get("field8")
        ])

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="last_1_hour_data.csv"
    )


if __name__ == "__main__":
    app.run(debug=True)
