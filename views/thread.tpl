% from utils import author_color, image_size, is_video
% from models import Post, Board
<div class="Thread" id="{{thread.refnum}}">
  <div class="Thread-meta">
  [<span class="hide-thread" title="Hide thread">=</span>]
  <span class="image-data">File:
  <a href="{{basename}}/{{thread.image}}" title="{{thread.filename}}">
  % if len(thread.filename.split(".")[0]) > 20:
    {{thread.filename[:20]}}(...).{{thread.filename.split(".")[-1]}}
  % else:
    {{thread.filename}}
  % end
  </a>
  % if not is_video(thread.filename):
    [<a href="https://www.google.com/searchbyimage?image_url={{basename}}/uploads/{{thread.image}}"class="gsearch">S</a>]
  % end
    ({{image_size(thread.image)}})
    </span>
    </div>
    % if is_video(thread.filename):
      <video width="250" height="250" class="Thread-video">
      <source src="{{basename}}/{{thread.image}}" type="video/{{thread.image[-3:]}}">
      Your browser does not support the video tag.
      </video>
    % else:
      <img class="Thread-image" src="{{basename}}/uploads/{{board_name}}/{{thread.refnum}}s.jpg">
    % end
    <div class="Thread-info">
    <input type="checkbox" name="{{thread.refnum}}" value="delete">
    <span class="Hilo-title">{{thread.title}}</span>
    <span class="Author" style="background-color: {{author_color(thread.author.name)}};">{{thread.author.name}}</span>
    % if thread.by_mod:
    <span class="role">Mod</span>
    % end
  {{thread.date}} No. <span class="dopen">{{thread.refnum}}</span>
  % if thread.pinned:
    <img class="pin" src="{{basename}}/static/img/sticky.gif"></img>
  % end
  % if thread.closed:
    <img class="pin" src="{{basename}}/static/img/locked.gif"></img>
  % end
  % if not is_detail:
    <a class="btn Thread-repbtn" href="{{basename}}/{{board_name}}/thread/{{thread.refnum}}">Reply</a>
  % end
  % if f':{board_name}:' in current_user.mod:
    <div class="dropdown">
      <button class="dropbtn">▶</button>
      <div class="myDropdown dropdown-content">
        <a class="dropin" href="{{basename}}/{{board_name}}/thread/{{thread.refnum}}/pin">Pin</a>
        <a class="dropc" href="{{basename}}/{{board_name}}/thread/{{thread.refnum}}/close">Close</a>
      </div>
    </div> 
  % end
  </div>
  <div class="Thread-text">
  % include('thread_text', board_name=board_name, board=board)
  </div>
  <div class="Replies">
  % query = board.posts.where(Post.replyrefnum == thread.refnum).order_by(Post.refnum.asc())
  % replies = query if is_detail else query.offset(query.count() - 4)
  % if not is_detail and query.count() > 4:
    <span class="load-replies btn">Load {{query.count() - 4}} replies</span>
  % end
  % for reply in replies:
  % include('reply', reply=reply)
  % end
  </div>
</div>
