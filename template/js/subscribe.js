const email_input = document.getElementById('subscribe_box');
const subscribe_button = document.getElementById('subscribe_button');
const close_parent = document.getElementsByClassName('close_parent');

subscribe_button.addEventListener('click', () => {
    if (email_input.classList.contains('hidden')) {
        email_input.classList.remove('hidden');
    } else {
        email_input.classList.add('hidden');
    }
});

for (e of close_parent) {
    e.addEventListener('click', function(event) {
        event.target.parentElement.classList.add('hidden');
    });
}
