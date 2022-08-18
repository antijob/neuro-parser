function checkmark(data, other) {
  if (data == "1")
    { return '<div align=center><i class="fas fa-check"></i></div>' }
  else
    { return "" }
}

var rateTable = $('#table').DataTable({
  serverSide: false,
  columns: [
    {data: 'title', width: "50%"},
    {data: 'marker', width: "10%"},
    {data: 'cosine', width: "10%"},
    {data: 'url', width: "30%"},
  ],
  columnDefs: [
      {
        render: function ( data, type, row ) {
          return checkmark(data, row);
        },
        targets: 1
      },
      {
        render: function ( data, type, row ) {
          return checkmark(data, row);
        },
        targets: 2
      },
      {
        render: function ( data, type, row ) {
          return "<a href='" + data + "' target='_blank'>" + data + "</a>";
        },
        targets: 3
      },
  ],
  sDom: 'rt<"bottom">',
  language: {
    zeroRecords: "Нет данных",
  }
});

function updateTable() {
  rateTable.clear().draw();
  let date = $("#date").val();
  let source = $("#source").val();
  $("#updated").hide();
  if (!(date && source)) return false;

  $("#updating").show();
  $.get( "/grabber/algorithms_data/", { date: date, source: source } )
  .done(function( response ) {
    $("#algorithm").val(response.data.algorithm);
    $(".source_url").html(response.data.source_url);
    if (response.data.rates) {
      rateTable.rows.add(response.data.rates).draw();
    }
    $("#updated").show();
    $("#updating").hide();
  });
}

function setAlgorithm() {
  let algorithm = $("#algorithm").val();
  let source = $("#source").val();
  if (!(source && algorithm)) return false;

  let data = {algorithm: algorithm, source: source};
  $('#submit').html('Сохраняется').addClass('btn-light').removeClass('btn-primary').prop('disabled', true);
  $.post(window.location.href, data)
  .done(function() {
    $('#submit').html('Сохранено').addClass('btn-success').removeClass('btn-light');
    setTimeout(function() {
      $('#submit').html('Сохранить').addClass('btn-primary').removeClass('btn-success').prop('disabled', false);
    }, 2000)
  })
}

$( document ).ready(function() {
  document.getElementById("date").valueAsDate = new Date();
  $("#date").on("change", updateTable);
  $("#source").on("change", updateTable);
  $("#submit").on("click", setAlgorithm);
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) { return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method)) }
$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    var csrftoken = getCookie("csrftoken");
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});
