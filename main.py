from flask import Flask, request, send_from_directory, render_template, redirect, jsonify, url_for
from hurry.filesize import size, alternative
import random
import os
import os.path
app = Flask(__name__)


def count_directory():
    directory = os.listdir("static/birds")
    count = len(directory)
    return count


def count_images():
    directory = os.listdir("static/birds")
    image_count = 0

    for file in directory:
        if file.split(".")[1] == 'png':
            image_count += 1
    return image_count


def count_videos():
    directory = os.listdir("static/birds")
    video_count = 0

    for file in directory:
        if file.split(".")[1] == 'mp4':
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


@app.route("/")
def index():
    image, video = False, False
    bird_count = count_directory()
    bird_image_count = count_images()
    bird_video_count = count_videos()
    storage_size = return_directory_size()

    current_bird = random_bird()
    bird_path = f"static/birds/{current_bird}"
    file_type = current_bird.split(".")[1]

    if file_type == "mp4":
        video = True
    else:
        image = True

    return render_template('index.html', **locals())


@app.route("/bird")
def bird():
    bird_object = {
        'url': f"static/birds/{random_bird()}"
    }
    return jsonify(bird_object)


if __name__ == '__main__':
    app.run(debug=True)
