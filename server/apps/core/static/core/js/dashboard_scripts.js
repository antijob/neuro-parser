const ACTIVE_STATUSES = [2, 3, 4];
DATA_URL = "/dashboard/incidents/data/";
const COLUMNS = [
  {data: 'any_title', width: "50%", title: "Заголовок"},
  {data: 'status', width: "7%", title: "Статус"},
  {data: 'create_date', width: "7%", title: "Дата создания"},
  {data: 'tags', width: "7%", title: "Теги"},
  {data: 'urls', width: "5%", title: "Источники"},
  {data: null, width: "18%", title: "Действия"},
];
const COLUMN_DEFS = [
  {
    render: function ( data, type, row ) {
      if (row['is_media']){
        icon = "<i class='fas fa-newspaper mr-2 text-secondary' title='Инцидент из СМИ'></i>";
        title = data;
      } else {
        icon = "<i class='fas fa-user mr-2 text-secondary' title='Инцидент по заявке'></i>";
        title = row["email"];
      }
      return "<div class='row-title p-2'>" + icon + title + "<i class='fas fa-angle-down m-1'></i></div>";
    },
    targets: 0
  },
  {
    render: function ( data, type, row ) {
      badgeClass = ['danger', 'white', 'success', 'warning', 'warning', 'secondary'][data];
      badgeText = ['Не обработан', 'Отклонен', 'Принят', 'Коммуникации', 'В работе', 'Завершен', 'Удален'][data];
      td = '<span class="badge status-badge badge-' + badgeClass + '">' + badgeText + '</span>';
      return td;
    },
    targets: 1
  },
  {
    render: function ( data, type, row ) {
      if (!data) { return '' }
      td = '';
      for (url of data) {
        td = '<a href="' + url + '" target="_blank"><i class="fas fa-external-link-alt"></i></a>';
      };
      return td;
    },
    targets: 4
  },
  {
    render: function ( data, type, row ) {
      td = `<button type="button" class="btn btn-sm btn-success ajax-submit mr-2 mb-1" value="2">
              <i class="fas fa-check d-none d-xl-inline-block"></i> Принять</button>
            <button type="button" class="btn btn-sm btn-danger ajax-submit mb-1" value="1">
              <i class="fas fa-times d-none d-xl-inline-block"></i> Отклонить</button>`;
      return td;
    },
    targets: 5
  },
];
CATEGORIES = {
  0: 'Другое',
  1: 'Уголовное преследование',
  2: 'Административное давление',
  4: 'Регулирование',
  5: 'Насилие',
  6: 'Интернет-цензура',
  7: 'Гражданские иски',
  8: 'Кибератака',
  9: 'Давление на IT-бизнес',
  10: 'Шатдауны',
  11: 'Запросы личной информации у интернет-сервисов',
};
REGIONS = {
  'RU': 'Россия',
  'RU-AD': '01 Адыгея',
  'RU-BA': '02 Башкортостан',
  'RU-BU': '03 Бурятия',
  'RU-AL': '04 Республика Алтай',
  'RU-DA': '05 Дагестан',
  'RU-IN': '06 Ингушетия',
  'RU-KB': '07 Кабардино-Балкария',
  'RU-KL': '08 Калмыкия',
  'RU-KC': '09 Карачаево-Черкесия',
  'RU-KR': '10 Карелия',
  'RU-KO': '11 Республика Коми',
  'RU-ME': '12 Марий Эл',
  'RU-MO': '13 Мордовия',
  'RU-SA': '14 Якутия',
  'RU-SE': '15 Северная Осетия',
  'RU-TA': '16 Татарстан',
  'RU-TY': '17 Тыва',
  'RU-UD': '18 Удмуртия',
  'RU-KK': '19 Хакасия',
  'RU-CE': '20 Чечня',
  'RU-CU': '21 Чувашия',
  'RU-ALT': '22 Алтайский край',
  'RU-KDA': '23 Краснодарский край',
  'RU-KYA': '24 Красноярский край',
  'RU-PRI': '25 Приморский край',
  'RU-STA': '26 Ставропольский край',
  'RU-KHA': '27 Хабаровский край',
  'RU-AMU': '28 Амурская область',
  'RU-ARK': '29 Архангельская область',
  'RU-AST': '30 Астраханская область',
  'RU-BEL': '31 Белгородская область',
  'RU-BRY': '32 Брянская область',
  'RU-VLA': '33 Владимирская область',
  'RU-VGG': '34 Волгоградская область',
  'RU-VLG': '35 Вологодская область',
  'RU-VOR': '36 Воронежская область',
  'RU-IVA': '37 Ивановская область',
  'RU-IRK': '38 Иркутская область',
  'RU-KGD': '39 Калининградская область',
  'RU-KLU': '40 Калужская область',
  'RU-KAM': '41 Камчатский край',
  'RU-KEM': '42 Кемеровская область',
  'RU-KIR': '43 Кировская область',
  'RU-KOS': '44 Костромская область',
  'RU-KGN': '45 Курганская область',
  'RU-KRS': '46 Курская область',
  'RU-LEN': '47 Ленинградская область',
  'RU-LIP': '48 Липецкая область',
  'RU-MAG': '49 Магаданская область',
  'RU-MOS': '50 Московская область',
  'RU-MUR': '51 Мурманская область',
  'RU-NIZ': '52 Нижегородская область',
  'RU-NGR': '53 Новгородская область',
  'RU-NVS': '54 Новосибирская область',
  'RU-OMS': '55 Омская область',
  'RU-ORE': '56 Оренбургская область',
  'RU-ORL': '57 Орловская область',
  'RU-PNZ': '58 Пензенская область',
  'RU-PER': '59 Пермский край',
  'RU-PSK': '60 Псковская область',
  'RU-ROS': '61 Ростовская область',
  'RU-RYA': '62 Рязанская область',
  'RU-SAM': '63 Самарская область',
  'RU-SAR': '64 Саратовская область',
  'RU-SAK': '65 Сахалинская область',
  'RU-SVE': '66 Свердловская область',
  'RU-SMO': '67 Смоленская область',
  'RU-TAM': '68 Тамбовская область',
  'RU-TVE': '69 Тверская область',
  'RU-TOM': '70 Томская область',
  'RU-TUL': '71 Тульская область',
  'RU-TYU': '72 Тюменская область',
  'RU-ULY': '73 Ульяновская область',
  'RU-CHE': '74 Челябинская область',
  'RU-ZAB': '75 Забайкальский край',
  'RU-YAR': '76 Ярославская область',
  'RU-MOW': '77 Москва',
  'RU-SPE': '78 Санкт-Петербург',
  'RU-YEV': '79 Еврейская автономная область',
  'UA-43': '82 Крым',
  'RU-NEN': '83 Ненецкий автономный округ',
  'RU-KHM': '86 Ханты-Мансийский автономный округ — Югра',
  'RU-CHU': '87 Чукотский автономный округ',
  'RU-YAN': '89 Ямало-Ненецкий автономный округ',
  'UA-40': '92 Севастополь'
};
function getCategoryOptions(selected) {
  let options = '';
  for (const [categoryTerm, categoryName] of Object.entries(CATEGORIES)) {
    options += '<option value="' + categoryTerm + '"' + (selected == categoryTerm ? ' selected ' : '') + '>' + categoryName + '</option>';
  }
  return options;
}
function getRegionOptions(selected) {
  let options = '';
  for (const [regionCode, regionName] of Object.entries(REGIONS)) {
    options += '<option value="' + regionCode + '"' + (selected == regionCode ? ' selected ' : '') + '>' + regionName + '</option>';
  }
  return options;
}

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

