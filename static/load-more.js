function full_thread(){
  var href = $(this).parents(".Thread").children(".Thread-info").children(".btn").attr("href");
  var container = $(this).parent()
  var post_id = $(this).parents(".Reply,.Thread").attr("id")
  $.ajax({
    url: href,
    type: 'GET',
    success: function(data){
      container.html(markdown_parser($(data).find("#"+post_id).find(".Thread-text").html().replace(/\s+/g, ' ').autoLink()))
      container.append('<span class="btn less-thread">Show less</span>')
    }
  });
}

function load_replies(){
  var href = $(this).parent().siblings(".Thread-info").children(".btn").attr("href");
  var container = $(this).parents(".Replies")
  $.ajax({
    url: href,
    type: 'GET',
    success: function(data){
      container.html('<span class="less-replies btn">Less replies</span>' + markdown_parser($(data).find(".Replies").html().replace(/\s+/g, ' ').autoLink()));
    }
  });
}

function less_replies(){
  var href = document.URL
  var thread_id = $(this).parents(".Thread").attr("id");
  var container = $(this).parents(".Replies")
  $.ajax({
    url: href,
    type: 'GET',
    success: function(data){
      container.html(markdown_parser($(data).find("#" + thread_id).children(".Replies").html().replace(/\s+/g, ' ').autoLink()))
    }
  });
}

function less_thread(){
  var href = document.URL
  var thread_id = $(this).parents(".Reply,.Thread").attr("id");
  var container = $(this).parent()
  $.ajax({
    url: href,
    type: 'GET',
    success: function(data){
      container.html(markdown_parser($(data).find("#" + thread_id).find(".Thread-text").html().replace(/\s+/g, ' ').autoLink()))
    }
  });
}

$( document ).ready(function() {
  $("#container").on("click", ".full-thread", full_thread);
  $("#container").on("click", ".less-thread", less_thread);
  $("#container").on("click", ".load-replies", load_replies);
  $("#container").on("click", ".less-replies", less_replies);
});
