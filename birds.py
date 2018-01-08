from flask import Flask, abort, request, make_response, send_from_directory, render_template, redirect, jsonify, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from hurry.filesize import size, alternative
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from secret import SECRET, TINY
import random
import os
import os.path
import uuid
from threading import Thread
from tinypng import api

app = Flask(__name__)
bcrypt = Bcrypt(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["4000 per day", "150 per hour"]
)

image_extensions = {'png', 'jpg', 'jpeg'}
video_extensions = {'mp4', 'webm', 'gif'}
allowed_extensions = set.union(image_extensions, video_extensions)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['USE_X_SENDFILE'] = True


def count_directory(path):
    directory = os.listdir(path)
    count = len(directory)

    return count


def count_file_type(path, extension):
    birds_folder = os.listdir(path)
    count = 0

    for file in birds_folder:
        if file.split(".")[1] in extension:
            count += 1

    return count


def count_directory_size(path):
    folder = os.listdir(path)
    folder_size = 0

    for file in folder:
        pathname = os.path.join("static/birds", file)
        folder_size += os.stat(pathname).st_size

    folder_size = size(folder_size, system=alternative)

    return folder_size


def random_bird(directory, file_types=None, exclude_types=None):
    applicable = []

    if not file_types:
        file_types = allowed_extensions
    if not exclude_types:
        exclude_types = []

    for file in directory:
        if file.split(".")[-1] not in exclude_types and file.split(".")[-1] in file_types:
            applicable.append(file)

    r = random.randrange(0, len(applicable))
    return applicable[r]


def allowed_file(filename):
    return "." in filename and filename.split(".")[-1].lower() in allowed_extensions


def shrink_file(file):
    api.shrink_file(file, api_key=TINY, out_filepath=file)


def stats():
    options = dict()
    birds_folder = os.listdir("static/birds")
    birds_review_folder = os.listdir("review_birds")

    video = False
    video_review = False
    bird_image_count = 0
    bird_video_count = 0

    bird_count = count_directory("static/birds")
    if bird_count:
        bird_image_count = count_file_type("static/birds", image_extensions)
        bird_video_count = count_file_type("static/birds", video_extensions)

        current_bird = random_bird(birds_folder)
        bird_path = f"{request.url_root}{current_bird}"
        file_type = current_bird.split(".")[1]

        if file_type.lower() in video_extensions:
            video = True

    bird_review_count = count_directory("review_birds")
    if bird_review_count:
        review_bird = random_bird(birds_review_folder)
        bird_review_path = f"{request.url_root}review_birds/{review_bird}"
        file_type_review = review_bird.split(".")[1]

        if file_type_review.lower() in video_extensions:
            video_review = True

    storage_size = count_directory_size("static/birds")

    options.update(**locals())

    return options


@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, we could not find any birds for you!', 404


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route("/", methods=["GET", "POST"])
def index():
    options = stats()
    options.update({'page_title': 'index'})

    return render_template("index.html", **locals())


@app.route("/review_birds/<path:path>", methods=['GET'])
def return_review_bird(path):
    return send_from_directory("review_birds/", path.split("/")[-1])


@app.route("/upload", methods=["POST"])
@limiter.limit("10 per day", error_message="We cannot take this many birds from you!")
def upload():
    options = stats()
    options.update({'page_title': 'upload'})
    free_storage = os.statvfs("/").f_frsize * os.statvfs("/").f_bfree

    if "file" not in request.files:
        message = "No file found"
        return render_template("upload.html", **locals())

    file = request.files["file"]

    if file.filename == "":
        message = "No file found"
        return render_template("upload.html", **locals())

    if file and free_storage / 1.074e+9 < 1:
        message = "We are out of space for birds!"
        return render_template("upload.html", **locals())

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}.{filename.split('.')[-1].lower()}"
        pathname = os.path.join("review_birds/", filename)

        file.save(pathname)

        file_type = file.filename.split(".")[-1]
        if file_type.lower() in image_extensions:
            shrink = Thread(target=shrink_file, args=(pathname,))
            shrink.start()

        options.update({"bird_review_count": count_directory("review_birds")})
        message = "File uploaded successfully!"

        return render_template("upload.html", **locals())

    return render_template("upload.html", **locals())


@app.route("/upload", methods=["GET"])
def upload_get():
    options = stats()
    options.update({'page_title': 'upload'})

    return render_template("upload.html", **locals())


@app.route("/review", methods=["POST"])
def review():
    options = stats()

    if request.args.get('seed') and bcrypt.check_password_hash(SECRET, request.args.get('seed')):
        app.logger.info('Auth successful! %s', request.remote_addr)
    else:
        app.logger.info('Auth failed... %s', request.remote_addr)

        return redirect(url_for("index"))

    if "House" in request.form:
        image = request.form["House"]
        image_name = image.split("/")[-1]

        os.rename(f"review_birds/{image_name}", f"static/birds/{image_name}")

        path = os.path.join(f"static/birds/{image_name}")

        file_type = image_name.split(".")[-1]
        if file_type in image_extensions:
            shrink = Thread(target=shrink_file, args=(path,))
            shrink.start()

        options.update({"bird_review_count": count_directory("review_birds")})
        app.logger.info('Housed bird: %s', image_name)

    if "Remove" in request.form:
        image = request.form["Remove"]
        image_name = image.split("/")[-1]

        os.remove(f"review_birds/{image_name}")

        options.update({"bird_review_count": count_directory("review_birds")})
        app.logger.info('Removed bird: %s', image_name)

    return render_template("review.html", **locals())


@app.route("/review", methods=["GET"])
def review_get():
    options = stats()

    if request.args.get('seed') and bcrypt.check_password_hash(SECRET, request.args.get('seed')):
        app.logger.info('Auth successful! %s', request.remote_addr)
    else:
        app.logger.info('Auth failed... %s', request.remote_addr)

        return redirect(url_for("index"))

    return render_template("review.html", **locals())


@app.route("/bird.json")
@limiter.limit("500 per hour", error_message="The birds are resting!)")
def bird():
    birds_folder = os.listdir("static/birds")
    try:
        bird_object = {
            'status': 'Success',
            'url': f"{request.url_root}{random_bird(birds_folder, request.args.get('only'), request.args.get('exclude'))}"
        }
        return jsonify(bird_object)
    except ValueError:
        bird_object = {
            'status': 'Failed',
        }
        return jsonify(bird_object)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
