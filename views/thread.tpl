% from utils import author_color, image_size, is_video
<div class="Thread" id="{{thread.refnum}}">
  <div class="Thread-meta">
  [<span class="hide-thread" title="Hide thread">=</span>]
  <span class="image-data">File:
  <a href="/{{thread.image}}" title="{{thread.filename}}">
  % if len(thread.filename.split(".")[0]) > 20:
    {{thread.filename[:20]}}(...).{{thread.filename.split(".")[-1]}}
  % else:
    {{thread.filename}}
  % end
  </a>
  % if not is_video(thread.filename):
    [<a href="https://www.google.com/searchbyimage?image_url=http://192.168.1.104/{{thread.image}}"class="gsearch">S</a>]
  % end
    ({{image_size(thread.image)}})
    </span>
    </div>
    % if is_video(thread.filename):
      <video width="250" height="250" class="Thread-video">
      <source src="/{{thread.image}}" type="video/{{thread.image[-3:]}}">
      Your browser does not support the video tag.
      </video>
    % else:
      <img class="Thread-image" src="/uploads/{{board_name}}/{{thread.refnum}}s.jpg">
    % end
    <div class="Thread-info">
    <input type="checkbox" name="{{thread.refnum}}" value="delete">
    <span class="Hilo-title">{{thread.title}}</span>
    <span class="Author" style="background-color: {{author_color(thread.author)}};">{{thread.author}}</span>
    % if thread.by_mod:
    <span class="role">Mod</span>
    % end
  {{thread.date}} No. <span class="dopen">{{thread.refnum}}</span>
  % if thread.pinned:
    <img class="pin" src="/static/img/sticky.gif"></img>
  % end
  % if thread.closed:
    <img class="pin" src="/static/img/locked.gif"></img>
  % end
  % if not is_detail:
    <a class="btn Thread-repbtn" href="/{{board_name}}/thread/{{thread.refnum}}">Reply</a>
  % end
  % if f':{board_name}:' in current_user.mod:
    <div class="dropdown">
      <button class="dropbtn">▶</button>
      <div class="myDropdown dropdown-content">
        <a class="dropin" href="/{{board_name}}/thread/{{thread.refnum}}/pin">Pin</a>
        <a class="dropc" href="/{{board_name}}/thread/{{thread.refnum}}/close">Close</a>
      </div>
    </div> 
  % end
  </div>
  <div class="Thread-text">
  % include('thread_text', board_name=board_name, board=board)
  </div>
  <div class="Replies">
  % replies = thread.replies if is_detail else thread.replies[-4:]
  % if not is_detail and thread.reply_count > 4:
    <span class="load-replies btn">Load {{thread.reply_count - 4}} replies</span>
  % end
  % for reply in replies:
  % include('reply', reply=reply)
  % end
  </div>
</div>
