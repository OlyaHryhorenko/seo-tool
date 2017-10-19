$('.delete-item').click(function(e){
    e.preventDefault();
    if (confirm("Are you sure?") == false) {
        return false;
    }
    var $this = $(this);
    $this.parent().css('backgroundColor', '#ccc');
    var url = $(this).attr('href');
    $.ajax({
        url: url,
        success: function(response){
           if (response = true) {

                $this.parent().hide();
           }
        }
    })

});


 $(document).ready(function() {

   var docHeight = $(window).height();
   var footerHeight = $('footer').height();
   var footerTop = $('footer').position().top + footerHeight;

   if (footerTop < docHeight) {
    $('footer').css('margin-top', (docHeight - footerTop) + 'px');
   }
  });

//  function check_status(){
//    var item = $(this);
//    var id = item.getAttribute('data-id');
//    $.ajax({
//            url: '/get-status?id='+id,
//            success: function(response){
//                console.log(response);
//                $(this).html(response);
//            }
//        })
//  }

//  $(document).ready(function() {
//    var arr = [];
//    var item = $(".check_status");
//
//    console.log(item.length);
//    for (i = 0; i <= item.length; i++) {
//        var x = item[i].getAttribute('data-id');
//         console.log(item[i]);
//        $.ajax({
//            url: '/get-status?id='+x,
//            success: function(response){
//                console.log(response);
//            }
//        })
//    }
//
//  })