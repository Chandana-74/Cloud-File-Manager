from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from botocore.config import Config
import os
import boto3

app = Flask(__name__)
app.secret_key = "cloudfilemanager123"
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
print("Region:", AWS_REGION)
print("Bucket:", AWS_BUCKET_NAME)

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "virtual"}
    )
)


@app.route("/")
def home():
    response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME)

    files = []

    if "Contents" in response:
        for obj in response["Contents"]:
            files.append(obj["Key"])

    return render_template(
    "index.html",
    files=files,
    total_files=len(files)
)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    print("Filename:", file.filename)

    try:
        s3.upload_fileobj(
            file,
            AWS_BUCKET_NAME,
            file.filename
        )

        flash(f"{file.filename} uploaded successfully to Amazon S3!")

    except Exception as e:
        print("Upload Error:", e)

    return redirect(url_for("home"))

@app.route("/download/<filename>")
def download(filename):
    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": AWS_BUCKET_NAME,
            "Key": filename
        },
        ExpiresIn=3600,
        HttpMethod="GET"
    )
    print(url)
    return redirect(url)

@app.route("/delete/<filename>")
def delete(filename):
    s3.delete_object(
        Bucket=AWS_BUCKET_NAME,
        Key=filename
    )

    flash(f"{filename} deleted successfully!")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)