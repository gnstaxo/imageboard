function window_reply(button, board_name, thread_refnum, post_refnum){

  var maxlength = $(document).find("#texta1").attr("maxlength");
  var maxsize = $(document).find("#max-size").text()
  var chars = post_refnum.length + 3

  $(button).parents(".Thread").before('<div id="reply-window"> <div id="window-header">Reply to thread #'+thread_refnum+'<span class="dclose">X</span></div> <form method="POST" action="/'+board_name+'/thread/'+thread_refnum+'" enctype="multipart/form-data"> <table> <tbody> <tr> <th>Comment</th> <td><textarea maxlength="'+maxlength+'" id="texta2" rows="6" name="content" required>>>'+post_refnum+'\n</textarea><br><small style="opacity:.5;">Max message length: <span id="count2">'+chars+'</span>/'+maxlength+'</small></td> </tr><tr><th>File</th><td><small>'+maxsize+'</small><br><input type="file" name="upload"> <input type="submit" value="Reply"></td> </tr> </tbody> </table> </form> </div>')

  window_width = $("#reply-window").width();
  $("#reply-window").css("left", $(window).width() - window_width - 8);
  $("#reply-window").css("top", ($(window).height() / 2) - ($(window).height() / 4));
  $("#reply-window").attr("for", thread_refnum)

}

function open_window()
{
  var basename = document.URL.split("/").slice(3, 4);
  var board_name = document.URL.split("/").slice(4, 5);
  if (board_name == "")
    board_name = basename
  else
    board_name = basename +"/"+ board_name
  var thread_refnum = $(this).parents(".Thread").attr("id")
  var post_refnum = $(this).text()

  if (Boolean($("#reply-window").length))
  {
    win = $("#reply-window")
    if ( win.attr("for") == thread_refnum )
    {
      a = win.find("textarea").val() + ">>" + post_refnum + "\n";
      win.find("textarea").val(a);
      win.find("#count2").text(win.find("textarea").val().length);
      win.find("textarea").focus();
    }
    else {
      $("#reply-window").detach()
      window_reply(this, board_name, thread_refnum, post_refnum)
    }
  }
  else {
    window_reply(this, board_name, thread_refnum, post_refnum)
  }

  // Make the DIV element draggable:
  dragElement(document.getElementById("reply-window"));

  function dragElement(elmnt) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    if (document.getElementById("window-header")) {
      // if present, the header is where you move the DIV from:
      document.getElementById("window-header").onmousedown = dragMouseDown;
    } else {
      // otherwise, move the DIV from anywhere inside the DIV:
      elmnt.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
      e = e || window.event;
      e.preventDefault();
      // get the mouse cursor position at startup:
      pos3 = e.clientX;
      pos4 = e.clientY;
      document.onmouseup = closeDragElement;
      // call a function whenever the cursor moves:
      document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
      e = e || window.event;
      e.preventDefault();
      // calculate the new cursor position:
      pos1 = pos3 - e.clientX;
      pos2 = pos4 - e.clientY;
      pos3 = e.clientX;
      pos4 = e.clientY;
      // set the element's new position:

      if ( elmnt.offsetTop - pos2 <= 0 ) return
      if ( elmnt.offsetLeft - pos1 <= 0 ) return

      if ( elmnt.offsetTop - pos2 >= $(window).height() - $(elmnt).height()) return

      if ( elmnt.offsetLeft - pos1 >= $(window).width() - $(elmnt).width() - 8) return

      elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
      elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
      // stop moving when mouse button is released:
      document.onmouseup = null;
      document.onmousemove = null;
    }
  }

}

$( document ).ready(function() {

  $("#container").on("click", ".dclose", function(){
    $("#reply-window").detach()
  });

  $("#container").on("click", ".dopen", open_window)

})
