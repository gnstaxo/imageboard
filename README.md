# Imageboard
![Screenshot](https://0x0.st/iv0g.png)

## Features
- Simple markdown: bold (**), italic (*) and underline (__)
- Green (>) and Pink (<) text
- Quick replies
- Reply previews
- Mod and Admin functions
- Youtube embeds
- Mobile responsive design (through CSS media queries)

## Dependencies
- bottle: Web framework.
- filetype: To make sure people upload valid files.
- Pillow: To create thumbnails and get image dimensions.
- waitress: Production server.
- peewee: SQL ORM.

## Usage
First, get the dependencies:

`$ pip install -r requirements.txt`

Then you can run the app:

`$ python backend.py`

To change stuff edit `imageboard.conf`

Admin dashboard is at /admin for which you'll first have to go through /login.

## Notes
- The function to limit the size of uploads only works in production mode.
- To use a MySQL database install pymysql, and psycopg2 for Postgresql.
