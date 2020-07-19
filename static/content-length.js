$( document ).ready( function() {

  $("#texta1").keyup(function(){
    $("#count1").text($(this).val().length);
  });

  $("#container").on("keyup", "#texta2", function(){
    $("#count2").text($(this).val().length);
  });

});
