% from bottle import ConfigDict
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="{{basename}}/static/css/global.css">
  <link rel="stylesheet" href="{{basename}}/static/css/styles.css">
  <link rel="shortcut icon" href="{{basename}}/static/favicon.ico">
  <title>{{title}}</title>
  </head>
  <body>
    % include('menu')
    {{!base}}
    <script src="{{basename}}/static/lib/jquery-3.5.1.min.js"></script>
    <script src="{{basename}}/static/lib/markdown.js"></script>
    <script src="{{basename}}/static/lib/autolink-min.js"></script>
    <script src="{{basename}}/static/js/post-markdown.js"></script>
    % if defined('board_name'):
      <script src="{{basename}}/static/js/captcha.js"></script>
      <script src="{{basename}}/static/js/hide-post.js"></script>
      <script src="{{basename}}/static/js/youtube.js"></script>
      <script src="{{basename}}/static/js/quick-reply.js"></script>
      <script src="{{basename}}/static/js/expand-images.js"></script>
      <script src="{{basename}}/static/js/reply-previews.js"></script>
      <script src="{{basename}}/static/js/load-more.js"></script>
      <script src="{{basename}}/static/js/videos.js"></script>
      <script src="{{basename}}/static/js/content-length.js"></script>
      % if f':{board_name}:' in current_user.mod:
        <script src="{{basename}}/static/js/mod-actions.js"></script>
      % end
      % if defined('reports'):
        <script src="{{basename}}/static/lib/sorttable.js"></script>
        <script>
          $("#reports").addSortWidget();
          $("#bans").addSortWidget();
        </script>
      % end
      % if defined('mods'):
        <script src="{{basename}}/static/lib/sorttable.js"></script>
        <script>
  	  $("#mods").addSortWidget();
        </script>
      % end
    % end
  </body>
</html>