function rowDetailsFormat(d) {
  let categoryOptions = getCategoryOptions(d.incident_type);
  let regionOptions = getRegionOptions(d.region);
  let title = '<p><input name="title" class="form-control" value="' + (d.public_title || d.title) + '"></p>';
  let tags = '<label>Теги через запятую</label><p><input name="tags" class="form-control" value="' + (d.tags || '') + '"></p>';
  let selectRegion = '<label>Регион</label><select class="form-control" name="region">' + regionOptions + '</select>';
  let incidentDate = '<label>Дата инцидента</label><input type="text" id="create_date" name="create_date" class="form-control bootstrap-datepicker" value="' + d.create_date + '">';
  let selectCategory = '<label>Категория</label><select class="form-control" name="category">' + categoryOptions + '</select>';
  let description = '<p><textarea class="form-control" name="description" rows=12>' + (d.public_description || d.description) + '</textarea></p>';
  let counter = '<p><label>Количество нарушений</label><input name="count" type="number" class="form-control" value="' + d.count + '" min=1></p>';
  let buttonAccept = '<button type="button" class="btn btn-success ajax-submit mr-2" value="2"><i class="fas fa-check"></i> Принять</button>';
  let buttonReject = '<button type="button" class="btn btn-danger ajax-submit mr-2" value="1"><i class="fas fa-times"></i> Отклонить</button>';
  let buttonInProgress = '<button type="button" class="btn btn-warning ajax-submit mr-2" value="4"><i class="fas fa-cogs"></i> В работу</button>';
  let editorUrl = '/dashboard/' + (d.is_media ? 'mediaincident/' : 'incident/') + d.pk + '/update/';
  let buttonEdit = '<a href="' + editorUrl + '" class="btn btn-primary"><i class="fas fa-pen"></i> Редактировать</a> ';
  let buttonRow = '<p class="d-flex justify-content-between"><span>' + (d.is_media ? '': buttonInProgress) + buttonAccept + buttonReject + '</span>' + buttonEdit + '</p>';
  let selects_row = '<div class="row"><div class="col-12 col-md-3">' + selectRegion + '</div><div class="col-12 col-md-3">' + selectCategory + '</div><div class="col-12 col-md-3">' + incidentDate + '</div><div class="col-12 col-md-3">' + counter + '</div></div>';

  if (d.duplicate_pks && d.duplicate_pks.length && d.duplicate_pks[0]) {
    duplicates = '';
    for (i=0; i<d.duplicate_pks.length; i++) {
      duplicates += '<li class="py-1"><a href="/dashboard/mediaincident/' + d.duplicate_pks[i] + '/update/">' + d.duplicate_titles[i] + '</a></li>';
    }
    duplicates_tag = `<details class="pb-4"><summary style="font-size:1.2em;outline:none;" class="pb-2">Дубликаты:</summary><ul style="list-style: none">${duplicates}</ul></details>`;
  } else {
    duplicates_tag = '';
  }

  if (d.original_pk) {
    original = '<a href="/dashboard/mediaincident/' + d.original_pk + '/update/">' + d.original_title + '</a>';
    original_tag = `<p class="pb-4 font-size:1.2em;outline:none;">Дубликат инцидента: ${original}</p>`;
  } else {
    original_tag = '';
    original_title = '';
  }

  let form = '<form action="/dashboard/mediaincident/' + d.pk + '/ajax/">' + title + tags + selects_row + description + duplicates_tag + original_tag + buttonRow + '</form>';
  return '<div class="bg-grey p-4">' + form + '</div>';
}

