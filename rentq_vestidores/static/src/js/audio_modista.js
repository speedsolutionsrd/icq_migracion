$(document).on("ready", function(){
    setTimeout("location.reload();", 60000);

//
//     function setCookie(cname, cvalue, exdays) {
//         var d = new Date();
//         d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
//         var expires = "expires="+d.toUTCString();
//         document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
//     };
//
//     function getCookie(cname) {
//         var name = cname + "=";
//         var decodedCookie = decodeURIComponent(document.cookie);
//         var ca = decodedCookie.split(';');
//         for(var i = 0; i < ca.length; i++) {
//             var c = ca[i];
//             while (c.charAt(0) == ' ') {
//                 c = c.substring(1);
//             }
//             if (c.indexOf(name) == 0) {
//                 return c.substring(name.length, c.length);
//             }
//         }
//         return "";
//     };
//
//     var turno_modista = [];
//     $('.table-modista tr').each(function() {
//         var modista = $(this).find("td span").eq(0).html();
//         var vestidor = $(this).find("td span").eq(1).html();
//         if (modista != undefined && vestidor != undefined && modista.length != 0 && vestidor.length != 0){
//             turno_modista.push({
//                 modista: modista,
//                 vestidor: vestidor
//             });
//         }
//     });
//
//     function checkCookie(cookie, modistas){
//         var cookieModista = [];
//         var allModistas = [];
//         cookie.map((element) => {
//             cookieModista.push(element.modista);
//         })
//         modistas.map((element) => {
//             var aux = cookieModista.indexOf(element.modista)
//             if(aux < 0){
//                 allModistas.push(element);
//             }
//         })
//         return allModistas;
//     }
//
//     var cookie = getCookie('Turno');
//         if(cookie){
//             var checks = checkCookie(JSON.parse(cookie), turno_modista);
//             if (checks.length > 0) {
//                 checks.map((element) => {
//                     responsiveVoice.speak("Modista " + element.modista + " dirigirse al vestidor " + element.vestidor, "Spanish Latin American Female", {rate: 1.0});
//                 })
//             };
//         }else{
//             turno_modista.map((element) => {
//                 responsiveVoice.speak("Modista " + element.modista + " dirigirse al vestidor " + element.vestidor, "Spanish Latin American Female", {rate: 1.0});
//             })
//         }
//     setCookie('Turno', JSON.stringify(turno_modista), 15);
});
