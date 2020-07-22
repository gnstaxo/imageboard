import sqlite3
import json
from utils import board_directory, get_directory_size, remove_media
from bottle import ConfigDict

config = ConfigDict()
config.load_config('imageboard.conf')

class Report:

    def __init__(self, reason, refnum, date="", board_name=""):

        self.reason = reason
        self.refnum = refnum
        self.date = date
        self.board_name = board_name

    def create(self):

        conn = sqlite3.connect('imageboard.db')

        c = conn.cursor()

        c.execute("INSERT INTO reports VALUES (?,?,datetime('now'),?)", (self.reason, self.refnum, self.board_name))

        conn.commit()
        conn.close()

class Ip:

    def __init__(self, ip, user, banned=False, ban_reason="", ban_date="", mod=""):

        self.ip = ip
        self.user = user
        self.banned = banned
        self.mod = mod 
        self.ban_reason = ban_reason
        self.ban_date = ban_date

    @classmethod
    def exists(self, ip):

        conn = sqlite3.connect('imageboard.db')

        c = conn.cursor()

        c.execute("SELECT EXISTS(SELECT 1 FROM ips WHERE ip = ?)", (ip,))

        result = c.fetchone()[0]

        conn.commit()
        conn.close()

        return result

    @classmethod
    def get_mods(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute('SELECT * FROM ips WHERE mod IS NOT ""')

        rows = c.fetchall()

        conn.close()

        mod_list = []

        for row in rows: 
            mod_list.append(Ip(*row))

        return mod_list

    @classmethod
    def get_ip(self, ip):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT * FROM ips WHERE ip = ?", (ip,))

        row = c.fetchone()

        conn.close()

        ip = Ip(*row)

        return ip

    @classmethod
    def add_mod(self, user, role):
        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT mod FROM ips WHERE last_user LIKE ?", (user,))

        try:

            roles = c.fetchone()[0]

            if f':{role}:' in roles:
                conn.close()
                return

            roles += ":"+role+":"

            c.execute("UPDATE ips SET mod = ? WHERE last_user LIKE ?", (roles, user))
            conn.commit()

        except: pass

        conn.close()

    @classmethod
    def rm_mod(self, user, role):
        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT mod FROM ips WHERE last_user = ?", (user,))

        roles = c.fetchone()[0]

        roles = roles.replace(f':{role}:', "")

        c.execute("UPDATE ips SET mod = ? WHERE last_user = ?", (roles, user))
        conn.commit()

        conn.close()

    @classmethod
    def rm_all(self, user, role):
        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT mod FROM ips WHERE last_user = ?", (user,))

        roles = c.fetchone()[0]
        roles = ""

        c.execute("UPDATE ips SET mod = ? WHERE last_user = ?", (roles, user))
        conn.commit()

        conn.close()

    def create(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("INSERT INTO ips VALUES (?,?,?,?,?,?)", (self.ip, self.user, self.banned, self.ban_reason, self.ban_date, self.mod))

        conn.commit()
        conn.close()

    @classmethod
    def ban(self, ban_reason, user):
        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("UPDATE ips SET banned = TRUE, ban_reason = ?, ban_date = datetime('now') WHERE last_user = ?",
            (ban_reason, user))

        conn.commit()
        conn.close()

    @classmethod
    def unban(self, user):
        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("DELETE FROM ips WHERE last_user = ?", (user,))

        conn.commit()
        conn.close()

    @classmethod
    def dall(self, user):
        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("DELETE FROM threads WHERE author = ?", (user,))

        conn.commit()
        conn.close()

class Thread:
    def __init__(self, date="", board_name="", author="", filename="", image="", content="",
            refnum=0, title="", is_reply=False, replyrefnum=0, bumped_at="",
            closed=False, by_mod=False, pinned=False, replylist='[]', short_content=""):

        self.date = date
        self.board_name = board_name
        self.author = author
        self.filename = filename
        self.image = image
        self.title = title
        self.content = content
        self.refnum = refnum
        self.is_reply = is_reply
        self.replyrefnum = replyrefnum
        self.bumped_at = bumped_at
        self.closed = closed
        self.by_mod = by_mod
        self.pinned = pinned
        self.replylist = replylist
        self.short_content = short_content

    def add_reply(self, reference):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT * FROM threads WHERE board = ? AND refnum = ?", (self.board_name, self.refnum))

        a = json.loads(Thread(*c.fetchone()).replylist)

        a.append(int(reference))

        c.execute("UPDATE threads SET replylist = ? WHERE board = ? AND refnum = ?",(json.dumps(a), self.board_name, self.refnum))

        conn.commit()
        conn.close()

    def rm_reply(self, reference):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT * FROM threads WHERE board = ? AND refnum = ?", (self.board_name, self.refnum))

        a = json.loads(Thread(*c.fetchone()).replylist)

        a.remove(int(reference))

        c.execute("UPDATE threads SET replylist = ? WHERE board = ? AND refnum = ?",(json.dumps(a), self.board_name, self.refnum))

        conn.commit()
        conn.close()

    def create(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        if self.is_reply:
            for word in self.content.split():
                if word[:2] == ">>":
                    ref = word[2:]
                    if ref.rstrip().isdigit():
                        ref = ref
                        thread_ref = Board.get_board(self.board_name).get_thread(ref)
                        if thread_ref != 1 and self.refnum not in json.loads(thread_ref.replylist):
                            thread_ref.add_reply(self.refnum)

        c.execute("SELECT COUNT(*) FROM threads WHERE is_reply = FALSE and board = ?", (self.board_name,))

        thread_count = c.fetchone()[0]

        if thread_count >= int(config['threads.max_active']):

            c.execute("SELECT * FROM threads WHERE is_reply = FALSE and board = ? ORDER BY date LIMIT ?",
                    (self.board_name, thread_count - int(config['threads.max_active'])))

            rows = c.fetchall()

            for row in rows:

                thread = Thread(*row)
            
                remove_media(thread.image)

                for reply in thread.replies:

                    if reply.image: remove_media(reply.image)

                    reply.delete()

                thread.delete()


        c.execute("INSERT INTO threads VALUES (strftime('%m/%d/%Y %H:%M'),?,?,?,?,?,?,?,?,?,datetime('now'),?,?,?,?,?)",
                (self.board_name, self.author, self.filename,
                self.image, self.content, self.refnum, self.title, 
                self.is_reply, self.replyrefnum, self.closed,
                self.by_mod, self.pinned, self.replylist, self.short_content))

        c.execute("SELECT last_id FROM boards WHERE board_name = ?", (self.board_name,))

        a = c.fetchone()[0]
        a += 1

        c.execute("UPDATE boards SET last_id = ? WHERE board_name = ?", (a, self.board_name))

        conn.commit()
        conn.close()

    def bump(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("UPDATE threads SET bumped_at = datetime('now') WHERE refnum = ? AND board = ?", (self.refnum, self.board_name))

        conn.commit()
        conn.close()

    def delete(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        if self.is_reply:
            for word in self.content.split():
                if word[:2] == ">>":
                    ref = word[2:]
                    if ref.rstrip().isdigit():
                        ref = ref
                        thread_ref = Board.get_board(self.board_name).get_thread(ref)
                        if thread_ref != 1 and self.refnum in json.loads(thread_ref.replylist):
                            thread_ref.rm_reply(self.refnum)

        c.execute("DELETE FROM threads WHERE board = ? AND refnum = ?", (self.board_name, self.refnum))

        conn.commit()
        conn.close()

    def pin(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT pinned FROM threads WHERE refnum = ? AND board = ?", (self.refnum, self.board_name))

        pinned = c.fetchone()[0]

        if pinned:
            c.execute("UPDATE threads SET pinned = FALSE WHERE refnum = ? AND board = ?", (self.refnum, self.board_name))
        else:
            c.execute("UPDATE threads SET pinned = TRUE WHERE refnum = ? AND board = ?", (self.refnum, self.board_name))

        conn.commit()
        conn.close()

    def close(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT closed FROM threads WHERE refnum = ? AND board = ?", (self.refnum, self.board_name))

        closed = c.fetchone()[0]

        if closed:
            c.execute("UPDATE threads SET closed = FALSE WHERE refnum = ? AND board = ?", (self.refnum, self.board_name))
        else:
            c.execute("UPDATE threads SET closed = TRUE WHERE refnum = ? AND board = ?", (self.refnum, self.board_name))

        conn.commit()
        conn.close()

    @property
    def images_count(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute('SELECT COUNT(*) FROM threads WHERE board = ? AND replyrefnum = ? AND filename IS NOT "" AND is_reply = TRUE', (self.board_name, self.refnum,))

        count = c.fetchone()[0]

        conn.commit()
        conn.close()

        return count

    @property
    def replies(self):
        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor() 

        c.execute("SELECT * FROM threads WHERE board = ? AND replyrefnum = ? AND is_reply = TRUE",
                (self.board_name, self.refnum))

        rows = c.fetchall()

        conn.close()

        reply_list = []

        for row in rows:

            reply_list.append(Thread(*row))

        return reply_list

    @property
    def reply_count(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor() 

        c.execute("SELECT COUNT(*) FROM threads WHERE board=? AND replyrefnum = ? AND is_reply = TRUE",
                (self.board_name, self.refnum))
        
        result = c.fetchone()[0]

        conn.close()

        return result


class Board:
    def __init__(self, board_name, board_title, last_id=1, nsfw=False):

        self.board_name = board_name
        self.board_title = board_title
        self.nsfw = nsfw

    @property
    def thread_count(self):
       
        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor() 

        c.execute("SELECT COUNT(*) FROM threads WHERE board=? AND is_reply = FALSE", (self.board_name,))
        
        result = c.fetchone()[0]

        conn.close()

        return result

    @property
    def threads(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor() 

        c.execute("SELECT * FROM threads WHERE board = ? AND is_reply = FALSE ORDER BY bumped_at DESC", (self.board_name,))

        rows = c.fetchall()

        conn.close()

        thread_list = []

        pinned_thread_list = []

        for row in rows:
            thread = Thread(*row)

            if thread.pinned:
                pinned_thread_list.append(thread)
            else:
                thread_list.append(thread)

        pinned_thread_list.reverse()

        return pinned_thread_list + thread_list

    @property
    def reports(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor() 

        c.execute("SELECT * FROM reports WHERE board = ?", (self.board_name,))

        rows = c.fetchall()

        conn.close()

        report_list = []

        for row in rows:
            report_list.append(Report(*row))

        report_list.sort(key=lambda report: report.date, reverse=True)

        return report_list

    @property
    def bans(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT * FROM ips WHERE banned = TRUE")

        rows = c.fetchall()
        conn.close()

        ban_list = []

        for row in rows:

            ban_list.append(Ip(*row))

        ban_list.reverse()

        return ban_list
    
    @property
    def last_id(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor() 

        c.execute("SELECT last_id FROM boards WHERE board_name = ?", (self.board_name,))

        rows = c.fetchone()[0]

        conn.close()

        return rows


    def get_thread(self, refnum):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT * FROM threads WHERE board = ? AND refnum = ?", (self.board_name, str(refnum)))

        row = c.fetchone()

        conn.close()

        try:
            thread = Thread(*row)
            return thread
        except TypeError:
            return 1

    def create_board(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("INSERT INTO boards VALUES (?,?,?,?)",
                (self.board_name, self.board_title, 1, self.nsfw))

        conn.commit()
        conn.close()

    @classmethod
    def delete_board(self, board_name):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("DELETE FROM boards WHERE board_name = ?", (board_name,))
        c.execute("DELETE FROM threads WHERE board = ?", (board_name,))
        conn.commit()

        c.execute("SELECT * FROM ips WHERE mod LIKE ?", (f'%:{board_name}:%',))

        rows = c.fetchall()
        conn.close()

        for row in rows:

            user = Ip(*row)
            Ip.rm_mod(user.user, board_name)
        
    @classmethod
    def boards(self):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT * FROM boards")

        rows = c.fetchall()
        conn.close()

        board_list = {}

        for row in rows:

            board_list[row[0]] = Board(*row)

        return board_list

    @classmethod
    def get_board(self, board_name):

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT * FROM boards WHERE board_name = ?", (board_name,))

        row = c.fetchone()
        conn.close()
        
        if row is None: return 1

        board = Board(*row)

        return board

    @classmethod
    def latest(self):

        LATEST = {'messages': [], 'images': []}

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT * FROM threads ORDER BY date DESC LIMIT 10")
        rows = c.fetchall()

        for row in rows: LATEST['messages'].append(Thread(*row))

        c.execute('SELECT * FROM threads WHERE image IS NOT "" ORDER BY date DESC LIMIT 10')

        rows = c.fetchall()

        for row in rows: LATEST['images'].append(Thread(*row))

        conn.close()

        return LATEST

    @classmethod
    def stats(self):

        STATS = {}

        conn = sqlite3.connect('imageboard.db')
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM threads")

        number = c.fetchone()[0]
        STATS["msg_number"] = number

        conn.close()

        STATS["contsize"] = get_directory_size("uploads")

        return STATS
