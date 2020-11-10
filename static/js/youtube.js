function youtube(){

  if ($(this).text() == "Play")
  {
    $(this).text("Hide")
    url = $(this).siblings(".yt-url").text().slice(-11);
    $(this).parent().siblings(".yt-container").children("iframe").detach()
    $(this).parent().siblings(".yt-container").children(".play").text("Play")
    $(this).parent().append('<iframe width="320" height="215" style="float:left; margin-right: 5px;" src="https://www.youtube.com/embed/' + url + '"></iframe>')

    if (!$(this).parents(".Respuesta-cuerpo").length){
      $(this).parents(".Thread").children(".Replies").before('<div class="clear" style="clear:both;"></div>')
    }
  }
  else
  {
    $(this).text("Play");
    $(this).siblings("iframe").detach()
    $(this).parents(".Thread").children(".clear").detach()
  }

}

$( document ).ready(function() {

  $("#container").on("click", ".play", youtube);

});
