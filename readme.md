# Birds are cool

A tiny website made for the sole purpose of providing an api for random bird pictures.
Yes.

## Usage

`bird.json`

Accepts arguments `only` and `exclude` followed by file extensions  
Example:

    https://birdsare.cool/bird.json?only=png,gif
    https://birdsare.cool/bird.json?exclude=mp4

## Local

`git clone https://github.com/vallode/birdsarecool birdsarecool`  

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