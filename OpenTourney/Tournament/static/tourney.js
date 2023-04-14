// JavaScript for editing match

function matchInfo(event) {

    // Create a Bootstrap modal popup
    var modal = $('<div class="modal fade" tabindex="-1" role="dialog">');
    var modalDialog = $('<div class="modal-dialog" role="document">');
    var modalContent = $('<div class="modal-content">');
    modal.append(modalDialog);
    modalDialog.append(modalContent);

    const matchId = parseInt(this.getAttribute('data-matchid'));
    const rounds = parseInt(this.getAttribute('data-tourney_id'));

    // Load the edit form inside the modal
    $.ajax({
        url: '/tourney/edit_match/' + matchId + '/' + rounds,
        success: function(data) {
            modalContent.html(data);
        }
    })

    // Show the model
    modal.modal('show');

    // Submit the form and close the modal when it's done
    modalContent.on('submit', 'form', function(e) {
        e.preventDefault();
        $.ajax({
            url: $(this).attr('action'),
            method: $(this).attr('method'),
            data: $(this).serialize(),
            success: function() {
                modal.modal('hide');
                location.reload(); // Reload the page to show the updated information
            }
        });
    });
}

let match_buttons = document.querySelectorAll('.matchup');

for (match_button of match_buttons) {
    match_button.addEventListener('click', matchInfo);
}