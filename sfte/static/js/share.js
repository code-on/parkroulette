    // Facebook
    function fb_top(id, text_id){
        if(typeof(id)==='undefined') id='fb-top-link';
        if(typeof(text_id)==='undefined') text_id='#share-top-text';
    var link = document.getElementById(id);
    var url="http://www.parkroulette.com"
    var facebook="https://www.facebook.com/sharer/sharer.php?s=100&p[url]=";
    var sharetitle=encodeURIComponent(document.title)
    var sharetxt=encodeURIComponent($(text_id).text());
    link.href=facebook+url+'&p[title]='+sharetitle+'&p[summary]='+sharetxt;
  }
    // Twitter
   function twitter_top(id, text_id){
       if(typeof(id)==='undefined') id='tweeter-top-link';
       if(typeof(text_id)==='undefined') text_id='#share-top-text';
    var link = document.getElementById(id);
    var url="http://www.parkroulette.com"
    var twitter="https://twitter.com/share?url=";
    var sharetxt=encodeURIComponent($(text_id).text());
    link.href=twitter+url+"&text="+sharetxt;
  }
    // Google +1
   function googleone_top(id){
    if(typeof(id)==='undefined') id='googleone-link';
    var link = document.getElementById(id);
    var url="http://www.parkroulette.com";
    var google="https://plus.google.com/share?url=";
    link.href=google+url;
  }
  function limitText(limitField, limitCount, limitNum) {
    if (limitField.value.length > limitNum) {
      limitField.value = limitField.value.substring(0, limitNum);
        $("#textarea").text(limitField.value);
    } else {
      $("#textarea").text(limitField.value);
      $(limitCount).text(limitNum - limitField.value.length);
    }
  }
