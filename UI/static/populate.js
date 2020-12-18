function get(name){
   if(name=(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(location.search))
      return decodeURIComponent(name[1]);
}
  window.onload = function(){
       document.getElementById("clientid").value = get('clientid');
}
