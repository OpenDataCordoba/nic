$( document ).ready(function() {
    
$('.msg_list').click(function() {
    msg_id = $(this).data('msg_id');
    $('.msg_content').filter('[data-msg_id='+msg_id+']').toggle();
})

});