$(document).ready(function() {          
  $('#predict').click(function(){
    $('#predict').css('visibility','hidden');
    if ( $('.progress').css('visibility') == 'hidden' )
      $('.progress').css('visibility','visible');
    else
      $('.progress').css('visibility','hidden');
  });
});