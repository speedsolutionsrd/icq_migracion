odoo.define('posbox_send.sales_posbox', function (require) {

    var posbox = require('posbox_send.posbox');
    //
    var host = "http://192.168.1.126:8069";

    $(document).on('click', '[data-field="print_receipt"] button', function(e){
        return false;
    });

    // var receipt = "<receipt align='center' width='40'><left>Payments:</left></receipt>";


    // $.ajax({
    //     url: 'api?=data',
    //     data: {
    //         id: 123
    //     },
    //     success: function(response){
    //
    //         //response.host
    //         //response.receipt
    //
    //
    //     }
    // })


     // posObj.connect(host);
     // posObj.status();
    // posObj.print(receipt);

    // alert(12);

    // var form_widget = require('web.form_widgets');
    // var core = require('web.core');
    // var _t = core._t;
    // var QWeb = core.qweb;
    //
    // form_widget.WidgetButton.include({
    //     on_click: function(model) {
    //         alert(model);
    //         if(this.node.attrs.custom === "click"){
    //             alert('message');
    //             return;
    //         }
    //         this._super();
    //     },
    // });



});