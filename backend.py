#!/bin/env python
from bottle import (run, static_file, request, view, redirect,
        abort, get, post, ConfigDict, response, default_app, error)
from utils import random_name, file_validation, remove_media, board_directory, get_directory_size
from json import loads, dumps
from os import path, mkdir
from string import punctuation
from models import db, Post, Anon, Board, Report, Captcha
from datetime import datetime,timedelta
from captcha.image import ImageCaptcha
from random import randint

config = ConfigDict()
config.load_config('imageboard.conf')

basename = config['app.basename']
if basename[-1] == '/': basename = basename[:-1] # remove trailing slash

@get('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root='static')

@get('/uploads/<filename:path>')
def send_upload(filename):
    return static_file(filename, root='uploads')

def get_current_user(req):

    ip = req.get('HTTP_X_FORWARDED_FOR')
    if ip is None: ip = req.get('REMOTE_ADDR')

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
    show_nsfw = eval(config['home.show_nsfw'])
    active_content_size = get_directory_size('uploads')
    number_of_messages = Post.select().count()
    return dict(title=config['app.title'],
            welcome_message=config['home.welcome_message'],
            home_messages=int(config['home.messages']),
            home_images=int(config['home.images']),
            show_nsfw=show_nsfw, active_content_size=active_content_size,
            number_of_messages=number_of_messages, basename=basename)

@get('/captcha')
def generate_captcha():

    text = randint(10000,99999)
    time_exp = datetime.now() + timedelta(minutes=5)

    captcha = Captcha(text = text, time_exp = time_exp)
    captcha.save()

    challenge = {
        'id': captcha.id,
        'text': text,
        'time_exp': str(time_exp)
    }

    return dumps(challenge)

@get('/captchaimg/<cha:int>')
def captcha_image(cha):
    image = ImageCaptcha()
    code = Captcha.get_by_id(cha).text
    data = image.generate(code)
    response.content_type = "image/png"
    return data

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

    query = board.posts.where(Post.is_reply == False).order_by(Post.pinned.desc(), Post.bumped_at.desc())

    threads = query.paginate(page, per_page)

    return dict(
            board_name=board.name, board_title=board.title,
            threads=threads, board=board, current_page=page,
            is_detail = False, current_user = current_user,
            thread_count=query.count(),
            max_file_size=config['uploads.upload_max_size'],
            maxlength=config['threads.content_max_length'],
            timestamp_format=config['threads.timestamp'],
            per_page=per_page, basename=basename,
            host='://'.join(request.urlparts[:2])
        )

@get('/ban_info')
@view('ban')
def ban_info():

    current_user = get_current_user(request)

    return dict(current_user=current_user, basename=basename)

@get('/<board_name>/thread/<refnum:int>')
@view('detail')
def get_thread(board_name, refnum):

    try:
        board = Board.get(Board.name == board_name)
    except:
        return abort(404, "This page doesn't exist.")

    try:
        thread = board.posts.where(Post.refnum == refnum).get()
    except:
        abort(404, "This page doesn't exist.")

    return dict(board_name=board.name, thread=thread, board=board,
            is_detail=True, current_user=get_current_user(request),
            max_file_size=config['uploads.upload_max_size'],
            maxlength=config['threads.content_max_length'], basename=basename,
            timestamp_format=config['threads.timestamp'],
            host='://'.join(request.urlparts[:2])
    )

@get('/<board_name>/catalog')
@view('catalog')
def catalog(board_name):

    try:
        board = Board.get(Board.name == board_name)
    except:
        return abort(404, "This page doesn't exist.")

    query = board.posts.where(Post.is_reply == False).order_by(Post.pinned.desc(), Post.bumped_at.desc())

    return dict(threads=query, board_name=board.name,
            board_title=board.title, board=board,
            current_user=get_current_user(request), basename=basename)

@get('/<board_name>/mod')
@view('reports')
def reports(board_name):

    try:
        board = Board.get(Board.name == board_name)
    except:
        return abort(404, "This page doesn't exist.")

    current_user = get_current_user(request)
    
    if f':{board_name}:' not in current_user.mod:
        return redirect(f'{basename}/{board_name}/')

    report_reasons = loads(config['reports.reasons'])

    return dict(board=board, bans=Anon.select().where(Anon.banned == True),
            current_user=current_user, board_name=board_name,
            reasons=report_reasons, reports=board.reports, basename=basename)

@get('/admin')
@view('admin')
def admin_panel():

    current_user = get_current_user(request)

    logged_cookie = request.get_cookie("logged")

    if bool(logged_cookie):

        if logged_cookie != config['admin.token']: return redirect(f'{basename}/')

    else: return redirect(f'{basename}/')

    return dict(boards=Board.select(), current_user=current_user,
            board_name=None, mods=Anon.select().where(Anon.mod != ""),
            basename=basename)

@get('/login')
@view('login')
def login():

    current_user = get_current_user(request)

    return dict(current_user=current_user, basename=basename)


@post('/login')
def do_login():

    password = request.forms.get("password")

    if password == config['admin.password']:

        response.set_cookie("logged", config['admin.token'])

        return redirect(f'{basename}/admin')

    return redirect(f'{basename}/login')

@post('/logout')
def do_logout():

    response.delete_cookie('logged')

    return redirect(f'{basename}/')

@post('/<board_name>/')
def post_thread(board_name):

    captchares = request.forms.get('captchares')
    captchaid = request.forms.get('captchaid')

    challenge = Captcha.get_by_id(captchaid)

    if (challenge.text != captchares or
    challenge.time_exp <= datetime.now()): return abort(403, "Invalid Captcha.")

    current_user = get_current_user(request)
    if get_current_user(request).banned: return redirect(f'{basename}/ban_info')

    board = Board.get(Board.name == board_name)

    title = request.forms.get('title')
    content = request.forms.get('content')
    upload = request.files.get('upload')

    if not all([title, content]): return abort(400, "Incomplete post.")

    if len(content) > int(config['threads.content_max_length']):
            return abort(400, "The content exeeds the maximum length.")

    if request.content_length > float(config['uploads.upload_max_size']) * 1024 * 1024:
        return abort(400, "The file exeeds the maximum size.")

    author = current_user
    refnum = board.lastrefnum
    save_path = file_validation(board_name, refnum, upload)

    if len(content.split('\n')) < 10:
        short_content = ' '.join(content.split(' ')[:200])
    else:
        if any((len(item) > 200 for item in content.split(' '))):
            short_content = ' '.join(content.split(' ')[:200])
        else:
            short_content = '\n'.join(content.split('\n')[:10])

    if save_path == 1: return redirect(f'{basename}/{board_name}/')

    data = {
        "board": board,
        "author": author,
        "refnum": refnum,
        "filename": upload.filename,
        "image": save_path,
        "title": title,
        "content": content,
        "short_content": short_content,
    }

    thread = Post(**data)
    thread.save()

    board.lastrefnum += 1
    board.save()

    max_active_threads = int(config['threads.max_active'])

    query = board.posts.where(Post.is_reply == False).order_by(
            Post.pinned.desc(), Post.bumped_at.desc())

    if query.count() >= max_active_threads:

        threads_to_delete = query.offset(max_active_threads)

        for thread in threads_to_delete:

            remove_textual_refs(board, thread)
            thread.delete_instance()
            remove_media(thread.image)

            for reply in board.posts.where(Post.replyrefnum == thread.refnum):

                    reply.delete_instance()
                    remove_media(reply.image)

    redirect(f'{basename}/{board_name}/')

@post('/<board_name>/thread/<refnum:int>')
def post_reply(board_name, refnum):

    current_user = get_current_user(request)
    if get_current_user(request).banned: return redirect(f'{basename}/ban_info')

    board = Board.get(Board.name == board_name)
    thread = board.posts.where(Post.refnum == refnum).get()

    if thread.closed:
        return abort(423, "You cannot reply because this thread is locked.")

    content = request.forms.get('content')

    if not bool(content): return redirect(f'{basename}/{board_name}/')

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

    author = current_user
    no = board.lastrefnum

    filename = ""
    save_path = ""

    if upload is not None:

        if request.content_length > float(config['uploads.upload_max_size']) * 1024 * 1024:
            return abort(400, "The file exeeds the maximum size.")

        if upload.content_type.startswith('image') or upload.content_type.startswith('video'):

            save_path = file_validation(board_name, no, upload, is_reply=True)
            if save_path == 1: return redirect(f'{basename}/{board_name}/thread/{refnum}')
            filename = upload.filename

    data = {
        "board": board,
        "author": author,
        "refnum": no,
        "is_reply": True,
        "replyrefnum": refnum,
        "filename": filename,
        "image": save_path,
        "content": content,
        "short_content": short_content,
    }

    reply = Post(**data)
    reply.save()

    for word in content.split():
        if word[:2] == ">>":
            ref = word[2:]
            if ref.rstrip().isdigit():
                ref = int(ref)
                try:
                    thread_ref = board.posts.where(Post.refnum == ref).get()
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

    redirect(f'{basename}/{board_name}/')

def remove_textual_refs(board, thread):
    for word in thread.content.split():
        if word[:2] == ">>":
            ref = word[2:]
            if ref.rstrip().isdigit():

                thread_ref = board.posts.where(Post.refnum == ref).get_or_none()
                if thread_ref is None: continue

                replylist = loads(thread_ref.replylist)
                if thread.refnum in replylist:
                    replylist.remove(thread.refnum)
                    thread_ref.replylist = dumps(replylist)
                    thread_ref.save()

@post('/<board_name>/delete')
def delete_post(board_name):

    current_user = get_current_user(request)

    board = Board.get(Board.name == board_name)
    form = dict(request.forms)

    if bool(form.get('report')):
        reason = form.get('report')
        report_reasons = loads(config['reports.reasons'])
        if reason not in report_reasons: return redirect(f'{basename}/{board_name}/')
        for refnum in list(form)[:-1]:
            report = Report(reason=reason, refnum=refnum, board=board, date=datetime.now().replace(microsecond=0))
            report.save()
    else:
        for refnum in form:
            thread = board.posts.where(Post.refnum == refnum).get()
            if (thread.author == current_user or
                f':{board_name}:' in current_user.mod):

                remove_textual_refs(board, thread)
                
                if thread.image: remove_media(thread.image)

                if not thread.is_reply:

                    for reply in board.posts.where(Post.replyrefnum == thread.refnum):

                        if reply.image: remove_media(reply.image)
                        reply.delete_instance()

                thread.delete_instance()
                Report.delete().where(refnum == thread.refnum).execute()

    redirect(f'{basename}/{board_name}/')

@post('/<board_name>/ban')
def ban(board_name):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(403, "You are not allowed to do this.")

    form = dict(request.forms)

    reason = form.get('reason')

    user = form.get('user').strip()

    Anon.update(banned=True, ban_reason=reason, ban_date=datetime.now().replace(microsecond=0)).where(Anon.name == user).execute()

    return redirect(f'{basename}/{board_name}/mod')

@post('/<board_name>/unban/<name>')
def unban(board_name, name):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(403, "You are not allowed to do this.")

    form = dict(request.forms)

    anon = Anon.get(Anon.name == name)

    if bool(form.get("dall")):
        Post.delete().where(Post.author_id == anon.id).execute()

    if bool(form.get("unban")):
        Anon.update(banned=False, ban_reason=None, ban_date=None).where(Anon.name == name).execute()

    return redirect(f'{basename}/{board_name}/mod')

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

    return redirect(f'{basename}/admin')

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

    return redirect(f'{basename}/admin')

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

    return redirect(f'{basename}/admin')

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

    return redirect(f'{basename}/admin')

@get('/<board_name>/thread/<refnum:int>/pin')
def thread_pin(board_name, refnum):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(404, "This page doesn't exist.")

    board = Board.get(Board.name == board_name)

    thread = board.posts.where(Post.refnum == refnum).get()

    if thread.pinned: thread.pinned = False
    else: thread.pinned = True

    thread.save()

    return redirect(f'{basename}/{board_name}/')

@get('/<board_name>/thread/<refnum:int>/close')
def thread_close(board_name, refnum):

    if f':{board_name}:' not in get_current_user(request).mod:
        return abort(404, "This page doesn't exist.")

    board = Board.get(Board.name == board_name)

    thread = board.posts.where(Post.refnum == refnum).get()

    if thread.closed: thread.closed = False
    else: thread.closed = True

    thread.save()

    return redirect(f'{basename}/{board_name}/')

if __name__ == '__main__':

    db.connect()

    if not path.isdir('uploads'): mkdir('uploads')

    url_prefix = basename

    def fix_environ_middleware(app):
      def fixed_app(environ, start_response):
        path = environ['PATH_INFO']
        if path.startswith("/"):
            # strip extra slashes at the beginning of a path that starts
            # with any number of slashes
            path = "/" + path.lstrip("/")

        if url_prefix:
            # NB: url_prefix is guaranteed by the configuration machinery to
            # be either the empty string or a string that starts with a single
            # slash and ends without any slashes
            if path == url_prefix:
                # if the path is the same as the url prefix, the SCRIPT_NAME
                # should be the url_prefix and PATH_INFO should be empty
                path = ""
            else:
                # if the path starts with the url prefix plus a slash,
                # the SCRIPT_NAME should be the url_prefix and PATH_INFO should
                # the value of path from the slash until its end
                url_prefix_with_trailing_slash = url_prefix + "/"
                if path.startswith(url_prefix_with_trailing_slash):
                    path = path[len(url_prefix) :]
        environ['SCIPT_NAME'] = url_prefix
        environ['PATH_INFO'] = path
        return app(environ, start_response)
      return fixed_app

    app = default_app()
    app.wsgi = fix_environ_middleware(app.wsgi)

    production = eval(config['app.production'])

    run(
        debug    = not production,
        reloader = not production,
        host     = config['app.host'],
        port     = config['app.port']
    )
