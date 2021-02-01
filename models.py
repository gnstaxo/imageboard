from peewee import *
from bottle import ConfigDict

try:
    with open('imageboard.conf') as f:
        pass
except FileNotFoundError:
    print("Config file not found.")
    exit()

config = ConfigDict()
config.load_config('imageboard.conf')

if config['database.engine'] == 'sqlite':

    db = SqliteDatabase(f'{config["database.name"]}.db')

elif config['database.engine'] == 'postgresql':

    db = PostgresqlDatabase(
        config['database.name'],
        user     = config['database.username'],
        password = config['database.password'],
        host     = config['database.host'],
        port     = int(config['database.port'])
    )

elif config['database.engine'] == 'mysql':

    db = MySQLDatabase(
        config['database.name'],
        user     = config['database.username'],
        password = config['database.password'],
        host     = config['database.host'],
        port     = int(config['database.port'])
    )

class Anon(Model):
    name = CharField()
    ip = IPField()
    banned = BooleanField(default=False)
    mod = CharField(default="")
    ban_reason = CharField(null=True)
    ban_date = DateTimeField(null=True)

    class Meta:
        database = db

class Board(Model):
    name = CharField()
    title = CharField()
    nsfw = BooleanField(default=False)
    lastrefnum = IntegerField(default=1)

    class Meta:
        database = db

class Post(Model):
    board = ForeignKeyField(Board, backref='posts')
    author = ForeignKeyField(Anon, backref='posts')
    refnum = IntegerField()
    replyrefnum = IntegerField(null=True)
    date = DateTimeField()
    bumped_at = DateTimeField(null=True)
    filename = CharField()
    image = CharField()
    title = CharField(null=True)
    content = TextField()
    short_content = TextField()
    is_reply = BooleanField(default=False)
    closed = BooleanField(default=False)
    pinned = BooleanField(default=False)
    by_mod = BooleanField(default=False)
    replylist = CharField(default="[]")

    class Meta:
        database = db

class Report(Model):
    reason = CharField()
    refnum = IntegerField()
    date = DateTimeField()
    board = ForeignKeyField(Board, backref='reports')

    class Meta:
        database = db

with db:
    db.create_tables([Report, Post, Board, Anon])
