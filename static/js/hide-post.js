function load_hidden_posts(){

  var hidden = JSON.parse(window.localStorage.getItem("hidden_posts"))
  var board_name = document.URL.split("/").slice(3, 4)[0];

  if (hidden == null){
    hidden = Object({[board_name]:[]})
    window.localStorage.setItem("hidden_posts", JSON.stringify(hidden))
  }
  else if (hidden[board_name] == undefined){
    hidden[board_name] = []
    window.localStorage.setItem("hidden_posts", JSON.stringify(hidden))
  }
  else {
    var thread = $( ".Thread" ).toArray();
    for ( i = 0; i < thread.length; i++) {
      if (hidden[board_name].includes(parseInt($(thread[i]).attr("id"))))
      {
        $(thread[i]).find(".Thread-image,.Thread-video,.Thread-text,.Replies,.Thread-repbtn").hide()
        $(thread[i]).children(".Thread-meta").children(".image-data").hide()
        $(thread[i]).children(".Thread-meta,.Thread-info").css("display", "inline-block")
        $(thread[i]).children(".Thread-meta").children(".hide-thread").text("+")
      }
    }
    var reply = $( ".Reply" ).toArray();
    for ( i = 0; i < reply.length; i++) {
      if (hidden[board_name].includes(parseInt($(reply[i]).attr("id"))))
      {
        $(reply[i]).find(".Thread-text,.Reply-meta,.Reply-image,.Reply-video,.Reply-list").hide();
        $(reply[i]).find(".hide-reply").text("+");

        window.localStorage.setItem("hidden_posts", JSON.stringify(hidden));
      }
    }
  }
}

function toggle_post_hide(){

  var thread_id = $(this).parents(".Thread").attr("id");

  var hidden = JSON.parse(window.localStorage.getItem("hidden_posts"))

  var board_name = document.URL.split("/").slice(3, 4);

  if ( $(this).text() == "=" ) {

    hidden[board_name].push(parseInt(thread_id))

    $(this).parent().css("display", "inline");
    $(this).siblings(".image-data").hide();
    $(this).parent().siblings(".Thread-info").css("display", "inline-block");
    $(this).parents(".Thread").find(".Thread-image,.Thread-text,.Replies,.Thread-video,.Thread-repbtn").hide();

    $(this).text("+");

    window.localStorage.setItem("hidden_posts", JSON.stringify(hidden));
  }
  else {

    hidden[board_name].splice(hidden[board_name].indexOf(parseInt(thread_id)))

    $(this).parent().css("display", "")
    $(this).siblings(".image-data").show()
    $(this).parent().siblings(".Thread-info").css("display", "")
    $(this).parents(".Thread").find(".Thread-image,.Thread-text,.Replies,.Thread-video,.Thread-repbtn").show()

    $(this).text("=")

    window.localStorage.setItem("hidden_posts", JSON.stringify(hidden));
  }
}

function hide_reply(){ 
  var reply_id = $(this).parents(".Reply").attr("id");

  var hidden = JSON.parse(window.localStorage.getItem("hidden_posts"))

  var board_name = document.URL.split("/").slice(3, 4);

  if ( $(this).text() == "=" ) {

    hidden[board_name].push(parseInt(reply_id))

    $(this).siblings(".Thread-text,.Reply-meta,.Reply-image,.Reply-video,.Reply-list").hide();

    $(this).text("+");

    window.localStorage.setItem("hidden_posts", JSON.stringify(hidden));
  }
  else {

    hidden[board_name].splice(hidden[board_name].indexOf(parseInt(reply_id)))

    $(this).siblings(".Thread-text,.Reply-meta,.Reply-image,.Reply-video,.Reply-list").show();

    $(this).text("=");

    window.localStorage.setItem("hidden_posts", JSON.stringify(hidden));
  }
}

$( document ).ready(function() {

  load_hidden_posts()

  $("#container").on("click", ".hide-thread", toggle_post_hide)

  $("#container").on("click", ".hide-reply", hide_reply)

});
