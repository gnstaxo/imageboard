% rebase('base.tpl', board_name=board_name, title=f"Catalog of /{board_name}/")
% from models import Post, Board
<h1 class="Title">/{{board_name}}/ - {{board_title}}</h1>
<hr>
<div id="container">
	<ul id="card-list">
	% for thread in threads:
  % file_ext = thread.filename.split(".")[1]
		<li class="Card-item">
		<div class="Card">
      <a href="{{basename}}/{{board_name}}/thread/{{thread.refnum}}">
        % if  file_ext == "mp4" or file_ext == "webm":
          <video width="250">
          <source src="{{basename}}/uploads/{{board_name}}/{{thread.refnum}}.{{file_ext}}" type="video/{{file_ext}}">
          Your browser does not support the video tag.
          </video>
        % else:
          <img src="{{basename}}/uploads/{{board_name}}/{{thread.refnum}}s.jpg">
        % end
      </a>
      <h4 class="Card-title Hilo-title">{{thread.title}}</h4>
      <div class="Card-body">
        <div class="Card-text">
        {{thread.short_content}}        	
        </div>
      </div>
			<div class="Card-footer">
				<b>I:</b> {{board.posts.where((Post.replyrefnum == thread.refnum) & (Post.image != "")).count()}}
				<b>R:</b> {{board.posts.where(Post.replyrefnum == thread.refnum).count()}}
			</div>
		</div>
		</li>
	% end
	</ul>
</div>
<footer>
% include('menu')
% include('foot')
</footer>
