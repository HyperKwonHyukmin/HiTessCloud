$(function(){  
  // Trigger
  $('.trigger').click(function(){
    $(this).toggleClass('active')
    $('.gnb').toggleClass('active')
  })
  $('.gnb a').click(function(){
    $('.gnb, .trigger').removeClass('active')
  })
  
  // Sliding jQuery
  $('.gnb a, .gototop').click(function(e){
    $.scrollTo(this.hash || 0, 800);
    e.preventDefault();
  })
  
  // Header Scroll Change
  $(window).scroll(function(){
    if($(window).scrollTop() > 50) {
      $('header, .gototop').addClass('active')
    }
    else {
      $('header, .gototop').removeClass('active')
    }    
  })
  
  // Slick.js
  $('.myslider').slick({
    dots: true,
    infinite: true,
    speed: 300,
    slidesToShow: 2,
    slidesToScroll: 2, 
    autoplay: true   
  });

  $('.myshortcut').slick({
    dots: true,
    infinite: true,
    speed: 300,
    slidesToShow: 3,
    slidesToScroll: 3,   
  });

})
