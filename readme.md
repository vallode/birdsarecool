# Birds are cool

A tiny website made for the sole purpose of providing an api for random bird pictures.
Yes.

## Usage

Api has one endpoint: `/bird.json`  
It returns a json with a random bird url

It can accept the argument `file` set to whatever extension you want 
as an example: `/birds.json?file=gif` will return only gif images from the archive
## Local

`git clone https://github.com/vallode/birdsarecool birdsarecool`  
`cd birdsarecool`  
`mkdir review_birds`  
`mkdir static/birds`  

You have to create a `secret.py` file with your hash and and tinypng API key

Shoot me an [email](mailto:vallode@hotmail.co.uk) if you have any questions, or open an issue.