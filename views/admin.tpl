% rebase('base', title="Administration")
% from models import Board
<h3 class="Title">Mods</h3>
<form class="Ban-form" action="{{basename}}/new_mod" method="POST">
	<input name="user" type="text" placeholder="user">
  <select name="board">
    % for board in Board.select():
    <option value="{{board.name}}">{{board.name}}</option>
    % end
  </select>
	<input type="submit" value="Add">
</form>
<table class="Reports" id="mods">
  <thead>
    <tr>
      <th>IP</th>
      <th>User</th>
      <td>Mod</td>
      <td>Role</td>
      <td></td>
    </tr>
  </thead>  
  <tbody>
    % for mod in mods:
      <tr>
      	<td>{{mod.ip}}</td>
      	<td>{{mod.name}}</td>
      	<td>{{mod.mod.replace("::", ", ").strip(':')}}</td>
        <td>
          <form action="{{basename}}/mod" method="POST">
            <select name="board">
              % for board in Board.select():
              <option value="{{board.name}}">{{board.name}}</option>
              % end
            </select>
	    <input type="text" name="user" value="{{mod.name}}" hidden>
            <input type="submit" name="rm" value="Remove">
            <input type="submit" name="add" value="Add">
        </td>
        <td>
            <input type="submit" name="rmall" value="Remove all">
          </form>
        </td>
      </tr>
    % end
  </tbody>
</table>
<h3 class="Title">Boards</h3>
<form class="Ban-form" action="{{basename}}/add_board" method="POST">
	<input name="name" type="text" placeholder="board name" required>
	<input name="title" type="text" placeholder="board title" required>
	NSFW: <input name="nsfw" type="checkbox" placeholder="board title">
	<input type="submit" value="Add">
</form>
<table class="Reports">
  <thead>
    <tr>
      <td>Board</td>
      <td>Title</td>
      <td id="view-field"></td>
    </tr>
  </thead>
  <tbody>
    % for board in boards:
      <tr>
        <td>{{board.name}}</td>
        <td>{{board.title}}</td>
        <td>
          <form action="{{basename}}/del_board/{{board.name}}" method="POST">	
            <input type="submit" value="Delete"></input>
          </form>
        </td>
      </tr>
    % end
  </tbody>
</table>
<form action="{{basename}}/logout" method="POST" style="text-align: center;margin-top:10px;">
  <input type="submit" value="Log out">
</form>
