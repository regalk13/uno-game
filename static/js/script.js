$(window).load(function () {
  $(".card-online").click(function () {
    $('.hover_bkgr_fricc').show();
    console.log("click");
  });
  $('.hover_bkgr_fricc').click(function () {
    $('.hover_bkgr_fricc').hide();
  });
  $('.popupCloseButton').click(function () {
    $('.hover_bkgr_fricc').hide();
  });
});
