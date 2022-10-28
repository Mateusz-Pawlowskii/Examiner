let x = setInterval(function() {

    // Get today's date and time
    let distanceNow = new Date().getTime() - now;
  
    // Find the distance between now and the count down date
    let distance = countDownDate - now - distanceNow;
  
    // Time calculations for minutes and seconds
    let minutes = Math.floor((distance / (1000 * 60)));
    let seconds = Math.floor((distance % (1000 * 60)) / 1000);
  
    // Display the result in the element with id="timer"
    document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s ";
  
    // If the count down is finished, write some text
    if (distance < 0) {
      clearInterval(x);
      document.getElementById("timer").innerHTML = "Koniec";
      document.getElementById("timeout").click()
    }
  }, 1000);