% rebase('base', board_name=board_name, title=thread.title)
% from utils import image_size
<h3 class="Title">{{thread.title}}</h3>
<hr>
<form class="Formulario" method="POST" action="{{basename}}/{{board_name}}/thread/{{thread.refnum}}" enctype="multipart/form-data">
  <table>
    <tbody>
      <tr>
        <th>Comment</th>
        <td><textarea maxlength="{{maxlength}}" id="texta1" rows="6" name="content" required></textarea><br><small style="opacity:.5;">Max message length: <span id="count1">0</span>/{{maxlength}}</small></td>
      </tr>
      <tr>
        <th>File</th>
        <td><small>Max file size: {{max_file_size}}MB.</small><br><input type="file" name="upload"> <input type="submit" value="Reply"></td>
      </tr>
    </tbody>
  </table>
</form>
<div id="container">
<form action="{{basename}}/{{board_name}}/delete" method="POST">
	<div style="clear:both;"></div>
	% include('thread', thread=thread)	
</div>
<hr>
<footer>
% include('bottom')
</footer>
