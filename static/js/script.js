$(document).ready(function () {

  $('#open-join-room').click(function () {
    $('#model-join-room').css('transform', 'scale(1)');
  });

  $('#open-create-room').click(function () {
    $('#model-create-room').css('transform', 'scale(1)');
  });

  $('#close-join-room').click(function () {
    $('#model-join-room').css('transform', 'scale(0)');
  });

  $('#close-create-room').click(function () {
    $('#model-create-room').css('transform', 'scale(0)');
  });

});
