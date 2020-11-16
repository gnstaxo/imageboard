% from models import Board

<div class="Menu">
[<a href="/">Home</a>]
% if Board.select().count() > 0:
[
  % for board in Board.select():
    <a href="/{{board.name}}/" title="{{board.title}}">{{board.name}}</a>
    % if Board.select()[-1].name != board.name:
    /
    % end
  % end
]
% end
% if defined('board_name'):
  % if f':{board_name}:' in current_user.mod:
    [<a href="/{{board_name}}/mod">Mod</a>]
  % end
% end
</div>
