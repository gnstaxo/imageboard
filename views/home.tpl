% from models import Post, Board
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
    % if Board.select().count() == 0:
      No boards have been created.
    % end
    % for board in Board.select():
      <a href="{{basename}}/{{board.name}}/" style="display:inline-block;">/{{board.name}}/ - {{board.title}}</a>
    % end
  </div>
</div>
% if home_images:
<div class="Boards">
  <h2 class="Boards-title">Latest images</h2>
  <div id="img-container">
    % images_to_show = Post.select().join(Board).where((Board.nsfw == show_nsfw) & (Post.image != "")).order_by(Post.date.desc()).limit(home_images)
    % if images_to_show.count() == 0:
    No images have been uploaded.
    % else:
      % for thread in images_to_show:
        % if thread.is_reply:
            <a href="{{basename}}/{{thread.board.name}}/thread/{{thread.replyrefnum}}#{{thread.refnum}}">
            % if not is_video(thread.filename):
              <img src="{{basename}}/{{thread.image[:-4]}}s.jpg"></a>
            % end
        % else:
          <a href="{{basename}}/{{thread.board.name}}/thread/{{thread.refnum}}" style="text-decoration:none;">
            % if not is_video(thread.filename):
              <img src="{{basename}}/uploads/{{thread.board.name}}/{{thread.refnum}}s.jpg">
            % end
          </a>
        % end
      % end
    % end
  </div>
</div>
% end
% if home_messages:
<div class="Boards">
  <h2 class="Boards-title">Latest messages</h2>
    <ul id="msg-container">
      % messages_to_show = Post.select().join(Board).where(Board.nsfw == show_nsfw).order_by(Post.date.desc()).limit(home_messages)
      % if messages_to_show.count() == 0:
      No messages have been created.
      % else:
        % for thread in messages_to_show:
          <li>
            % if thread.is_reply:
              <a href="{{basename}}/{{thread.board.name}}/thread/{{thread.replyrefnum}}#{{thread.refnum}}">>>/{{thread.board.name}}/{{thread.replyrefnum}}</a><span class="Card-text">{{short_msg(thread.short_content)}}</span>
            % else:
              <a href="{{basename}}/{{thread.board.name}}/thread/{{thread.refnum}}">>>/{{thread.board.name}}/{{thread.refnum}}</a><span class="Card-text">{{short_msg(thread.short_content)}}</span>
            % end
          </li>
        % end
      % end
    </ul>
</div>
% end
<div class="Boards">
  <h2 class="Boards-title">Stats</h2>
  <ul id="stats">
    <li>
      <b>Number of messages :</b> {{number_of_messages}}
    </li>
    <li>
      <b>Active content :</b> {{get_size_format(active_content_size)}}
    </li>
  </ul>
</div>
<footer>
% include('foot')
</footer>
