const DEFAULT_YEAR = 2020;
const lineCharts = {};
const COLORS = ['#68bfed', '#F5D880', '#4F9791', '#a292f7', '#FF8467', '#4bdb60', '#c72054', "#8f8f53", "#FFFFFF", "#dfa6f7"];
const LINE_CHART_MAX_COUNT = 4;
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
};
const datasets = [];
const lineCtx = document.getElementById('incidents_line_chart').getContext('2d');
const pieCtx = document.getElementById('pie_chart').getContext('2d');
var lineChart = null;
var pieChart = null;
var lineChartCounter = 0;
var lineChartIndex = 0;
var dateRangeSelected = false;

const filterTemplate = (index, chartId, color, removeDisabled) => `
<div id=${chartId} class="filter d-flex flex-row mb-2" data-index="${index}">
  <div class="color_picker mr-2 mb-auto"><input type="color" name="color" value="${color}"></div>
  <div class="row mr-2">
    <div class="col-xl-3 col-lg-3 col-md-12">
      <select name="region" class="form-control"></select>
    </div>
    <div class="col-xl-3 col-lg-3 col-md-12">
      <select name="category" class="form-control">
        <option value="">Все категории</option>
      </select>
    </div>
    <div class="col-xl-3 col-lg-3 col-md-12">
      <select name="tag" class="form-control">
        <option value="">Все теги</option>
      </select>
    </div>
    <span class="col-xl-3 col-lg-3 col-md-12">
      <select name="dates" class="form-control">
      </select>
    </span>
  </div>
  <div class="remove_button btn btn-sm btn-outline-danger my-auto p-1 ${removeDisabled}">&#10006;</div>
</div>`;

function getCategoryId(categoryName) {
  if (categoryName == "") {
    return -1
  } else {
    return CATEGORY_INDEXES[categoryName];
  }
}
function getChartId(element) {
  element.closest(".filter").attr("id")
}

function getInput(filterBlock, name) {
  let input = filterBlock.find('input[name="' + name + '"]');
  if (input.length) {
    return $(input[0])
  };
  return $(filterBlock.find('select[name="' + name + '"]')[0]);
}

function setLineFilterOptions(filterBlock) {
  $.get("/incidents/filter-data/").done(function(data) {
    let incident_type_names = data.incident_type_names;
    let regions = data.regions;
    let tags = data.tags;
    let regionElement = getInput(filterBlock, "region");
    let tagElement = getInput(filterBlock, "tag");
    let categoryElement = getInput(filterBlock, "category");
    $.each(regions, function(i, pair) {
      let regionCode = pair[0];
      let regionName = pair[1];
      regionElement.append('<option value=' + regionCode + '>' + regionName + '</option>');
    });
    $.each(tags, function(i, tagName) {
      tagElement.append('<option value=' + tagName + '>' + tagName + '</option>');
    });
    $.each(incident_type_names, function(categoryId, categoryName) {
      categoryElement.append('<option value=' + categoryId + '>' + categoryName + '</option>');
    });
  });
};


function setPieFilterOptions(filterBlock) {
  $.get("/incidents/filter-data/").done(function(data) {
    let regions = data.regions;
    let regionElement = getInput(filterBlock, "region");
    $.each(regions, function(i, pair) {
      let regionCode = pair[0];
      let regionName = pair[1];
      regionElement.append('<option value=' + regionCode + '>' + regionName + '</option>');
    });
  });
};


function setLineDatePicker(filterBlock) {
  let datesInput = getInput(filterBlock, "dates");
  for (year=2015; year < new Date().getFullYear(); year++) {
    datesInput.append('<option ' + ((year == DEFAULT_YEAR && !dateRangeSelected) ? 'selected': '') + '>' + year + '</option>');
  };
  datesInput.append('<option value="all" ' + (dateRangeSelected ? 'selected': '') + '>За всё время наблюдений </option>');
};

function updateChartData(chartId, newData) {
  Object.keys(newData).forEach(function(key) {
    lineCharts[chartId][key] = newData[key];
  });
};

