let map_data = null;
let incident_type_names = null;
let regions = null;
let tags = null;
let incidentTable = null;

const COLUMNS = [
  {data: 'region', visible: false},
  {data: 'region_display', width: "20%"},
  {data: 'any_title'},
  {data: 'create_date', width: "12%"}
];
const CATEGORY_INDEXES = {
  other: 0,
  prosecution: 1,
  administrative: 2,
  regulation: 4,
  violence: 5,
  access: 6,
  civil: 7,
  cyberattack: 8,
  business: 9,
  shutdown: 10,
  personal_info_request: 11,
}

const COLUMN_DEFS = [
  {
    render: function (data, type, row) {
      if (row.urls && row.urls.length) {
        title = '<a href="' + row.urls[0] + '" target="_blank">' + data + ' &#129109;</a>';
      } else {
        title = data;
      }
      return title;
    },
    targets: 2
  },
];

$(document).ready(function () {

  let $russianFederation = $('#russia')
  $russianFederation.vectorMap({
    map: 'russia',
    backgroundColor: '#0D2129',
    borderColor: '#fff',
    borderWidth: 1,
    color: '#0D2129',
    enableZoom: true,
    hoverOpacity: 0.6,
    selectedColor: '',
    showTooltip: true,

    onLabelShow: function (event, label, code) {
      let data = getMapData();
      let labelText = '<strong>' + label.text() + '</strong><br>';
      let counters = data[code];
      if (counters) {
        for (let [type, count] of Object.entries(counters)) {
          let incident_type_name = incident_type_names[type];
          if (count && incident_type_name) {
            let listItem = '<li>' + incident_type_name + ': ' + count + '</li>';
            labelText += ("<ul>" + listItem + "</ul>");
          }
        }
      }
      label.html(labelText);
    },
    onRegionSelect: function (event, code, region) {
      $('#region option[value$="-' + code + '"]').attr('selected', 'selected');
      incidentTable.draw();
    },
  });

  function sumRegionData(a, b) {
    let result = {};
    for (let incident_type of Object.keys(incident_type_names)) {
      if (a[incident_type] || b[incident_type]) {
        result[incident_type] = (a[incident_type] || 0) + (b[incident_type] || 0);
      }
    }
    result.total = (a.total || 0) + (b.total || 0);
    for (let tag of tags) {
      if (a[tag] || b[tag]) {
        result[tag] = a[tag] + b[tag];
      }
    }
    return result;
  }

  function getMapData() {
    let result = {};
    if (!map_data) return result;
    result.summ = {};

    for (let i in map_data) {
      let region = map_data[i]['region'];
      let region_data = Object.assign({}, map_data[i]);

      if (region in result) {
        result[region] = sumRegionData(result[region], region_data)
      } else {
        result[region] = region_data
      }
      if (region_data) {
        result.summ = sumRegionData(result.summ, region_data);
      }
    }

    for (region of regions) {
      let region_code = region[0].replace("RU-", "").replace("UA-", "");
      if (!(region_code in result)) {
        result[region_code] = {total: 0};
      }
    }
    return result
  }

  function paintRegions() {
    let jsonData = getMapData();
    let totalcategoriesData = {}

    if (Object.hasOwnProperty.call(jsonData, "summ")) {
      jsonData["summ"]["access"] = jsonData["RU"]["access"]
    }

    Object.keys(jsonData.summ).forEach((k) => {
      if (incident_type_names[k]) {
        totalcategoriesData[k] = "<li>" + incident_type_names[k] + ": " + jsonData.summ[k] + "</li>";
      }
    });

    if (Object.keys(totalcategoriesData).length) {
      $(".total ul").html(Object.values(totalcategoriesData).reduce((a, b) => a + (b || "")));
    } else {
      $(".total ul").html("Нет инцидентов");
    }

    let highlightedRegions = {};
    for (let i in jsonData) {
      let count = jsonData[i].total;
      if (count) {
        if (count >= 1 && count <= 3) {
          highlightedRegions[i] = '#faffb9';
        } else if (count <= 9) {
          highlightedRegions[i] = '#d0ba91';
        } else if (count <= 29) {
          highlightedRegions[i] = '#965e5d';
        } else {
          highlightedRegions[i] = '#5d012a';
        }
      } else {
        highlightedRegions[i] = '#1a3039';
      }
    }
    $russianFederation.vectorMap('set', 'colors', highlightedRegions);
  }

  function getCategoryId(categoryName) {
    if (categoryName === "") {
      return -1
    } else {
      return CATEGORY_INDEXES[categoryName];
    }
  }

  function drawMap() {
    let tag = $('#tag').val();
    let categoryName = $('#category').val();
    let categoryId = null;
    if (categoryName && category !== 'total') {
      categoryId = getCategoryId(categoryName);
    }
    let start = $("#start_date").val();
    let end = $("#end_date").val();
    let sendData = {"tag": tag, "category": categoryId, "start": start, "end": end};
    $.get("map-data/", sendData).done(function (data) {
      map_data = data.map_data;
      paintRegions();
    });
  }

  function init() {
    $.get("filter-data/").done(function (data) {
      incident_type_names = data.incident_type_names;
      regions = data.regions;
      tags = data.tags;
      $.each(regions, function (i, pair) {
        let regionCode = pair[0] || "RU";
        let regionName = pair[1];
        $("#region").append('<option value=' + regionCode + '>' + regionName + '</option>');
      });
      $.each(tags, function (i, tagName) {
        $("#tag").append('<option value=' + tagName + '>' + tagName + '</option>');
      });
      $.each(incident_type_names, function (categoryId, categoryName) {
        $("#category").append('<option value=' + categoryId + '>' + categoryName + '</option>');
      });

      drawMap();

      incidentTable = $('#table').DataTable({
        ajax: {
          url: "table-data/",
          data: function (d) {
            d.region = $("#region").val();
            d.tag = $("#tag").val();
            let categoryName = $("#category").val();
            d.category = getCategoryId(categoryName);
            d.start_date = $("#start_date").val();
            d.end_date = $("#end_date").val();
          },
        },
        serverSide: true,
        columns: COLUMNS,
        columnDefs: COLUMN_DEFS,
        order: [[3, "desc"]],
        sDom: 'rt<"bottom"p>',
        language: {
          lengthMenu: "Display _MENU_ records per page",
          zeroRecords: "Нет инцидентов",
          search: "Поиск",
          info: "Показана _PAGE_ страница из _PAGES_",
          infoEmpty: "Нет инцидентов",
          infoFiltered: "(filtered from _MAX_ total records)",
          paginate: {
            "first": "Первая",
            "previous": "Назад",
            "next": "Вперед",
            "last": "Последняя"
          },
        },
        pagingType: "numbers"
      });
    });
  }

  let ranges = {
    'Этот месяц': [moment().startOf('month'), moment().endOf('month')],
    'Предыдущий месяц': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
    'За всё время': [moment([2015, 0, 1]), moment()],
  }
  for (year = 2015; year < new Date().getFullYear(); year++) {
    ranges[year] = [moment([year, 0, 1]), moment([year, 11, 31])]
  }

  datePicker = $('#dates').daterangepicker({
    ranges: ranges,
    startDate: moment("2021-01-01"),
    endDate: moment("2021-12-31"),
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
    autoUpdateInput: true,
    autoApply: true,
  });

  $("#start_date").val("2021-01-01");
  $("#end_date").val("2021-12-31");

  $('#dates').on('apply.daterangepicker', function (ev, picker) {
    start_date = picker.startDate.format('YYYY-MM-DD');
    end_date = picker.endDate.format('YYYY-MM-DD');
    $("#start_date").val(start_date);
    $("#end_date").val(end_date);
    $('#dates').val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    drawMap();
    incidentTable.draw()
  });

  $('#dates').on('apply.daterangepicker', function (ev, picker) {
    start_date = picker.startDate.format('YYYY-MM-DD');
    end_date = picker.endDate.format('YYYY-MM-DD');
    $("#start_date").val(start_date);
    $("#end_date").val(end_date);
    $('#dates').val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    drawMap();
    incidentTable.draw()
  });

  $('#dates').on('cancel.daterangepicker', function (ev, picker) {
    $("#start_date").val(null);
    $("#end_date").val(null);
    $('#dates').val('');
    drawMap();
    incidentTable.draw()
  });

  $("#tag").change(function () {
    drawMap();
    incidentTable.draw();
  });

  $("#category").change(function () {
    drawMap();
    incidentTable.draw();
  });

  init();

  $("#region").change(function () {
    incidentTable.draw()
  });
  $("#search").keyup(function () {
    incidentTable.search($(this).val()).draw()
  });

  // Map to image
  let node = document.getElementById("map");
  let mark = document.createElement("div");
  mark.innerHTML = "https://runet.report/";
  $("#downloadMap").on("click", function () {
    node.appendChild(mark);
    domtoimage.toPng(node)
      .then(function (dataUrl) {
        node.removeChild(mark);
        let link = document.createElement("a");
        let image = dataUrl.replace("image/png", "image/octet-stream");
        link.href = image;
        link.download = "runet_report_map.png";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
  });

  $("#export").click(function () {
    let query = {};
    query.region = $("#region").val();
    query.tag = $("#tag").val();
    query["search[value]"] = $("#search").val();
    let categoryName = $("#category").val();
    query.category = getCategoryId(categoryName);
    query.start_date = $("#start_date").val();
    query.end_date = $("#end_date").val();
    let urlParams = new URLSearchParams();
    for (const [key, value] of Object.entries(query)) {
      urlParams.set(key, value);
    }
    let url = "/incidents/export/?" + urlParams.toString();
    location.replace(url);
  });

});
