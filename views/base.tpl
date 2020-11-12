<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="/static/css/global.css">
  <link rel="stylesheet" href="/static/css/styles.css">
  <link rel="shortcut icon" href="/static/favicon.ico">
  <title>{{title}}</title>
  </head>
  <body>
    % include('menu')
    {{!base}}
    <script src="/static/lib/jquery-3.5.1.min.js"></script>
    <script src="/static/lib/markdown.js"></script>
    <script src="/static/lib/autolink-min.js"></script>
    <script src="/static/js/post-markdown.js"></script>
    % if defined('board_name'):
      <script src="/static/js/hide-post.js"></script>
      <script src="/static/js/youtube.js"></script>
      <script src="/static/js/quick-reply.js"></script>
      <script src="/static/js/expand-images.js"></script>
      <script src="/static/js/reply-previews.js"></script>
      <script src="/static/js/load-more.js"></script>
      <script src="/static/js/videos.js"></script>
      <script src="/static/js/content-length.js"></script>
      % if f':{board_name}:' in current_user.mod:
        <script src="/static/lib/mod-actions.js"></script>
      % end
      % if defined('reports'):
        <script src="/static/lib/sorttable.js"></script>
        <script>
          $("#reports").addSortWidget();
          $("#bans").addSortWidget();
        </script>
      % end
      % if defined('mods'):
        <script src="/static/lib/sorttable.js"></script>
        <script>
  	  $("#mods").addSortWidget();
        </script>
      % end
    % end
  </body>
</html>
