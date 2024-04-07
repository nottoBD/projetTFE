document.addEventListener('DOMContentLoaded', function () {
    const languageSelectors = document.querySelectorAll('.language-selector');

    languageSelectors.forEach(function (selector) {
        selector.addEventListener('click', function (e) {
            e.preventDefault();
            const languageCode = this.getAttribute('data-language');
            const form = document.createElement('form');
            form.action = "/i18n/setlang/";
            form.method = "POST";

            // fetch  token from template
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            form.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">` +
                `<input type="hidden" name="language" value="${languageCode}">` +
                `<input type="hidden" name="next" value="${window.location.pathname}">`;

            document.body.appendChild(form);
            form.submit();
        });
    });
});
