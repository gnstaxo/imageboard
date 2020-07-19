import sqlite3

def create_database():

    conn = sqlite3.connect('imageboard.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE threads
                (date text, board text, author text, filename text, image text, content text, refnum int, title text, is_reply bool, replyrefnum int, bumped_at text, closed bool, by_mod bool, pinned bool, replylist text, short_content text)''')

    c.execute('''CREATE TABLE ips (ip text, last_user text, banned bool, ban_reason text, ban_date text, mod text)''')

    c.execute('''CREATE TABLE reports (reason text, refnum int,  date text, board text)''')

    c.execute('''CREATE TABLE boards (board_name text, board_title text, last_id int, nsfw bool)''')

    conn.commit()

    conn.close()

if __name__ == '__main__':
    create_database()
