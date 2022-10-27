function passing_per() {
    let q_amount = document.getElementById('id_question_amount').value;
    let pass_score = document.getElementById('id_passing_score').value;
    if (parseInt(q_amount) < parseInt(pass_score)) {
        document.getElementById('id_passing_score').value = q_amount;
        pass_score = document.getElementById('id_passing_score').value;
    }
    document.getElementById("perc_score").innerHTML = 100*pass_score/q_amount + "%";
    }
    passing_per();
    document.getElementById("id_question_amount").addEventListener("change", passing_per);
    document.getElementById("id_passing_score").addEventListener("change", passing_per);

    var acc = document.getElementsByClassName("tog");
    var i;
    
    for (i = 0; i < acc.length; i++) {
      acc[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var panel = this.nextElementSibling;
        if (panel.style.maxHeight) {
          panel.style.maxHeight = null;
        } else {
          panel.style.maxHeight = panel.scrollHeight + "px";
        }
      });
    }