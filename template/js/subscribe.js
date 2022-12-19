const email_input = document.getElementById('subscribe_box');
const subscribe_button = document.getElementById('subscribe_button');
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

function hideOnClickOutside(element) {
    const outsideClickListener = event => {
        if (!element.contains(event.target) && !subscribe_button.contains(event.target) && isVisible(element)) { // or use: event.target.closest(selector) === null
          element.classList.add('hidden');
        }
    }
    document.addEventListener('click', outsideClickListener);
}

const isVisible = elem => !!elem && !!( elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length );

hideOnClickOutside(email_input);
