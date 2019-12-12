function launchModal(id) {
    var $sender = $('#' + id);
    var $modal = $('.modal').first();

    var image_url = $sender.find('img').first().attr('src');
    var book_title = $sender.find('.book-card-title').first().text();
    var book_genre = $sender.find('.book-card-genre').first().text();
    var book_rating = $sender.find('.book-card-rating').first().html();

    $modal.find('#modal_book_cover').attr('src', image_url);
    $modal.find('#modal_book_title').text(book_title);
    $modal.find('#modal_book_genre').text(book_genre);
    $modal.find('#modal_book_rating').html(book_rating);

    $modal.addClass('is-active');
    $('html').addClass('is-clipped');
}

function closeModal() {
    $('.modal').removeClass('is-active');
    $('html').removeClass('is-clipped');
}