function loadLineChartData(filterBlock) {
  let key = filterBlock.attr("id");
  let index = filterBlock.data("index");
  let tag = getInput(filterBlock, "tag").val()
  let region = getInput(filterBlock, "region").val()
  let categoryName = getInput(filterBlock, "category").val()
  let categoryId = null;
  if (categoryName && categoryName != 'total') {
    categoryId = getCategoryId(categoryName);
  }
  let date = getInput(filterBlock, "dates").val();
  if (date == "all") {
    var start_date = `2015-01-01`;
    var end_date = (new Date()).toISOString().slice(0,10);
  } else {
    var start_date = `${date}-01-01`;
    var end_date = `${date}-12-31`;
  }
  let requestData = {
    "tag": tag,
    "category": categoryId,
    "start_date": start_date,
    "end_date": end_date,
    "region": region,
  };

  $.get("/chart/line/", requestData)
    .done(function(data) {
      let chartData = data.chart_data;
      scale = data.scale;
      chartDataLabels = data.chart_data_labels;
      newData = {
        "filterBlock": filterBlock,
        "chartData": chartData,
        "scale": scale,
        "chartDataLabels": chartDataLabels
      };
      if (lineCharts[key]) {
        updateChartData(key, newData)
      } else {
        newData.color = COLORS[lineChartIndex % COLORS.length];
        lineCharts[key] = newData;
      }
      drawLineCharts();
    });
}

function loadPieChartData() {
  let filterBlock = $("#pie_filters");
  let region = getInput(filterBlock, "region").val();
  let slice_by = getInput(filterBlock, "slice_by").val();
  let start_date = `2015-01-01`;
  let end_date = `2020-12-31`;
  let requestData = {
    "slice_by": "incident_type",
    "start_date": $("#start_date").val(),
    "end_date": $("#end_date").val(),
    "region": region,
    "slice_by": slice_by,
  };

  $.get("/chart/pie/", requestData)
    .done(function(data) {
      pieChartData = data.chart_data;
      let pieChartLabels = data.chart_data_labels;
      let config = [{data: pieChartData, backgroundColor: COLORS, borderColor: '#333', borderWidth:1}];
      drawPieChart(pieCtx, config, pieChartLabels);
    });
}

function drawLineCharts() {
  let datasets = [];
  let counter = 0;
  for (chartId in lineCharts) {
    let color = lineCharts[chartId].color;
    datasets.push({"label": counter, "borderColor": color, "backgroundColor": color, "data": lineCharts[chartId]["chartData"], "fill": false})
  }
  drawLineChart(lineCtx, datasets, scale, chartDataLabels)
}

function drawLineChart(ctx, datasets, scale, chartDataLabels) {
  if (lineChart) { lineChart.destroy()}
  lineChart = new Chart(ctx, {
      type: 'line',
      data: {
          labels: chartDataLabels,
          datasets: datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          xAxes: [{
            scaleLabel: {
              display: true,
              labelString: ['Дни', 'Месяцы', 'Годы'][scale],
            },
            ticks: {
              callback: function(value, index, values) {
                let d = new Date(value * 1000);
                let t = [d.getDate(), d.toLocaleString('default', { month: 'long' }), d.getFullYear()][scale]
                return t;
              }
            },
            gridLines: {
              color: "#333",
            },
          }],
          yAxes: [{
            scaleLabel: {
              display: true,
              labelString: 'Инциденты'
            },
            ticks: {
              beginAtZero: true,
            },
            gridLines: {
              color: "#333",
            },
          }],
        },
        legend: {
          display: false,
        },
      },
  });
};


function drawPieChart(ctx, datasets, chartDataLabels) {
  if (pieChart) { pieChart.destroy() };
  $("#pie_chart_message").html("");
  $("#pie_legend").html("");

  const sum = (x, y) => x + y;
  let summ = datasets[0].data.reduce(sum);
  if (summ == 0) {
    $("#pie_chart_message").html("Нет инцидентов с указанными параметрами");
    return;
  }

  pieChart = new Chart(ctx, {
      type: 'pie',
      data: {
          labels: chartDataLabels,
          datasets: datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        legend: {
          display: false,
        },
      },
  });

  let legendItems = datasets[0].data.map(function(e, i) {
    let color = COLORS[i];
    return "<li><span style='background: " + color + "'> </span> " + chartDataLabels[i] + ": " + e + "</li>";
  });
  $("#pie_legend").html(legendItems.join(""));
};

function removeChart(chartId) {
  $("#" + chartId).remove();
  delete lineCharts[chartId];
  lineChartCounter--;
  if (lineChartCounter < LINE_CHART_MAX_COUNT) {
     $("#add_line_chart").show();
  }
  if (lineChartCounter <= 1) {
    $(".remove_button").addClass('disabled');
  }
  drawLineCharts();
}

