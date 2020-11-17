#!/bin/env python
from bottle import (run, static_file, request, view, redirect,
        abort, get, post, ConfigDict, response, default_app, error)
from utils import random_name, file_validation, remove_media, board_directory, get_directory_size
from json import loads, dumps
from os import path
from string import punctuation
from waitress import serve
from models import db, Post, Anon, Board, Report
from datetime import datetime

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

    try:
        current_user = Anon.get(Anon.ip == ip)
    except:
        anon = Anon(ip = ip, name = random_name())
        anon.save()

        current_user = anon

    return current_user

def check_admin(req):
    logged_cookie = req.get_cookie("logged")
    if bool(logged_cookie):
        if logged_cookie != config['admin.token']: return 1
    else: return 1

@get('/')
@view('home')
def home():
    show_nsfw = ('True' == config['threads.show_nsfw'])
    active_content_size = get_directory_size('uploads')
    number_of_messages = Post.select().count()
    return dict(title=config['app.title'],
            welcome_message=config['app.welcome_message'],
            show_nsfw=show_nsfw, active_content_size=active_content_size, number_of_messages=number_of_messages)

@get('/<board_name>/')
@get('/<board_name:re:[a-z0-9]+>')
@get('/<board_name>/<page:int>')
@view('board')
def get_board(board_name, page=1):

    try:
        board = Board.get(Board.name == board_name)
    except:
        abort(404, "This page doesn't exist.")

    current_user = get_current_user(request)

    per_page = int(config['threads.per_page'])

    query = Post.select().join(Board).where((Board.name == board_name) & (Post.is_reply == False)).order_by(Post.pinned.desc(), Post.bumped_at.desc())

    threads = query.paginate(page, per_page)

    report_reasons = loads(config['reports.reasons'])

    return dict(
            board_name=board.name, board_title=board.title,
            threads=threads, board=board, current_page=page,
            is_detail = False, current_user = current_user,
            thread_count=query.count(),
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

    try:
        board = Board.get(Board.name == board_name)
    except:
        return abort(404, "This page doesn't exist.")

    try:
        thread = Post.select().join(Board).where((Post.refnum == refnum) &
                (Board.name == board_name) & (Post.is_reply == False)).get()
    except:
        abort(404, "This page doesn't exist.")

    report_reasons = loads(config['reports.reasons'])

    return dict(board_name=board.name, thread=thread, board=board,
            is_detail=True, current_user=get_current_user(request),
            max_file_size=config['app.upload_max_size'],
            maxlength=config['threads.content_max_length'],
            reasons=report_reasons)

@get('/<board_name>/catalog')
@view('catalog')
def catalog(board_name):

    try:
        board = Board.get(Board.name == board_name)
    except:
        return abort(404, "This page doesn't exist.")

    query = Post.select().join(Board).where((Board.name == board_name) & (Post.is_reply == False)).order_by(Post.bumped_at.desc())

    return dict(threads=query, board_name=board.name,
            board_title=board.title, board=board,
            current_user=get_current_user(request))

@get('/<board_name>/mod')
@view('reports')
def reports(board_name):

    try:
        board = Board.get(Board.name == board_name)
    except:
        return abort(404, "This page doesn't exist.")

    current_user = get_current_user(request)
    
    if f':{board_name}:' not in current_user.mod:
        return redirect(f"/{board_name}/")

    report_reasons = loads(config['reports.reasons'])

    return dict(reports=Report.select(), board=board,
            bans=Anon.select().where(Anon.banned == True), current_user=current_user,
            board_name=board_name, reasons=report_reasons)

@get('/admin')
@view('admin')
def admin_panel():

    current_user = get_current_user(request)

    logged_cookie = request.get_cookie("logged")

    if bool(logged_cookie):

        if logged_cookie != config['admin.token']: return redirect("/")

    else: return redirect("/")

    return dict(boards=Board.select(), current_user=current_user,
            board_name=None, mods=Anon.select().where(Anon.mod != ""))

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

    board = Board.get(Board.name == board_name)

    title = request.forms.get('title')
    content = request.forms.get('content')
    upload = request.files.get('upload')

    if not all([title, content]): return abort(400, "Incomplete post.")

    if len(content) > int(config['threads.content_max_length']):
            return abort(400, "The content exeeds the maximum length.")

    author = current_user.name
    refnum = board.lastrefnum
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

    data = {
        "board": board,
        "author": author,
        "refnum": refnum,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "bumped_at": datetime.now().replace(microsecond=0),
        "filename": upload.filename,
        "image": save_path,
        "title": title,
        "content": content,
        "short_content": short_content,
        "by_mod": by_mod
    }

    thread = Post(**data)
    thread.save()

    board.lastrefnum += 1
    board.save()

    max_active_threads = int(config['threads.max_active'])
    query = Post.select().join(Board).where((Board.name == board.name) &
            (Post.is_reply == False)).order_by(Post.pinned.desc(),
            Post.bumped_at.desc())

    if query.count() >= max_active_threads:

        threads_to_delete = query.offset(max_active_threads)

        for thread in threads_to_delete:

            thread.delete_instance()
            remove_media(thread.image)

            for reply in Post.select().join(Board).where((Board.name == board.name) & (Post.replyrefnum == thread.refnum)):

                    reply.delete_instance()
                    remove_media(reply.image)


    redirect(f"/{board_name}/")

@post('/<board_name>/thread/<refnum:int>')
def post_reply(board_name, refnum):

    current_user = get_current_user(request)
    if get_current_user(request).banned: return redirect("/ban_info")

    board = Board.get(Board.name == board_name)
    thread = Post.select().join(Board).where((Post.refnum == refnum) & (Board.name == board_name)).get()

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

    author = current_user.name
    no = board.lastrefnum

    filename = ""
    save_path = ""

    by_mod = (f':{board_name}:' in current_user.mod)

    if upload is not None:

        save_path = file_validation(board_name, no, upload, True)
        if save_path == 1: return redirect(f"/{board_name}/thread/{refnum}")
        filename = upload.filename

    data = {
        "board": board,
        "author": author,
        "refnum": no,
        "is_reply": True,
        "replyrefnum": refnum,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "filename": filename,
        "image": save_path,
        "content": content,
        "short_content": short_content,
        "by_mod": by_mod
    }

    reply = Post(**data)
    reply.save()

    for word in content.split():
        if word[:2] == ">>":
            ref = word[2:]
            if ref.rstrip().isdigit():
                ref = int(ref)
                try:
                    thread_ref = Post.select().join(Board).where((Board.name == board.name) & (Post.refnum == ref)).get()
                    replylist = loads(thread_ref.replylist)
                    if no not in replylist:
                        replylist.append(no)
                        thread_ref.replylist = dumps(replylist)
                        thread_ref.save()
                except: pass

    thread.bumped_at = datetime.now().replace(microsecond=0)
    thread.save()

    board.lastrefnum += 1
    board.save()

    redirect(f"/{board_name}/")

@post('/<board_name>/delete')
def delete_thread(board_name):

    current_user = get_current_user(request)

    board = Board.get(Board.name == board_name)
    form = dict(request.forms)

    if bool(form.get('report')):
        reason = form.get('report')
        report_reasons = loads(config['reports.reasons'])
        if reason not in report_reasons: return redirect(f'/{board_name}/')
        for refnum in list(form)[:-1]:
            report = Report(reason=reason, refnum=refnum, board=board_name, date=datetime.now().replace(microsecond=0))
            report.save()
    else:
        for refnum in form:
            thread = Post.select().join(Board).where((Board.name == board.name) & (Post.refnum == refnum)).get()
            if (thread.author == current_user.name or
                f':{board_name}:' in current_user.mod):

                for word in thread.content.split():
                    if word[:2] == ">>":
                        ref = word[2:]
                        if ref.rstrip().isdigit():
                            ref = ref
                            try:
                                thread_ref = Post.select().join(Board).where((Board.name == board.name) & (Post.refnum == ref)).get()
                                replylist = loads(thread_ref.replylist)
                                if thread.refnum in replylist:
                                    replylist.remove(thread.refnum)
                                    thread_ref.replylist = dumps(replylist)
                                    thread_ref.save()
                            except: pass


                if thread.image: remove_media(thread.image)
                if not thread.is_reply:
                    for reply in Post.select().join(Board).where((Board.name == thread.board.name) & (Post.replyrefnum == thread.refnum)):
                        if reply.image: remove_media(reply.image)
                        Post.delete().join(Board).where((Board.name == thread.board.name) & (Post.replyrefnum == thread.refnum)).execute()
                thread.delete_instance()


    redirect(f"/{board_name}/")

@post('/<board_name>/ban')
def ban(board_name):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(403, "You are not allowed to do this.")

    form = dict(request.forms)

    reason = form.get('reason')

    user = form.get('user').strip()

    Anon.update(banned=True, ban_reason=reason, ban_date=datetime.now().replace(microsecond=0)).where(Anon.name == user).execute()

    return redirect(f"/{board_name}/mod")

@post('/<board_name>/unban/<user>')
def unban(board_name, user):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(403, "You are not allowed to do this.")

    form = dict(request.forms)

    if bool(form.get("dall")):
        Post.delete().where(Post.author == user).execute()

    if bool(form.get("unban")):
        Anon.update(banned=False, ban_reason=None, ban_date=None).where(Anon.name == user).execute()

    return redirect(f"/{board_name}/mod")

@post('/add_board')
def add_board():

    if check_admin(request) == 1:
        return abort(403, "You are not allowed to do this.")

    name = request.forms.get("name").strip().lower()

    if any( char in list(punctuation + ' ') for char in name ):
        return abort(400, "Boards can't have symbols in their name.")

    if Board.select().where(Board.name == name).exists():
        return abort(400, "A board with this name already exists.")

    data = {
        "name": name,
        "nsfw": bool(request.forms.get("nsfw")),
        "title": request.forms.get("title").strip()
    }

    board = Board(**data)
    board.save()
    board_directory(name)

    return redirect("/admin")

@post('/del_board/<board_name>')
def del_board(board_name):

    if check_admin(request) == 1:
        return abort(403, "You are not allowed to do this.")

    for anon in Anon.select().where(Anon.mod != ""):
        anon.mod = anon.mod.replace(f':{board_name}:', '')
        anon.save()

    board = Board.get(Board.name == board_name)

    Post.delete().where(Post.board_id == board.id).execute()

    board.delete_instance()
    board_directory(board_name, remove=True)

    return redirect("/admin")

@post('/mod')
def mod():

    if check_admin(request) == 1:
        return abort(403, "You are not allowed to do this.")

    user = request.forms.get("user").strip()
    board = request.forms.get("board")
    opts = request.forms

    anon = Anon.get(Anon.name == user)

    if bool(opts.get("add")) and f':{board}:' not in anon.mod:
        anon.mod += f':{board}:'

    if bool(opts.get("rm")): anon.mod = anon.mod.replace(f':{board}:', '')

    if bool(opts.get("rmall")): anon.mod = ""

    anon.save()

    return redirect(f"/admin")

@post('/new_mod')
def add_mod():

    if check_admin(request) == 1:
        return abort(403, "You are not allowed to do this.")

    user = request.forms.get("user").strip()
    board = request.forms.get("board")

    try:
        anon = Anon.get(Anon.name == user)
    except:
        return abort(404, "User does not exist.")

    if f':{board}:' not in anon.mod: anon.mod += ":"+board+":"

    anon.save()

    return redirect(f"/admin")

@get('/<board_name>/thread/<refnum:int>/pin')
def thread_pin(board_name, refnum):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(404, "This page doesn't exist.")

    board = Board.get(Board.name == board_name)

    thread = Post.select().join(Board).where((Board.name == board_name) &
            (Post.refnum == refnum)).get()

    if thread.pinned: thread.pinned = False
    else: thread.pinned = True

    thread.save()

    return redirect(f'/{board_name}/')

@get('/<board_name>/thread/<refnum:int>/close')
def thread_close(board_name, refnum):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(404, "This page doesn't exist.")

    board = Board.get(Board.name == board_name)

    thread = Post.select().join(Board).where((Board.name == board_name) &
            (Post.refnum == refnum)).get()

    if thread.closed: thread.closed = False
    else: thread.closed = True

    thread.save()

    return redirect(f'/{board_name}/')

if __name__ == '__main__':

    db.connect()

    if not path.isdir('uploads'): board_directory('uploads')

    if config['app.production'] == 'False':

        run(debug=True, reloader=True, host='127.0.0.1', port=8080)

    else:
        upload_max_size = int(config['app.upload_max_size'])
        application = default_app()
        serve(application, listen=config['app.domain']+':'+config['app.port'],
               max_request_body_size=upload_max_size * 1024**2)
