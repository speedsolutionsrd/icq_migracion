function showpickup() {
    let pickup = document.getElementById("state_id")
    let data_pickup = pickup.options[pickup.selectedIndex].getAttribute('data-pickup')
    let myDiv = $('.pickup_val');

    if (data_pickup === 'True') myDiv.show();
    else myDiv.hide();
}

