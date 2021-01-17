% from utils import author_color
% from json import loads
% from models import Post
<div id="{{reply.refnum}}" class="Reply">
	<div class="Respuesta-flecha">>></div>
	<div class="Respuesta-cuerpo">
  <input type="checkbox" name="{{reply.refnum}}" value="delete">
	<span class="Author" style="background-color: {{author_color(reply.author.name)}};">{{reply.author.name}}</span>
	    % if reply.by_mod:
		    <span class="role">Mod</span>
	    % end
	    % if Post.get(Post.refnum == reply.replyrefnum).author.name == reply.author.name:
		    <span class="op">OP</span>
	    % end
	{{reply.date}} <a style="color:black;" href="{{basename}}/{{board_name}}/thread/{{reply.replyrefnum}}#{{reply.refnum}}">No.</a> <span class="dopen">{{reply.refnum}}</span>
  [<span class="hide-reply" title="Hide reply">=</span>]
	% if reply.image:
	<div class="Reply-meta">File:
		<a href="{{basename}}/{{reply.image}}" title="{{reply.filename}}">
		% if len(reply.filename.split(".")[0]) > 20:
		{{reply.filename[:20]}}(...).{{reply.filename.split(".")[-1]}}
		% else:
		{{reply.filename}}
		% end
		</a>
    % if not is_video(reply.filename):
      [<a href="{{basename}}https://www.google.com/searchbyimage?image_url=http://192.168.1.104/{{reply.image}}"class="gsearch">S</a>]
    % end
    % if not is_video(reply.filename):
      ({{image_size(reply.image)}})
    % end
	</div>
  % if is_video(reply.filename):
    <video class="Reply-video" width="250" height="250">
      <source src="{{basename}}/{{reply.image}}" type="video/{{reply.image[-3:]}}">
      Your browser does not support the video tag.
    </video>
  % else:
    <img class="Reply-image" src="{{basename}}/uploads/{{board_name}}/{{reply.refnum}}s.jpg">
  % end
	% end
	<div class="Thread-text">
	% include('thread_text', thread=reply)
	</div>
	<div style="clear:both;"></div>
  % replylist = loads(reply.replylist)
  % if replylist:
    <div class="Reply-list">
      <span class="reps">Replies:</span>
      % for i in range(len(replylist)):
        <a href="{{basename}}/{{board_name}}/thread/{{reply.replyrefnum}}#{{replylist[i]}}" class="reps reference">>>{{replylist[i]}}</a>
      % end
    </div>
  % end
	</div>
</div>
