function show_preview(){

    var href = $(this).attr("href");
    var id = $(this).text().replace(/[>>\D]/g, '');

    var is_thread = href.split("/").slice(-1)[0].includes("#")

    elmnt = this;

    $(this).after('<div class="Reply-floating"><span style="text-align:center;">[...]</span></div>');

    jQuery.ajax({
      url: href,
      method: 'GET',
      success: function(data){
        if (is_thread){
          var preview = $(data).find("#"+id).children(".Respuesta-cuerpo");
          preview.find(".hide-reply").detach();
          preview.find(".gsearch").detach();
          var thread = preview.html().replace(/\[\]/g, "");
          preview = markdown_parser(thread).autoLink();
        }
        else
        {
          var preview = $(data).find("#"+id)
          preview.children(".Replies").detach()
          ti = preview.children(".Thread-info")
          ti.css("margin", 0)
          preview.children(".Thread-info").detach()
          preview.children(".Thread-meta").before(ti)
          preview.find("button").detach()
          preview.find(".hide-thread").detach()
          preview.find(".gsearch").detach()

          var thread = preview.html().replace(/\[\]/g, "");
          preview = thread;
        }
        $(elmnt).siblings(".Reply-floating").html(preview);
      }
    });
}

$( document ).ready(function(){

  $("#container").on("mouseenter", ".reference", show_preview)

  $("#container").on("mouseleave", ".reference", function(){
    $(this).siblings(".Reply-floating").detach()
  });

});
