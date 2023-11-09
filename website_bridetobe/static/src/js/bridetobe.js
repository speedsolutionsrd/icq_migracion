$(document).ready(function () {
  // $('input[type="date"]').datepicker({dateFormat : 'dd/mm/yy'});
    console.log("paso por aqui")
    $('#calendar').fullCalendar({
        
        header: {
            left: 'prev,next today', center: 'title', right: 'month,agendaWeek,agendaDay,listWeek'
        }, events: {
            url: '/get_events', type: 'POST', data: {
                product_id: $('input#product_id').val(), csrf_token: $('input#csrf_token').val()
            }
        },
    });

    $('#product_barcode').on('paste', function (e) {
        e.preventDefault();
    });

    $('#product_barcode').scannerDetection({
        minLength: 3,
        stopPropagation: true,
        preventDefault: true,
        timeBeforeScanTest: 200,
        startChar: [],
        endChar: [13],
        avgTimeByChar: 100,
        onComplete: function (barcode) {
            var product_code = $('#product_barcode').val();
            if (!product_code.includes(barcode)) {
                if (!!product_code) {
                    $('#product_barcode').val(product_code + ',' + barcode);
                } else {
                    $('#product_barcode').val(barcode);
                }
            }
        },
        onError: function (e) {
            $('#product_barcode').val($('#product_barcode').val());
        }
    });

    $('#add_week').on('click', function (e) {
        e.preventDefault();
        var event_date_count = document.querySelectorAll('[id^="event_date"]');
        var event_date = $('#event_date').val();
        var count = event_date_count.length - 1;
        var date = new Date(event_date);

        if (event_date !== '') {
            $.ajax({
                url: '/get_next_week', type: 'POST', data: {
                    'event_date': event_date, 'week_count': event_date_count.length
                }, dataType: 'json', error: function (response) {
                    console.log('Ocurrio un Error');
                }, success: function (data) {
                    var field_name = 'event_date_' + event_date_count.length;
                    if (event_date_count.length > 1) {
                        $('<div class="form-group col-sm-6 ' + field_name + '"><label class="control-label col-sm-12" for="event_date">Semana Adicional ' + event_date_count.length + '</label><input type="date" value="' + data['event_date'] + '" class="form-control" id="' + field_name + '" name="' + field_name + '" readonly="True"/></div>').insertAfter('.event_date_' + count);
                    } else {
                        $('<div class="form-group col-sm-6 ' + field_name + '"><label class="control-label col-sm-12" for="event_date">Semana Adicional 1</label><input type="date" value="' + data['event_date'] + '" class="form-control" id="' + field_name + '" name="' + field_name + '" readonly="True"/></div>').insertAfter('.event_date_minus');
                    }
                }
            });
        }
    });

    $('#remove_week').on('click', function (e) {
        e.preventDefault();
        var event_date_count = document.querySelectorAll('[id^="event_date"]');
        if (event_date_count.length > 1) {
            var count = event_date_count.length - 1;
            var el = $('.event_date_' + count);
            el.remove();
        }
    });

    // $('#search_partner').on('click', function (e) {
    //   e.preventDefault();
    //   var  vat = $('#vat').val();
    //   console.log(vat)
    // });
});

function showsection() {
    let suministro_materiales = document.getElementById("suministro_materiales");
    let options = suministro_materiales.value;

    if (options == 'p_cliente' || options == 'e_cliente') document.getElementById("materiales_recibidos").style.display = 'block';
    else document.getElementById("materiales_recibidos").style.display = 'none';
}
function showupper(e){
    let text = e.value;
    e.value = text.toUpperCase()
}

function confirmationDates() {
    let fechaActual = new Date();
    let hora = fechaActual.getHours() + ":" + fechaActual.getMinutes() + ":" + fechaActual.getSeconds()
    let fecha = fechaActual.getDay() + '/' + fechaActual.getMonth() + '/' + fechaActual.getFullYear()
    console.log(hora, fecha)
}