odoo.define('rentq_vestidores.vestidores', function (require) {
    "use strict";

    var core = require('web.core');
    var ajax = require('web.ajax');
    var Session = require('web.Session');
    var session = require('web.session');
    var QWeb = core.qweb;
    var _t = core._t;

    $(document).ready(function () {

        if ($('#notify').val() == 'True'){
            // console.log($('#notify').val());
            _beep();
        }

        function _beep() {
            if (typeof(Audio) === "undefined") {
                return function () {};
            }
            var audio;

            if (!audio) {
                audio = new Audio();
                var ext = audio.canPlayType("audio/ogg; codecs=vorbis") ? ".ogg" : ".mp3";
                audio.src = session.url("/rentq_vestidores/static/src/audio/ting" + ext);
            }
            audio.play();

        };

        $(".js-example-basic-multiple").select2();

        $(".onSubmitVestidores").on("click", function (e) {
            var id_form = $(this).closest("form");
            var name = $('input[name="vestidor"]', id_form).val();
            if (this.id == 'dc') {
                id_form.append('<input type="hidden" name="stop_counter" value="1"/>');
            }
            swal({
                title: "¿Seguro que desea liberar el Vestidor " + name + "?",
                icon: "warning",
                buttons: true,
                dangerMode: true
            }).then(willDelete => {
                if (willDelete) {
                    id_form.submit();
                    swal("Vestidor " + name + " a sido liberado", {
                        icon: "success"
                    });
                    $(this)
                        .closest("tr")
                        .remove();
                }
            });
            return false;
        });

        $(".onSubmitRenta").on("click", function (e) {
            var vestidor_id = $('#vestidor_id').val();
            $.ajax({
                url: '/dressing_room_assignation',
                type: 'POST',
                data: {
                    'vestidor_id': vestidor_id
                },
                dataType: 'json',
                error: function () {
                    swal("Ocurrio un Error revise Vestidor");
                },
                success: function (data) {
                    swal("Ocupacion Exitosa", {
                        icon: "success"
                    });
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                }
            });

        });

        $(".onSubmitMyRental").on("click", function (e) {
            var id_form = $(this).closest("form");

            var data = {}
            $(this).closest("form").serializeArray().map(function (x) {
                data[x.name] = x.value;
            });

            swal({
                title: "¿Estás seguro?",
                text: "de tomar turno",
                icon: "warning",
                buttons: true,
                dangerMode: true
            }).then(willShow => {
                if (willShow) {
                    // var form_submission = id_form.submit();
                    $.ajax({
                        url: '/take_turn_in_queue',
                        type: 'POST',
                        data: data,
                        error: function () {
                            swal("Ocurrio un Error revise Vestidor");
                        },
                        success: function (data) {
                            var result = JSON.parse(data);

                            if (result.vestidor_printer_url){

                                var url = result.vestidor_printer_url;
                                this.connection = new Session(undefined, url, {use_cors: true});
                                this.host = url;
                                self = this;
                                var tmp_re = "<receipt align='center' width='50'>"
                                tmp_re += "<img src=\"data:image/png;base64," + result.logo + "\" alt=\"" + result.company + "\" style=\"max-height: 35px;height: 35px;\"/>" + "<br/>"
                                tmp_re += "<h1>" + result.ticket + "</h1><br/>"
                                tmp_re += "<div>" + moment().format("DD-MM-YYYY h:mm:ss a") + "</div>" + "<br/>"
                                tmp_re += "<div>" + '-----------------------------' + "</div>"
                                tmp_re += "<div font='b' line-ratio='1.0'>"
                                tmp_re += 'Le atenderemos pronto!!'
                                tmp_re += "</div><br/><br/>"
                                tmp_re += "</receipt>";
                                self.connection.rpc('/hw_proxy/print_xml_receipt', {receipt: tmp_re}, {timeout: 5000})
                                    .then(function () {
                                        console.log('Called');
                                    }, function (error, event) {
                                        console.log('There was an error while trying to print the ticket:');
                                        console.log(error);
                                    });
                            }

                            swal({
                                title: result.ticket,
                                text: "Estimado(a) " + result.cliente_nombre + " le atenderemos a la brevedad posible",
                                icon: "success"
                            }).then(willShow => {
                                location.replace(result.redirect_to);
                            });
                            // setTimeout(() => {
                            //     location.replace(result.redirect_to);
                            // }, 2000);
                        }
                    });

                } else {
                    swal("Se cancelo la asignación");
                }
            });
            return false;
        });

        $(".onSubmitPartner").on("click", function (e) {
            var id_form = $(this).closest("form");
            var name = $('input[name="cliente_nombre"]', id_form).val();
            swal({
                title: "¿Estás seguro?",
                text: "de asignar turno a : " + name,
                icon: "warning",
                buttons: true,
                dangerMode: true
            }).then(willShow => {
                if (willShow) {
                    swal(name + " se asigno a la cola", {
                        icon: "success"
                    });
                } else {
                    swal("La asignación fue cancelada");
                }
            });
        });

        $(".onSubmitPartne").on("click", function (e) {
            var id_form = $(this).closest("form");
            var name = $('input[name="cliente_nombre"]', id_form).val();
            swal({
                title: "¿Estás seguro?",
                text: "De guardar cliente: " + name,
                icon: "warning",
                buttons: true,
                dangerMode: true
            }).then(willShow => {
                if (willShow) {
                    swal("Registro Exitoso", {
                        icon: "success"
                    });
                } else {
                    swal("Registro cancelado");
                }
            });
        });


    });
});