(function () {
    "use strict";

    var $receipt_url = $('[name="receipt_url"]');
    var $receipt = $('[name="receipt"]');

    var data = {
        host: $receipt_url.val(),
        receipt: $receipt.val()
    };

    var pos = new posbox();

    var onSuccess = function () {
        $('.modal').modal('hide').data('bs.modal', null);
    }

    var onError = function (status, error) {
        $('.modal').modal('hide').data('bs.modal', null);
        alert(error.message);
    }

    pos.connect(data.host);
    pos.status();
    pos.print(data.receipt, onSuccess, onError);

})();