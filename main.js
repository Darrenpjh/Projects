document.getElementById('pizza-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting the usual way

    const formData = new FormData(this); // Gather the form data

    fetch('/submit_order', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Order placed successfully!');
        } else {
            alert('Error placing order: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});
