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
