from flask import Flask, abort, request, send_from_directory, render_template, redirect, jsonify, url_for, flash
from hurry.filesize import size, alternative
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from secret import SECRET
import random
import os
import os.path
import uuid
app = Flask(__name__)
bcrypt = Bcrypt(app)

image_extensions = set(['png', 'jpg'])
video_extensions = set(['mp4', 'webm'])
allowed_extensions = set.union(image_extensions, video_extensions)


def count_directory(directory):
    count = len(directory)
    return count


def count_images():
    birds_folder = os.listdir("static/birds")
    image_count = 0

    for file in birds_folder:
        if file.split(".")[1] in image_extensions:
            image_count += 1
    return image_count


def count_videos():
    birds_folder = os.listdir("static/birds")
    video_count = 0

    for file in birds_folder:
        if file.split(".")[1] in video_extensions:
            video_count += 1
    return video_count


def return_directory_size():
    birds_folder = os.listdir("static/birds")
    directory_size = 0

    for file in birds_folder:
        pathname = os.path.join("static/birds", file)
        file_size = os.stat(pathname).st_size
        directory_size += file_size

    directory_size = size(directory_size, system=alternative)
    return directory_size


def stats():
    birds_folder = os.listdir("static/birds")
    birds_review_folder = os.listdir("review_birds")

    options = dict()
    video = False
    video_review = False
    bird_image_count = 0
    bird_video_count = 0

    bird_count = count_directory(birds_folder)
    if bird_count:
        bird_image_count = count_images()
        bird_video_count = count_videos()

        current_bird = random_bird(birds_folder)
        bird_path = f"{request.url_root}{current_bird}"
        file_type = current_bird.split(".")[1]

        if file_type in video_extensions:
            video = True

    bird_review_count = count_directory(birds_review_folder)
    if bird_review_count:
        review_bird = random_bird(birds_review_folder)
        bird_review_path = f"{request.url_root}review_birds/{review_bird}"
        file_type_review = review_bird.split(".")[1]

        if file_type_review in video_extensions:
            video_review = True

    storage_size = return_directory_size()
    print(storage_size)

    options.update(**locals())
    return options


def random_bird(directory):
    r = random.randrange(0, len(directory))
    return directory[r]


def allowed_file(filename):
    return "." in filename and filename.split(".")[-1].lower() in allowed_extensions


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/", methods=["GET", "POST"])
def index():
    options = stats()

    return render_template("index.html", **locals())


@app.route("/<path:path>", methods=['GET'])
def return_bird(path):
    return send_from_directory("static/birds", path.split("/")[-1])


@app.route("/review_birds/<path:path>", methods=['GET'])
def return_review_bird(path):
    return send_from_directory("review_birds/", path.split("/")[-1])


@app.route("/upload", methods=["GET", "POST"])
def upload():
    options = stats()
    if request.method == "POST":
        if "file" not in request.files:
            message = "No file found"
            return render_template("upload.html", **locals())

        file = request.files["file"]

        if file.filename == "":
            message = "No file found"
            return render_template("upload.html", **locals())

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4()}.{filename.split('.')[-1]}"

            file.save(os.path.join("review_birds/", filename))
            options.update({"bird_review_count": count_directory(os.listdir("review_birds"))})
            message = "File uploaded successfully!"
            return render_template("upload.html", **locals())

        return render_template("upload.html", **locals())
    if request.method == "GET":
        return render_template("upload.html", **locals())


@app.route("/review", methods=["GET", "POST"])
def review():
    options = stats()

    if request.args.get('seed') and bcrypt.check_password_hash(SECRET, request.args.get('seed')):
        print('Auth successful!')
        print(f'Logged from: {request.remote_addr}')
    else:
        print('Auth failed...')
        print(f'Logged from: {request.remote_addr}')
        return redirect(url_for("index"))

    if request.method == "POST":
        if "House" in request.form:
            image = request.form["House"]
            image_name = image.split("/")[-1]

            os.rename(f"review_birds/{image_name}", f"static/birds/{image_name}")

            options.update({"bird_review_count": count_directory(os.listdir("review_birds"))})
            print(f"Housed bird {image_name}!")

        if "Remove" in request.form:
            image = request.form["Remove"]
            image_name = image.split("/")[-1]

            os.remove(f"review_birds/{image_name}")

            options.update({"bird_review_count": count_directory(os.listdir("review_birds"))})
            print(f"Removed bad bird {image_name}!")

        return render_template("review.html", **locals())

    if request.method == "GET":
        return render_template("review.html", **locals())

    return redirect(url_for("index"))


@app.route("/bird.json")
def bird():
    birds_folder = os.listdir("static/birds")
    try:
        bird_object = {
            'url': f"{request.url_root}{random_bird(birds_folder)}"
        }
        return jsonify(bird_object)
    except ValueError:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True)
