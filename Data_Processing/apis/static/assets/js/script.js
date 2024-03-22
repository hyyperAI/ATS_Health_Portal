function include(file) {
  const script = document.createElement('script');
  script.src = `static/assets/js/componentss/${file}`;
  console.log(script.src)
  script.type = 'text/javascript';
  script.defer = false;
  const head = document.getElementsByTagName('head')[0];
  console.log(head)
  head.appendChild(script);
}


// Bot pop-up intro
document.addEventListener("DOMContentLoaded", () => {
  const elemsTap = document.querySelector(".tap-target");
  // eslint-disable-next-line no-undef
  const instancesTap = M.TapTarget.init(elemsTap, {});
  instancesTap.open();
  setTimeout(() => {
    instancesTap.close();
  }, 10000);
});

/* import components */
include('index.js');
window.addEventListener('load', () => {
  // initialization
  $(document).ready(() => {
    // Bot pop-up intro
    $("div").removeClass("tap-target-origin");

    $(".dropdown-trigger").dropdown();

    $(".modal").modal();

  // Toggle the chatbot screen
  $("#profile_div").click(() => {
    $(".profile_div").toggle();
    $(".widget").toggle();
    //Increase height to 550px
    $("#chatbotiframe").css("height", "550px");
  });


  // clear function to clear the chat contents of the widget.
  $("#clear").click(() => {
    $(".chats").fadeOut("normal", () => {
      $(".chats").html("");
      $(".chats").fadeIn();
    });
  });

  // close function to close the widget.
  $("#closeChat").click(() => {
    $(".profile_div").toggle();
    $(".widget").toggle();
    $("#chatbotiframe").css("height", "100px");
    scrollToBottomOfResults();
  });
});
});
