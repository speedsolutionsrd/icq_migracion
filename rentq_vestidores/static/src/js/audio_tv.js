$(document).on('ready', function () {
  // setTimeout("location.replace('/views_tv');",60000);
  setTimeout(() => {
    location.reload();
  }, 60000);


  function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = 'expires=' + d.toUTCString();
    document.cookie = cname + '=' + cvalue + ';' + expires + ';path=/';
  };

  function getCookie(cname) {
    var name = cname + '=';
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return '';
  };
  var tickets = [];
  $('.table-tv tr').each(function () {
    var ticket = $(this).find('td span').eq(0).html();
    var vestidor = $(this).find('td span').eq(1).html();
    if (ticket != undefined && vestidor != undefined && ticket.length != 0 && vestidor.length != 0) {
      tickets.push({
        ticket: ticket,
        vestidor: vestidor
      });
    }
  });

  function checkCookie(cookie, tickets) {
    var cookieTicket = [];
    var allTickets = [];
    cookie.map((element) => {
      cookieTicket.push(element.ticket);
    });

    tickets.map((element) => {
      var aux = cookieTicket.indexOf(element.ticket);
      if (aux < 0) {
        allTickets.push(element);
      }
    });
    return allTickets;
  }

  function speak(text) {
    var utterThis = new SpeechSynthesisUtterance(text);
    var synth = window.speechSynthesis;
    utterThis.lang = 'es-US';
    synth.speak(utterThis);
  }

  var cookie = getCookie('Ticket');
  if (cookie) {
    var checks = checkCookie(JSON.parse(cookie), tickets);
    if (checks.length > 0) {
      checks.map((element) => {
        speak('Numero de ticket' + element.ticket + ' dirigirse al vestidor ' + element.vestidor);
      });
    }
  } else {
    tickets.map((element) => {
      speak('Numero de ticket' + element.ticket + ' dirigirse al vestidor ' + element.vestidor);
    });
  }

  setCookie('Ticket', JSON.stringify(tickets), 15);
});
