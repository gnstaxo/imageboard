# Imageboard
Imageboard engine written in Python.
![Screenshot](https://0x0.st/iv0g.png)

## Features
- Simple markdown: bold (**), italic (*) and underline (__)
- Green (>) and Pink (<) text
- Quick replies
- Reply previews
- Mod and Admin panels
- Youtube embeds
- Mobile responsive design (through CSS media queries)

## Dependencies
- bottle
- pillow
- waitress
- filetype

## Usage
To start the app:

`$ ./backend`

To change stuff edit `imageboard.conf`

Admin dashboard is at /admin for which you'll first have to go through /login.

## Notes
- The function to limit the size of uploads only works in production mode.
