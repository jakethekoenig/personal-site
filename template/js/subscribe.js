const email_input = document.getElementById('subscribe_box');
const subscribe_button = document.getElementById('subscribe_button');
const subscribe_submit = document.getElementById('subscribe_submit');
const subscribe_form = document.getElementById('subscribe_form');
const thanks_message = document.getElementById('thanks_message');
const close_parent = document.getElementsByClassName('close_parent');

subscribe_button.addEventListener('click', () => {
    if (email_input.classList.contains('hidden')) {
        email_input.classList.remove('hidden');
    } else {
        email_input.classList.add('hidden');
    }
});

subscribe_submit.addEventListener('click', () => {
    subscribe_form.classList.add('hidden');
    thanks_message.classList.remove('hidden');
});

for (e of close_parent) {
    e.addEventListener('click', function(event) {
        event.target.parentElement.classList.add('hidden');
        subscribe_form.classList.remove('hidden');
        thanks_message.classList.add('hidden');
    });
}
