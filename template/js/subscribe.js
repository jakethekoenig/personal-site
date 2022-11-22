const email_input = document.getElementById('subscribe_box');
const subscribe_button = document.getElementById('subscribe_button');

console.log("hi");
subscribe_button.addEventListener('click', () => {
console.log("hi");
    if (email_input.classList.contains('hidden')) {
        email_input.classList.remove('hidden');
    } else {
        email_input.classList.add('hidden');
    }
});
