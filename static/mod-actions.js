function dropdown()
{
    /* When the user clicks on the button,
    toggle between hiding and showing the dropdown content */
    $(this).siblings(".myDropdown").toggleClass("show");
    $(this).toggleClass("dropbtn-open");

    event.preventDefault();

    boton = this;

    // Close the dropdown menu if the user clicks outside of it
    window.onclick = function(event) {
      if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
          var openDropdown = dropdowns[i];
          if (openDropdown.classList.contains('show')) {
            $(boton).removeClass("dropbtn-open");
            openDropdown.classList.remove('show');
          }
        }
      }
    } 
}

$( document ).ready(function() {
  $("#container").on("click", ".dropbtn", dropdown)
});
