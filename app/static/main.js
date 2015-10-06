Zepto(function($){

    $(document).on('ajaxBeforeSend', function(e, xhr, options) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(options.type)) {
            xhr.setRequestHeader("X-CSRFToken", $('#csrf-token').val());
        }
    });

    $('.js-order').on('submit', function(e){
        $.post('/graph/', { domain: $('.js-order-field').val() }, function(response){
            if (response.result && response.result != 'fail') {
                window.location = response.url;
            }else{
                // TODO invalid domain error
            }
        });
        return false;
    });
});