Zepto(function($){

    $(document).on('ajaxBeforeSend', function(e, xhr, options) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(options.type)) {
            xhr.setRequestHeader("X-CSRFToken", $('#csrf-token').val());
        }
    });

    $('.js-order').on('submit', function(e){
        $.post(
            '/domain/public',
            {domain: $('.js-order-field').val()},
            function(response) {
                $('.js-console').append(response.message + '<br />');
            });
        return false;
    });
});