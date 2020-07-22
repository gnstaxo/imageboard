% from board import Board
% from utils import get_size_format, short_msg, is_video
% rebase('base', title=title)
<h1 class="Title">{{title}}</h1>
<div class="Boards">
  <h2 class="Boards-title">Welcome</h2>
  <p id="welcome">{{welcome_message}}</p>
</div>
<div class="Boards">
  <h2 class="Boards-title">Boards</h2>
  <div id="boards">
    % if len(Board.boards()) == 0:
      No boards have been created.
    % end
    % for bname, btitle in Board.boards().items():
      <a href="/{{bname}}/">/{{bname}}/ - {{btitle.board_title}}</a>
    % end
  </div>
</div>
<div class="Boards">
  <h2 class="Boards-title">Latest images</h2>
  <div id="img-container">
    % if len(Board.latest()['images']) == 0:
    No images have been uploaded.
    % end
    % for thread in Board.latest()['images']:
      % if thread.image and (Board.get_board(thread.board_name).nsfw == (show_nsfw == 'True') or not Board.get_board(thread.board_name).nsfw):
          % if thread.is_reply:
            <a href="/{{thread.board_name}}/thread/{{thread.replyrefnum}}#{{thread.refnum}}">
            % if not is_video(thread.filename):
              <img src="/{{thread.image[:-4]}}s.jpg"></a>
            % end
          % else:
            <a href="/{{thread.board_name}}/thread/{{thread.refnum}}" style="text-decoration:none;">
              % if not is_video(thread.filename):
                <img src="/uploads/{{thread.board_name}}/{{thread.refnum}}s.jpg">
              % end
            </a>
          % end
      % end
    % end
  </div>
</div>
<div class="Boards">
  <h2 class="Boards-title">Latest messages</h2>
    <ul id="msg-container">
      % if len(Board.latest()['images']) == 0:
      No messages haven been created.
      % end
      % for thread in Board.latest()['messages']:
        <li>
          % if thread.is_reply:
            <a href="/{{thread.board_name}}/thread/{{thread.replyrefnum}}#{{thread.refnum}}">>>/{{thread.board_name}}/{{thread.replyrefnum}}</a><span class="Card-text">{{short_msg(thread.short_content)}}</span>
          % else:
            <a href="/{{thread.board_name}}/thread/{{thread.refnum}}">>>/{{thread.board_name}}/{{thread.refnum}}</a><span class="Card-text">{{short_msg(thread.short_content)}}</span>
          % end
        </li>
      % end
    </ul>
</div>
<div class="Boards">
  <h2 class="Boards-title">Stats</h2>
  <ul id="stats">
    <li>
      <b>Number of messages :</b> {{Board.stats()["msg_number"]}}
    </li>
    <li>
      <b>Active content :</b> {{get_size_format(Board.stats()["contsize"])}}
    </li>
  </ul>
</div>
<footer>
% include('foot')
</footer>
