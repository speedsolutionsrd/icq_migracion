(function () {

    var $receipt_url = $('[name="receipt_url"]');
    var $receipt = $('[name="receipt"]');

    function print() {
        var config = qz.configs.create($receipt_url.val());       // Create a default config for the found printer
        return qz.print(config, [$receipt.val()]);
    }

    qz.websocket.connect().then(function () {
        return print();
    }).catch(function (e) {
        if(qz.websocket.isActive()){
            return print();
        }else{
            alert(e);
        }
    });
    $('.modal').modal('hide').data('bs.modal', null);

})();