$(document).ready(function(){
    $('.menu-bar li').each(function(e){
        var $me = $(this);
        var $a = $me.find('a');
        if(window.location.pathname == $a.attr('href')){
            $me.addClass('active');
        }
    });
});

// $(document).ready(function(){
//     resizeDiv();
// });
//
// window.onresize = function(event) {
//     resizeDiv();
// }
//
// function resizeDiv() {
//     vpw = $(window).width();
//     vph = $(window).height();
//     $('menusize').css({'height': vph + 'px'});
// }