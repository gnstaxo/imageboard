function expand_images(){

  thread_width = $(this).parents( ".Thread" ).width();

  image_full = $(this).siblings(".Thread-meta").children(".image-data").children().attr("href");

  image_small = image_full.split(".")[0] + "s.jpg";

  if ($(this).attr("src") == image_small){

    $(this).attr("src", image_full);
    $(this).addClass("full-image");
    if(window.matchMedia('(max-width: 600px)').matches){

      $(this).css("max-width", "100%");
      $(this).css("max-height", "initial");

    } else {
      $(this).css("max-width", thread_width / 2);
    }

  } 
  else {

    $(this).attr("src", image_small);
    $(this).removeClass("full-image");

    if(window.matchMedia('(max-width: 600px)').matches)
      $(this).css("max-height", "");

    $(this).css("max-width", "");

  }
  
}

function expand_image_reply(){
  thread_width = $(this).parents( ".Respuesta-cuerpo" ).width();

  image_full = $(this).siblings(".Reply-meta").children("a").attr("href");

  image_small = image_full.split(".")[0] + "s.jpg";

  if ($(this).attr("src") == image_small){

    $(this).attr("src", image_full);
    $(this).addClass("full-image");
    $(this).css("max-width", thread_width);
    if(window.matchMedia('(max-width: 600px)').matches)
      $(this).css("max-height", "initial");
    $(this).css("margin-right", 0);

  } 
  else {

    $(this).attr("src", image_small);
    $(this).removeClass("full-image");
    $(this).css("max-width", "");
    if(window.matchMedia('(max-width: 600px)').matches)
      $(this).css("max-height", "");
    $(this).css("margin-right", 5);

  }
}

$( document ).ready(function() {

  $("#container").on("click", ".Thread-image", expand_images)
  $("#container").on("click", ".Reply-image", expand_image_reply)

});
