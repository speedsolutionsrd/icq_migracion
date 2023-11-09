$(document).ready(function () {



    setTimeout(() => {
                location.reload();
            }, 60000);

    var vestidor;

    $('.inputVestidorRadio').on('click', function () {
        vestidor = this.value;
    });

    $(".onSumitAsigarColaAle").on("click", function (e) {
        var cola_vestidor = this.value;
        $.ajax({
        url: '/dressing_room_assignation',
        type: 'POST',
        data: {
            'cola_vestidor_id': cola_vestidor,
            'vestidor_id': vestidor
        },
        dataType: 'json',
        error: function(){
            swal("Ocurrio un Error revise Vestidor");
        },
        success:function(data){
            swal("Asignación Exitosa", {
                icon: "success"
            });
            setTimeout(() => {
                location.reload();
            }, 2000);
        }
        });
    });

    $('#cola_vestidor_table thead tr:eq(1) th').each( function (i) {
        var title = $(this).text();
        $( 'input', this ).on( 'keyup change', function () {
            if ( table.column(i).search() !== this.value ) {
                table
                    .column(i)
                    .search( this.value )
                    .draw();
            }
        });
        $( '.drop_stat', this ).on( 'click', function () {
            if ( table.column(i).search() !== this.value ) {
                table
                    .column(i)
                    .search( this.innerHTML)
                    .draw();
            }
        });
    } );

    $('#cola_vestidor_table thead tr:nth-child(2) th:eq(4)').html(""); //clear last column
    // var table = $('#cola_vestidor_table').DataTable( {
    //     orderCellsTop: true,
    //     fixedHeader: false
    // } );
    // $('.dataTables_length').addClass('bs-select');

});

function allowDrop(ev) {
    ev.preventDefault();
}
function drag(ev) {
    var aux = ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    var aux = ev.dataTransfer.getData("text").split('-');
    var cola_vestidor = aux[0]
    var cliente = aux[1]
    var vestidor = $(ev.target).closest("button")[0].id;
    var vestidor_name = $(ev.target).closest("button")[0].name;
    swal({
        title: "¿Estás seguro?",
        text: "De asignar cliente: " + cliente + " al vestidor: " + vestidor_name,
        icon: "warning",
        buttons: true,
        dangerMode: true
    }).then(willShow => {
        if (willShow) {
            $.ajax({
                url: '/dressing_room_assignation',
                type: 'POST',
                data: {
                    'cola_vestidor_id': cola_vestidor,
                    'vestidor_id': vestidor
                },
                dataType: 'json',
                error: function(error){
                    swal(error.responseText);
                },
                success:function(data){
                    swal("Asignación Exitosa", {
                        icon: "success"
                    });
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                }
            });
        } else {
            swal("Asignación cancelada");
        }
    });
}