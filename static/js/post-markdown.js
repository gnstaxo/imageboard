function markdown(){

  var text_thread = $( ".Thread-text" ).toArray();

  for ( i = 0; i < text_thread.length; i++) {

    thread_text = $(text_thread[i]).html().replace(/\s+/g, ' ');

    formated_text = markdown_parser(thread_text).autoLink();

    $(text_thread[i]).html(formated_text);

  }

}

function card_text(){

  var text_thread = $( ".Card-text" ).toArray();

  for ( i = 0; i < text_thread.length; i++) {

    thread_text = $(text_thread[i]).html().replace(/\s+/g, ' ');

    formated_text = markdown_parser(thread_text);

    $(text_thread[i]).html(formated_text);

  }
}

$( document ).ready(function() {

  markdown();

  card_text();

});