function addLineChart() {
  lineChartCounter++;
  lineChartIndex++;
  if (lineChartCounter >= LINE_CHART_MAX_COUNT) {
    $("#add_line_chart").hide();
  }
  if (lineChartCounter > 1) {
     $(".remove_button").removeClass('disabled');
  }

  let chartId = "filter" + lineChartIndex;
  let removeDisabled = (lineChartCounter - 1) ? "" : "disabled";
  let filterHTML = filterTemplate(lineChartIndex, chartId, COLORS[lineChartIndex % COLORS.length], removeDisabled);
  let filterBlock = $(filterHTML);
  $("#line_filters").append(filterBlock);

  setLineDatePicker(filterBlock);
  setLineFilterOptions(filterBlock);

  let tag = getInput(filterBlock, "tag");
  let region = getInput(filterBlock, "region");
  let category = getInput(filterBlock, "category");
  let dates = getInput(filterBlock, "dates");
  let color = getInput(filterBlock, "color");
  let removeButton = filterBlock.find(".remove_button");

  tag.change(function() {
    loadLineChartData(filterBlock);
  });
  category.change(function() {
    loadLineChartData(filterBlock);
  });
  region.change(function() {
    loadLineChartData(filterBlock);
  });
  dates.change(function() {
    dateRangeSelected = ($(this).val() == "all");
    loadLineChartData(filterBlock);
  });
  color.change(function() {
    lineCharts[chartId].color = color.val();
    drawLineCharts();
  })
  removeButton.click(function() {
    if (!$(this).hasClass('disabled')) {
      removeChart(chartId);
    }
  })

  loadLineChartData(filterBlock);
}

function setupPieDatePicker() {
  let ranges = {
    'За всё время': [moment([2015, 0, 1]), moment()],
  }
  for (year=2015; year < new Date().getFullYear(); year++) {
    ranges[year] = [moment([year, 0, 1]), moment([year, 11, 31])]
  }

  datePicker = $('#pie_dates').daterangepicker({
    ranges: ranges,
    startDate: moment("2015-01-01"),
    endDate: moment(),
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

  $("#start_date").val("2015-01-01");
  $("#end_date").val(moment().format("YYYY-MM-DD"));

  $('#pie_dates').on('apply.daterangepicker', function(ev, picker) {
    start_date = picker.startDate.format('YYYY-MM-DD');
    end_date = picker.endDate.format('YYYY-MM-DD');
    $("#start_date").val(start_date);
    $("#end_date").val(end_date);
    $('#pie_dates').val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    loadPieChartData();
  });

  $('#pie_dates').on('apply.daterangepicker', function(ev, picker) {
    start_date = picker.startDate.format('YYYY-MM-DD');
    end_date = picker.endDate.format('YYYY-MM-DD');
    $("#start_date").val(start_date);
    $("#end_date").val(end_date);
    $('#pie_dates').val(picker.startDate.format('DD.MM.YYYY') + ' - ' + picker.endDate.format('DD.MM.YYYY'));
    loadPieChartData();
  });

  $('#pie_dates').on('cancel.daterangepicker', function(ev, picker) {
    $("#start_date").val(null);
    $("#end_date").val(null);
    $('#pie_dates').val('');
    loadPieChartData();
  });
}

function addPieChart() {
  let filterBlock = $("#pie_filters");
  setPieFilterOptions(filterBlock);

  let region = getInput(filterBlock, "region");
  let slice_by = getInput(filterBlock, "slice_by");

  region.change(function() {
    loadPieChartData();
  });
  slice_by.change(function() {
    loadPieChartData();
  });

  loadPieChartData();
}

addLineChart();
$("#add_line_chart").on("click", addLineChart);

setupPieDatePicker();
addPieChart();


// Map to image
$("#download_line_chart").on("click", function() {
  let node = document.getElementById("line_chart_block");
  let mark = document.createElement("div");
  mark.innerHTML = "по данным runet.report";
  node.appendChild(mark);
  domtoimage.toPng(node)
    .then (function (dataUrl) {
      node.removeChild(mark);
      let link = document.createElement("a");
      let image = dataUrl.replace("image/png", "image/octet-stream");
      link.href = image;
      link.download = "runet_report_chart.png";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
});
