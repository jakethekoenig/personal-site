const email_input = document.getElementById('subscribe_box');
const subscribe_button = document.getElementById('subscribe_button');
const subscribe_buttons = document.getElementById('subscribe_buttons');
const toggle_subscribe_buttons = document.getElementById('toggle_subscribe_buttons');
const subscribe_submit = document.getElementById('subscribe_submit');
const email_subscribe_textform = document.getElementById('email_subscribe_textform');
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

toggle_subscribe_buttons.addEventListener('click', () => {
    if (subscribe_buttons.classList.contains('fixed_bottom')) {
        subscribe_buttons.classList.remove('fixed_bottom');
        subscribe_buttons.classList.add('fixed_bottom_visible');
    } else {
        subscribe_buttons.classList.remove('fixed_bottom_visible');
        subscribe_buttons.classList.add('fixed_bottom');
    }
});

function sendSubToLambda(email) {
        const data = {
            type:'newsletter_subscribe',
            email: email
        };
        fetch('https://ifr71jknt7.execute-api.us-east-2.amazonaws.com/default/addComment', {
            method: 'POST',
            mode: 'no-cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then(data => {
            console.log(JSON.stringify(data));
        })
        .catch((error) => {
            console.error('Error: ', error);
        });
}

subscribe_submit.addEventListener('click', () => {
    subscribe_form.classList.add('hidden');
    const email = email_subscribe_textform.value;
    // TODO: client side validate email
    console.log(email);
    sendSubToLambda(email);
    thanks_message.classList.remove('hidden');
});

for (e of close_parent) {
    e.addEventListener('click', function(event) {
        event.target.parentElement.classList.add('hidden');
        subscribe_form.classList.remove('hidden');
        thanks_message.classList.add('hidden');
    });
}

function addClassOnClickOutside(element, className, removeClass=[]) {
    const outsideClickListener = event => {
        // TODO: this long list of classes makes the function not quite do what it claims.
        if (!element.contains(event.target) && !subscribe_button.contains(event.target) && !toggle_subscribe_buttons.contains(event.target) && isVisible(element)) { // or use: event.target.closest(selector) === null
          element.classList.add(className);
            for (e of removeClass) {
                element.classList.remove(e);
            }
        }
    }
    document.addEventListener('click', outsideClickListener);
}

const isVisible = elem => !!elem && !!( elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length );

addClassOnClickOutside(email_input, 'hidden');
addClassOnClickOutside(subscribe_buttons, 'fixed_bottom', ['fixed_bottom_visible']);
