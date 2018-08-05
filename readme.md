# Birds are cool

A flask-powered website made for the sole purpose of distributing 
bird pictures through an api

## API

`https://birdsare.cool/bird.json`

Accepts arguments `only` and `exclude` followed by file extensions  
Example:

    https://birdsare.cool/bird.json?only=png,gif
    https://birdsare.cool/bird.json?exclude=mp4

## Development

`git clone https://github.com/vallode/birdsarecool`  

Create your virtual environment:  
`virtualenv -p /usr/bin/python3 env/`

Running the app is simple:  
`env FLASK_APP=birds.py FLASK_DEBUG=True flask run`

The app requires three things to set up:  
`static/birds` folder  
`review_birds` folder  
`secret.py` file

`secret.py` needs to include `API` and `SECRET`  
`API` is your tinypng dev api key  
`SECRET` is your hash that needs to match with your password

Accessing the review endpoint is only available through

    https://birdsare.cool/review?seed=PASSWORD

Shoot me an [email](mailto:vallode@hotmail.co.uk) if you have any questions, or open an issue.