$(document).ready(function () {
  $("#region").html(getRegionOptions());
  $("#category").html("<option value=''> - Все категории - </option>" + getCategoryOptions());
  tableApi = $('#dataTable').DataTable({
    dom: "Brtip",
    ajax: {
      url: DATA_URL,
      data: function ( d ) {
        d = Object.assign(d, tableData);
        d.start_date = $("#start_date").val();
        d.end_date = $("#end_date").val();
        d.region = $("#region").val();
        d.category = $("#category").val();
      },
    },
    serverSide: true,
    info: false,
    pageLength: 12,
    bSort: false,
    columns: COLUMNS,
    columnDefs: COLUMN_DEFS,
    sPaginationType: "full_numbers",
    createdRow: function (row, data, dataIndex) {
      $(row).addClass('data-row');
    },
    language: {
      paginate: {
        next: 'Вперед',
        previous: "Назад",
        first: '&laquo;',
        last: '&raquo;'
      },
    },
  });

  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  });

  searchTimeout = null;
  $('#table-search').keyup(function () {
    let query = $(this).val();
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(function () {
      tableApi.search(query).draw();
    },
    1000);
  });

  $("#region").change(tableApi.draw);
  $("#category").change(tableApi.draw);

  let ranges = {
        'Этот месяц': [moment().startOf('month'), moment().endOf('month')],
        'Предыдущий месяц': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
        'За всё время': [moment([2015, 0, 1]), moment()],
  }
  for (year=2015; year <= new Date().getFullYear(); year++) {
    ranges[year] = [moment([year, 0, 1]), moment([year, 11, 31])]
  }
  datePicker = $('#dates').daterangepicker({
  ranges: ranges,
  locale: {
      "format": "DD.MM.YYYY",
      "separator": " - ",
      "applyLabel": "Принять",
      "cancelLabel": "Отмена",
      "fromLabel": "С",
      "toLabel": "до",
      "customRangeLabel": "Выбрать свои даты",
      "weekLabel": "Нед",
      "daysOfWeek": [
          "Вс",
          "Пн",
          "Вт",
          "Ср",
          "Чт",
          "Пт",
          "Сб"
      ],
      "monthNames": [
          "Январь",
          "Февраль",
          "Март",
          "Апрель",
          "Май",
          "Июнь",
          "Июль",
          "Август",
          "Сентябрь",
          "Октябрь",
          "Ноябрь",
          "Декабрь"
      ],
      "firstDay": 1
  },
  autoUpdateInput: false,
  autoApply: true,
  });

  $('#dates').on('apply.daterangepicker', function(ev, picker) {
    start_date = picker.startDate.format('YYYY-MM-DD');
    end_date = picker.endDate.format('YYYY-MM-DD');
    $("#start_date").val(start_date);
    $("#end_date").val(end_date);
    $('#dates').val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    tableApi.draw();
  });

  $('#dates').on('cancel.daterangepicker', function(ev, picker) {
    $("#start_date").val(null);
    $("#end_date").val(null);
    $('#dates').val('');
    tableApi.draw();
  });

  // Open row details
  $('#dataTable tbody').on('click', 'td .row-title', function() {
    var tr = $(this).closest('tr');
    var row = tableApi.row( tr );

    if ( row.child.isShown() ) {
      row.child.hide();
    }
    else {
      row.child( rowDetailsFormat(row.data()) ).show();
      $('.bootstrap-datepicker').datepicker({
          format: "yyyy-mm-dd",
          autoclose: true
      });
    }
  });

  $('#dataTable').on( 'click', '.data-row', function () {
    $('.selected').removeClass('selected');
    $(this).addClass('selected');
  });

  $('#dataTable').on( 'click', '.ajax-submit', function () {
    let button = $(this);
    let status = button.val();
    let buttonColor = {1: "btn-danger", 2: "btn-success"}[status];
    let buttonText = {1: '<i class="fas fa-times"></i> Отклонить', 2: '<i class="fas fa-check"></i> Принять'}[status];

    button.prop( "disabled", true );

    let tr = button.parents('tr');
    if (!tr.hasClass('data-row')) {
      tr = tr.prev();
    }
    let row = tableApi.row(tr);
    let rowData = tableApi.row( row ).data();
    let form = button.parent().parent().parent();
    let counter = form.find('[name="count"]').val();
    let create_date = form.find('[name="create_date"]').val();
    let category = form.find('[name="category"]').val();
    let title = form.find('[name="title"]').val();
    let tags = form.find('[name="tags"]').val();
    let description = form.find('[name="description"]').val();
    let region = form.find('[name="region"]').val();
    if (rowData.is_media) {
      url = "/dashboard/mediaincident/" + rowData.pk + "/ajax/"
    } else {
      url = "/dashboard/incident/" + rowData.pk + "/ajax/"
    };
    let data = {public_title: title,
                public_description: description,
                region: region,
                count: counter,
                create_date: create_date,
                tags: tags,
                category: category,
                is_media: rowData.is_media,
                status: status};
    $.post(url, data)
      .done(function() {
        tableApi.cell( row, 0 ).data(title);
        tableApi.cell( row, 1 ).data(status);
        tableApi.cell( row, 2 ).data(create_date);
        tableApi.cell( row, 3 ).data(tags);
        button.addClass("btn-light").removeClass(buttonColor).html("Сохранено!");
        setTimeout(function() {
          button.addClass(buttonColor)
          .removeClass("btn-light")
          .html(buttonText)
          .prop( "disabled", false );
          row.child.hide()
        }, 1000);
      })
      .fail(function() {
        alert("Ошибка при сохранении");
        button.addClass("btn-primary")
        .removeClass("btn-white")
        .prop( "disabled", false );
      })
      .always(function() {

      })

  });
});

function deleteStage(campaign_id, stage_id) {
  if (confirm("Вы действительно хотите удалить этап?")) {
    let url = "/dashboard/stage/" + stage_id + "/delete/";

    $.post(url, {})
      .done(function() {
        $("#stage-"+stage_id).remove();
      })
      .fail(function() {
        alert("Ошибка при удалении");
      })
  }
}


function deleteExplanation(campaign_id, explanation_id) {
  if (confirm("Вы действительно хотите удалить блок?")) {
    let url = "/dashboard/explanation/" + explanation_id + "/delete/";

    $.post(url, {})
      .done(function() {
        $("#explanation-"+explanation_id).remove();
      })
      .fail(function() {
        alert("Ошибка при удалении");
      })
  }
}
