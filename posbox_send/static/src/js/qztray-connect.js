odoo.define('posbox_send.qztray-connect', function () {
    if (!qz.websocket.isActive()) {
        qz.websocket.connect().then(function () {
            // return qz.printers.find("ZD410");         // Pass the printer name into the next Promise
        }).then(function () {
            alert('Label Print Connected.');
        }).catch(function (e) {
            alert(e);
        });
    }else{
        alert(qz.websocket.isActive());
    }
});