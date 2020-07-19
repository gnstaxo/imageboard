% from board import Board

<div class="Menu">
[<a href="/">Home</a>]
% if len(Board.boards()) > 0:
[
  % for bname, btitle in Board.boards().items():
    <a href="/{{bname}}/" title="{{btitle.board_title}}">{{bname}}</a>
    % if list(Board.boards())[-1] != bname:
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
