$( document ).ready(function() {

    MSG_CREATED = 10
    MSG_READED = 20
    MSG_DELETED = 30

    $('.msg_list').click(function() {
        elem = $(this)
        msg_id = elem.data('msg_id');
        $('.msg_content').filter('[data-msg_id='+msg_id+']').toggle();
        msg_status = elem.data('msg_status');
        if (msg_status == MSG_CREATED) {
            // mark as readed
            $.ajax({
            type: 'PATCH',
            url: '/api/v1/mensajes/mensaje/' + msg_id + '/',
            headers: {
                'X-CSRFToken': csrftoken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            data: JSON.stringify({'estado': MSG_READED}),
            processData: false,
            })
            .done(function( data ) {
                elem.data('msg_status', MSG_READED);
                elem.css('font-weight', 'normal');
            });
        }

    });

    $('.msg_del').click(function() {
        elem = $(this)
        msg_id = elem.data('msg_id');
        $('.msg_row').filter('[data-msg_id='+msg_id+']').hide();
        
        // mark as deleted
        $.ajax({
        type: 'DELETE',
        url: '/api/v1/mensajes/mensaje/' + msg_id + '/',
        headers: {
            'X-CSRFToken': csrftoken
        },
        processData: false,
        });

    })

});