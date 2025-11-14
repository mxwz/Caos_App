document.addEventListener('DOMContentLoaded', function() {
    const newsItems = document.querySelectorAll('.news-item');

    newsItems.forEach(item => {
        item.addEventListener('click', function() {
            window.open(item.querySelector('a').href, '_blank');
        });
    });
});
