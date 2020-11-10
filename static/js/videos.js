function video_controls(){
  $(this).attr("controls", "")
  $(this).attr("autoplay", "")
}

$( document ).ready(function() {
  $("#container").on("click", "video", video_controls)
});
