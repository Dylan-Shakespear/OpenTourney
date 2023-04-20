// JavaScript code for page switching animation
$(document).on('click', 'a.page-animation', function(event) {
    event.preventDefault();
    var url = $(this).attr('href');
    var currentUrl = window.location.href.replace(location.origin, '');
    if(currentUrl !== url) {
        $('#animation-page').addClass('out');
        $.ajax({
            url: url,
            success: function(data) {
                var newContent = $(data).filter('#animation-page').html();
                var classList = $(data).filter('#animation-page').attr('class').split(' ');
                $('#animation-page').removeClass('out').addClass('in');
                setTimeout(function() {
                    $('#animation-page').removeClass('in').addClass('show');
                    $('#animation-page').html(newContent);
                    // Remove Old Theme
                    if ($('#animation-page').hasClass('dark-theme')) {
                        $('#animation-page').removeClass('dark-theme');
                    }
                    else if ($('#animation-page').hasClass('med-theme')) {
                         $('#animation-page').removeClass('med-theme');
                    }
                    else {
                        $('#animation-page').removeClass('normal-theme');
                    }
                    // Add New Theme
                    if (classList.indexOf('dark-theme') !== -1) {
                        $('#animation-page').addClass('dark-theme');
                    }
                    else if (classList.indexOf('med-theme') !== -1) {
                        $('#animation-page').addClass('med-theme');
                    }
                    else {
                        $('#animation-page').addClass('normal-theme');
                    }
                    setTimeout(function() {
                        window.location.href = url;
                    }, 400);
                }, 400);
            }
        });
    }
});
