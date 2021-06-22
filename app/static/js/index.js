function launchModal(id, user_rating) {
    var $sender = $('#' + id);
    var $modal = $('.modal').first();

    var image_url = $sender.find('img').first().attr('src');
    var book_title = $sender.find('.book-card-title').first().text();
    var book_genre = $sender.find('.book-card-genre').first().text();
    var book_rating = $sender.find('.book-card-rating').get(0).outerHTML;

    $modal.find('#modal_book_cover').attr('src', image_url);
    $modal.find('#modal_book_title').text(book_title);
    $modal.find('#modal_book_genre').text(book_genre);
    $modal.find('#modal_content').append(book_rating);
    $modal.find('.rating__input').prop('checked', false);
    if (user_rating == 0) { user_rating = 'none'; }
    $modal.find('#rating-'+user_rating).prop('checked', true);

    var book_id = $sender.attr('data-id');
    $modal.find('#book_id').attr('value', book_id);
    $modal.find('#next_url').attr('value', window.location.href);

    $modal.addClass('is-active');
    $('html').addClass('is-clipped');
}

function closeModal() {
    $('.modal').removeClass('is-active');
    $('html').removeClass('is-clipped');
    $('.modal').find('.book-card-rating').remove();
}

function searchBooks(val, url) {
    re = /^[Tt]he\s/i;
    val = val.replace(re, '');
    if (val.length < 4) return;

    $.ajax({
        url: url,
        method: 'GET',
        data: { term: val },
        success: function(data) {
            var datalist = $('#searchresults');
            var options = [];

            datalist.children('option').each(function() {
                var opt_val = this.value;
                if (!data.includes(opt_val)) {
                    this.remove();
                } else {
                    options.push(opt_val);
                }
            });

            data.forEach(function(item, index) {
                if (!options.includes(item)) {
                    var opt = $('<option></option>').attr('value', item);
                    datalist.append(opt);
                }
            });
        }
    });
}

function submitSearch() {
    var term = $('.search-books').first().val();
    var url_param = { search: term };
    var url_root = window.location.href.split('?')[0];
    var url = url_root + '?' + $.param(url_param);
    window.location.href = url;
}
