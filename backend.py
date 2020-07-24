#!/bin/env python
from bottle import (run, static_file, request, view, redirect,
        abort, get, post, ConfigDict, response, default_app, error)
from board import Board, Thread, Ip, Report
from utils import random_name, file_validation, remove_media, board_directory
from json import loads
from os import path
from string import punctuation
from waitress import serve
from create_database import create_database

config = ConfigDict()
config.load_config('imageboard.conf')

@get('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

@get('/uploads/<filename:path>')
def send_upload(filename):
    return static_file(filename, root='uploads')

def get_current_user(req):
    ip = req.get('REMOTE_ADDR')

    if Ip.exists(ip):

        current_user = Ip.get_ip(ip)
    else:
        user = Ip(ip, random_name())
        user.create()

        current_user = user

    return current_user

def check_admin(req):
    logged_cookie = req.get_cookie("logged")
    if bool(logged_cookie):
        if logged_cookie != config['admin.token']: return 1
    else: return 1

@get('/')
@view('home')
def home():
    return dict(title=config['app.title'],
            welcome_message=config['app.welcome_message'],
            show_nsfw=config['threads.show_nsfw'])

@get('/<board_name>/')
@get('/<board_name:re:[a-z0-9]+>')
@get('/<board_name>/<page:int>')
@view('board')
def get_board(board_name, page=0):

    board = Board.get_board(board_name)
    if board == 1: return abort(404, "This page doesn't exist.")

    current_user = get_current_user(request)

    per_page = int(config['threads.per_page'])

    if page:

        number = (page + 1) * per_page 
        offset = number - per_page
        threads = board.threads[offset:number]

        if len(threads) < 1: return abort(404, "This page doesn't exist.")

    else: threads = board.threads[:per_page]

    report_reasons = loads(config['reports.reasons'])

    return dict(
            board_name=board.board_name, board_title=board.board_title,
            threads=threads, board=board, current_page=page,
            is_detail = False, current_user = current_user,
            thread_count=board.thread_count,
            max_file_size=config['app.upload_max_size'],
            maxlength=config['threads.content_max_length'],
            per_page=per_page, reasons=report_reasons
        )

@get('/ban_info')
@view('ban')
def ban_info():

    current_user = get_current_user(request)

    return dict(current_user=current_user)

@get('/<board_name>/thread/<refnum:int>')
@view('detail')
def get_thread(board_name, refnum):

    board = Board.get_board(board_name)
    if board == 1: return abort(404, "This page doesn't exist.")

    thread = board.get_thread(refnum)

    if thread.is_reply: abort(404, "This page doesn't exist.")

    report_reasons = loads(config['reports.reasons'])

    return dict(board_name=board.board_name, thread=thread, board=board,
            is_detail=True, current_user=get_current_user(request),
            max_file_size=config['app.upload_max_size'],
            maxlength=config['threads.content_max_length'],
            reasons=report_reasons)

@get('/<board_name>/catalog')
@view('catalog')
def catalog(board_name):

    board = Board.get_board(board_name)
    if board == 1: return abort(404, "This page doesn't exist.")

    return dict(threads=board.threads, board_name=board_name,
            board_title=board.board_title, board=board,
            current_user=get_current_user(request))

@get('/<board_name>/mod')
@view('reports')
def reports(board_name):

    board = Board.get_board(board_name)
    if board == 1: return abort(404, "This page doesn't exist.")

    current_user = get_current_user(request)
    
    if f':{board_name}:' not in current_user.mod:
        return redirect(f"/{board_name}/")

    report_reasons = loads(config['reports.reasons'])

    return dict(reports=board.reports, board=board,
            bans=board.bans, current_user=current_user,
            board_name=board_name, reasons=report_reasons)

@get('/admin')
@view('admin')
def admin_panel():

    current_user = get_current_user(request)

    logged_cookie = request.get_cookie("logged")

    if bool(logged_cookie):

        if logged_cookie != config['admin.token']: return redirect("/")

    else: return redirect("/")

    return dict(boards=Board.boards(), current_user=current_user,
            board_name=None, mods=Ip.get_mods())

@get('/login')
@view('login')
def login():

    current_user = get_current_user(request)

    return dict(current_user=current_user)


@post('/login')
def do_login():

    password = request.forms.get("password")

    if password == config['admin.password']:

        response.set_cookie("logged", config['admin.token'])

        return redirect("/admin")

    return redirect("/login")

@post('/logout')
def do_logout():

    response.delete_cookie('logged')

    return redirect("/")

@post('/<board_name>/')
def post_thread(board_name):

    current_user = get_current_user(request)
    if get_current_user(request).banned: return redirect("/ban_info")

    title = request.forms.get('title')
    content = request.forms.get('content')
    upload = request.files.get('upload')

    if not all([title, content]): return abort(400, "Incomplete post.")

    if len(content) > int(config['threads.content_max_length']):
            return abort(400, "The content exeeds the maximum length.")

    author = current_user.user
    refnum = Board.get_board(board_name).last_id
    save_path = file_validation(board_name, refnum, upload)

    if len(content.split('\n')) < 10:
        short_content = ' '.join(content.split(' ')[:200])
    else:
        if any((len(item) > 200 for item in content.split(' '))):
            short_content = ' '.join(content.split(' ')[:200])
        else:
            short_content = '\n'.join(content.split('\n')[:10])

    if save_path == 1: return redirect(f"/{board_name}/")

    by_mod = (f':{board_name}:' in current_user.mod)
    pinned = False

    thread = Thread(board_name=board_name, author=author,
            short_content=short_content, filename=upload.filename,
            image=save_path, content=content, refnum=refnum,
            title=title, by_mod=by_mod, pinned=pinned)
    thread.create()

    redirect(f"/{board_name}/")

@post('/<board_name>/thread/<refnum:int>')
def post_reply(board_name, refnum):

    current_user = get_current_user(request)

    if get_current_user(request).banned: return redirect("/ban_info")

    board = Board.get_board(board_name)
    thread = board.get_thread(refnum)

    if thread.closed:
        return abort(423, "You cannot reply because this thread is locked.")

    content = request.forms.get('content')

    if not bool(content): return redirect(f'/{board_name}/')

    if len(content) > int(config['threads.content_max_length']):
            return abort(400, "The content exeeds the maximum length.")

    if len(content.split('\n')) < 10:
        short_content = ' '.join(content.split(' ')[:200])
    else:
        if any((len(item) > 200 for item in content.split(' '))):
            short_content = ' '.join(content.split(' ')[:200])
        else:
            short_content = '\n'.join(content.split('\n')[:10])

    upload = request.files.get('upload')

    author = current_user.user
    no = board.last_id

    filename = ""
    save_path = ""

    by_mod = (f':{board_name}:' in current_user.mod)

    if upload is not None:

        save_path = file_validation(board_name, no, upload, True)
        if save_path == 1: return redirect(f"/{board_name}/thread/{refnum}")
        filename = upload.filename

    reply = Thread(board_name=board_name, author=author,
            filename=filename, image=save_path, content=content, refnum=no,
            short_content=short_content, is_reply=True,
            replyrefnum=refnum, by_mod=by_mod)
    reply.create()
    thread.bump()

    redirect(f"/{board_name}/")

@post('/<board_name>/delete')
def delete_thread(board_name):

    current_user = get_current_user(request)

    board = Board.get_board(board_name)
    form = dict(request.forms)

    if bool(form.get('report')):
        reason = form.get('report')
        report_reasons = loads(config['reports.reasons'])
        if reason not in report_reasons: return redirect(f'/{board_name}/')
        for refnum in list(form)[:-1]:
            report = Report(reason, refnum, board_name=board_name)
            report.create()
    else:
        for refnum in form:
            thread = board.get_thread(refnum)
            if (thread.author == current_user.user or
                f':{board_name}:' in current_user.mod):
                if thread.image: remove_media(thread.image)
                if not thread.is_reply:
                    for reply in thread.replies:
                        if reply.image: remove_media(reply.image)
                        reply.delete()
                thread.delete()

    redirect(f"/{board_name}/")

@post('/<board_name>/ban')
def ban(board_name):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(403, "You are not allowed to do this.")

    form = dict(request.forms)

    reason = form.get('reason')

    user = form.get('user').strip()

    Ip.ban(reason, user=user)

    return redirect(f"/{board_name}/mod")

@post('/<board_name>/unban/<user>')
def unban(board_name, user):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(403, "You are not allowed to do this.")

    form = dict(request.forms)

    if bool(form.get("dall")): Ip.dall(user)

    if bool(form.get("unban")): Ip.unban(user)

    return redirect(f"/{board_name}/mod")

@post('/add_board')
def add_board():

    if check_admin(request) == 1:
        return abort(403, "You are not allowed to do this.")

    board_name = request.forms.get("name").strip().lower()

    if any( char in list(punctuation + ' ') for char in board_name ):
        return abort(400, "Boards can't have symbols in their name.")

    if Board.get_board(board_name) != 1:
        return abort(400, "A board with this name already exists.")

    board_title = request.forms.get("title").strip()
    nsfw = bool(request.forms.get("nsfw"))

    board = Board(board_name, board_title, nsfw=nsfw)
    board.create_board()
    board_directory(board_name)

    return redirect("/admin")

@post('/del_board/<board_name>')
def del_board(board_name):

    if check_admin(request) == 1:
        return abort(403, "You are not allowed to do this.")

    Board.delete_board(board_name)
    board_directory(board_name, remove=True)

    return redirect("/admin")

@post('/mod')
def mod():

    if check_admin(request) == 1:
        return abort(403, "You are not allowed to do this.")

    user = request.forms.get("user").strip()
    board = request.forms.get("board")
    opts = request.forms

    if bool(opts.get("add")): Ip.add_mod(user, board)
    if bool(opts.get("rm")): Ip.rm_mod(user, board)
    if bool(opts.get("rmall")): Ip.rm_all(user, board)

    return redirect(f"/admin")

@post('/new_mod')
def add_mod():

    if check_admin(request) == 1:
        return abort(403, "You are not allowed to do this.")

    user = request.forms.get("user").strip()
    board = request.forms.get("board")

    Ip.add_mod(user, board)

    return redirect(f"/admin")

@get('/<board_name>/thread/<refnum:int>/pin')
def thread_pin(board_name, refnum):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(404, "This page doesn't exist.")

    board = Board.get_board(board_name)

    board.get_thread(refnum).pin()

    return redirect(f'/{board_name}/')

@get('/<board_name>/thread/<refnum:int>/close')
def thread_close(board_name, refnum):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(404, "This page doesn't exist.")

    board = Board.get_board(board_name)

    board.get_thread(refnum).close()

    return redirect(f'/{board_name}/')

if __name__ == '__main__':

    if not path.isfile('imageboard.db'): create_database()
    if not path.isdir('uploads'): board_directory('uploads')

    if config['app.production'] == 'False':

        run(debug=True, reloader=True, host='0.0.0.0', port=8080)

    else:
        upload_max_size = int(config['app.upload_max_size'])
        application = default_app()
        serve(application, listen=config['app.domain']+':80',
               max_request_body_size=upload_max_size * 1024**2)
