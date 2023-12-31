$( document ).ready(function(){
  $("#btnPost").click((e)=>{
    if ($("#captcha").length){
      $(".Formulario").submit()
    } else {
      e.preventDefault()
      $.ajax({
        url: "/captcha",
        dataType: "json",
        method: "GET",
        success: function(data){
          var countDownDate = new Date(data['time_exp']).getTime()
          $('.Formulario > table > tbody > tr').eq(1).after(`
            <tr id="captcha">
              <td><img src="/captchaimg/${data['id']}"></td>
              <td><span id="timer">5m 00s</span><br><input type="text" name="captchares">
              <input type="hidden" name="captchaid" value="${data['id']}">
            </tr>
          `)
          // Update the count down every 1 second
          var x = setInterval(function() {

            // Get today's date and time
            var now = new Date().getTime();

            // Find the distance between now and the count down date
            var distance = countDownDate - now;

            // Time calculations for days, hours, minutes and seconds
            var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            var seconds = Math.floor((distance % (1000 * 60)) / 1000);

            // Display the result in the element with id="demo"
            document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s ";

            // If the count down is finished, write some text
            if (distance < 0) {
              clearInterval(x);
              document.getElementById("timer").innerHTML = "EXPIRED";
            }
          }, 1000);
        }
      })
    }
  })
})
