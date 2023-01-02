% rebase('base', title=f"/{board_name}/ - {board_title}")
<h2 class="Title">/{{board_name}}/<br>{{board_title}}
 % if board.nsfw:
  [<span class="nsfw">NSFW</span>]
 % end
</h2>
<hr>
<form class="Formulario" method="POST" action="{{basename}}/{{board_name}}/" enctype="multipart/form-data">
  <table>
    <tbody>
      <tr>
        <th>Title</th>
        <td>
          <input type="text" name="title" required> <input type="submit" value="Post">
        </td>
      </tr>
      <tr>
        <th>Comment</th>
        <td><textarea id="texta1" maxlength="{{maxlength}}" rows="6" name="content" required></textarea><br><small style="opacity:.5;">Max message length: <span id="count1">0</span>/{{maxlength}}</small></td>
      </tr>
      <tr>
        <th>File</th>
        <td><small id="max-size">Max file size: {{max_file_size}}MB.</small><br><input type="file" name="upload" required></td>
      </tr>
    </tbody>
  </table>
</form>

<div id="container">
<form action="{{basename}}/{{board_name}}/delete" method="POST">
% for thread in threads:
% include('thread', thread=thread, board_name=board_name, board=board)
% end
</div>
<hr>
<footer>
% include('pagination', current_page=current_page, board_name=board_name)
% include('bottom')
</footer>
