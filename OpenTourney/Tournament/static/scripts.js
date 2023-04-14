// JavaScript code for page switching animation
$(document).on('click', 'a', function(event) {
    event.preventDefault();
    var url = $(this).attr('href');
    var currentUrl = window.location.href.replace(location.origin, '');
    if(currentUrl !== url) {
        $('#animation-page').addClass('out');
        $.ajax({
            url: url,
            success: function(data) {
                var newContent = $(data).filter('#animation-page').html();
                $('#animation-page').removeClass('out').addClass('in');
                setTimeout(function() {
                    $('#animation-page').removeClass('in').addClass('show');
                    $('#animation-page').html(newContent);
                    setTimeout(function() {
                        window.location.href = url;
                    }, 400);
                }, 400);
            }
        });
    }
});
