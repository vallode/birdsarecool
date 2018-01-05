from flask import Flask, request, send_from_directory, render_template, redirect, jsonify, url_for, flash
from hurry.filesize import size, alternative
from werkzeug.utils import secure_filename
import random
import os
import os.path
import uuid
app = Flask(__name__)

image_extensions = set(['png', 'jpg'])
video_extensions = set(['mp4', 'webm'])
allowed_extensions = set.union(image_extensions, video_extensions)


def count_directory():
    directory = os.listdir("static/birds")
    count = len(directory)
    return count


def count_images():
    directory = os.listdir("static/birds")
    image_count = 0

    for file in directory:
        if file.split(".")[1] in image_extensions:
            image_count += 1
    return image_count


def count_videos():
    directory = os.listdir("static/birds")
    video_count = 0

    for file in directory:
        if file.split(".")[1] in video_extensions:
            video_count += 1
    return video_count


def return_directory_size():
    directory = os.listdir("static/birds")
    directory_size = 0

    for file in directory:
        pathname = os.path.join("static/birds", file)
        file_size = os.stat(pathname).st_size
        directory_size += file_size

    directory_size = size(directory_size, system=alternative)
    return directory_size


def random_bird():
    directory = os.listdir("static/birds")

    r = random.randrange(0, len(directory))
    return directory[r]


def allowed_file(filename):
    return "." in filename and filename.split(".")[-1].lower() in allowed_extensions


@app.route("/")
def index():
    image, video = False, False
    bird_count = count_directory()
    bird_image_count = count_images()
    bird_video_count = count_videos()
    storage_size = return_directory_size()

    current_bird = random_bird()
    bird_path = f"{request.url_root}{current_bird}"
    file_type = current_bird.split(".")[1]

    if file_type == "mp4":
        video = True
    else:
        image = True

    return render_template("index.html", **locals())


@app.route("/<path:path>", methods=['GET'])
def return_bird(path):
    return send_from_directory("static/birds", path.split("/")[-1])


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            print(request.files)
            message = "No file found"
            return render_template("upload.html", **locals())

        file = request.files["file"]

        if file.filename == "":
            print(file)
            message = "No file found"
            return render_template("upload.html", **locals())

        if file and allowed_file(file.filename):
            print(file)
            filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}.{filename.split('.')[-1]}"
            print(filename)

            file.save(os.path.join("review_birds/", filename))
            message = "File uploaded successfully!"
            return render_template("upload.html", **locals())

        return render_template("upload.html", **locals())
    if request.method == "GET":
        return render_template("upload.html", **locals())


@app.route("/bird.json")
def bird():
    bird_object = {
        'url': f"{request.url_root}{random_bird()}"
    }
    return jsonify(bird_object)


if __name__ == '__main__':
    app.run(debug=True)
