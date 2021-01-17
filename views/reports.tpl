% rebase('base', title="Moderation")
% from models import Post, Board
<h3 class="Title">Reports</h3>
<table class="Reports" id="reports">
  <thead>
    <tr>
      <th>No.</th>
      <th>Author</th>
      <td>Title</td>
      <th>Reason</th>
      <th>Date</th>
      <td></td>
    </tr>
  </thead>
  <tbody>
  % for report in reports:
    % thread = board.posts.where(Post.refnum == report.refnum).get()
    <tr>
      <td>{{report.refnum}}</td>
      <td>{{thread.author.name}}</td>
      % if thread.is_reply:
        <td>{{Post.get((Post.refnum == thread.replyrefnum) & (Post.board_id == board.id)).title}}	
      % else:
        <td>{{thread.title}}</td>
      % end
      <td>{{report.reason}}</td>
      <td>{{report.date}}</td>
      % if thread.is_reply:
        <td style="text-align: center;">[<a href="{{basename}}/{{board.name}}/thread/{{thread.replyrefnum}}#{{report.refnum}}">View</a>]</td>
      % else:
        <td style="text-align: center;">[<a href="{{basename}}/{{board.name}}/thread/{{report.refnum}}">View</a>]
      % end
    </tr>
  % end
  </tbody>
</table>
<h3 class="Title">Bans</h3>
<form class="Ban-form" action="{{basename}}/{{board_name}}/ban" method="POST">
  <input name="user" type="text" placeholder="user">
  <select name="reason">
    <option selected disabled>Reason:</option>
    % for reason in reasons:
      <option value="{{reason}}">{{reason}}</option>   
    % end
  </select>
  <input type="submit" value="Ban">
</form>
<table class="Reports" id="bans">
  <thead>
    <tr>
      <th>IP</th>
      <th>Last user</th>
      <th>Ban reason</th>
      <th>Date</th>
      <td></td>
    </tr>
  </thead>  
  <tbody>
    % for ban in bans:
      <tr>
      	<td>{{ban.ip}}</td>
      	<td>{{ban.name}}</td>
      	<td>{{ban.ban_reason}}</td>
      	<td>{{ban.ban_date}}</td>
        <td>
          <form action="{{basename}}/{{board_name}}/unban/{{ban.name}}" method="POST">
            <input type="submit" name="dall" value="Delete all posts">
            <input type="submit" name="unban" value="Unban">
          </form>
        </td>
      </tr>
    % end
  </tbody>
</table>
