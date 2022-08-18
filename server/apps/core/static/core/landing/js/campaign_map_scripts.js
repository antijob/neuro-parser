var map_data = null;
var chart_description = null;
let regions = null;


$(document).ready(function() {

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

    onLabelShow: function (event, label, region_code) {
      let data = getMapData()[region_code];
      if (!data) return;

      let labelText = '<strong>' + label.text() + '</strong><br>';
      labelText += "<p>Инцидентов:" + data.count + "</p>"
      label.html(labelText);
      if (Object.keys(data.chart_data).length) {
        drawChart(label, data);
      }
    },
  });

  function drawChart(label, data, chart_data) {
      let labelText = label.html();
      if (chart_description) {
        labelText += ("<p><strong>" + chart_description + "</strong></p>");
      }
      if (Object.keys(data.chart_data).length) {
        labelText += '<canvas id="chart"></canvas><span id="legend"></span>';
      }
      label.html(labelText);

      let canvas = document.getElementById('chart');
      let graph = new PieChart(canvas, 70, 70, 70);
      let chart_colors = ["rgb(77, 122, 171)",
                          "rgb(209, 105, 122)",
                          "rgb(107, 214, 189)",
                          "rgb(210, 107, 214)",
                          "rgb(194, 158, 79)"];
      let summ = Object.values(data.chart_data).reduce((a, b) => a + b, 0);
      let color = 0;
      let percents = {};
      let legend = $("#legend");
      let legendText = "";
      for (key in data.chart_data) {
        let percent = data.chart_data[key] * 100 / summ;
        graph.items.push(new PieChartDataItem(percent, chart_colors[color]));
        color += 1;
        legendText += ("<p>" + key + " - " + percent + "% </p>")
      }
      graph.draw();
      legend.html(legendText);

  }

  function getMapData() {
    let result = {};
    if (!map_data) return result;

    for (let i in map_data) {
      let region = map_data[i]['region'];
      let region_data = Object.assign({}, map_data[i]);
      region_code = region.replace("RU-", "").replace("UA-", "");
      let count = map_data[i].count;
      let chart_value = map_data[i].chart_field;
      if (result[region_code]) {
        result[region_code]["count"] += count;
        if (chart_value) {
          let chart_count = result[region_code]["chart_data"][chart_value] || 0;
          result[region_code]["chart_data"][chart_value] = chart_count + count;
        }
      } else {
        result[region_code] = {"count": count, "chart_data": {}};
        if (chart_value) {
          result[region_code]["chart_data"][chart_value] = count;
        }
      }
      console.log(result[region_code])
    }
    return result
  }

  function paintRegions() {
    let jsonData = getMapData();
    let highlightedRegions = {};
    for (let i in jsonData) {
      let count = jsonData[i].count;
      if (count) {
        if (count >= 1 && count <= 5) {
          highlightedRegions[i] = '#faffb9';
        } else if (count <= 10) {
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

  function drawMap() {
    // let sendData = {"campaign": 23 };
    $.get("data/").done(function(data) {
      map_data = data.map_data;
      chart_description = data.chart_description;
      paintRegions();
    });
  }

  function init() {
    $.get("data/").done(function(data) {
      incident_type_names = data.incident_type_names;
      regions = data.regions;
      $.each(regions, function(i, pair) {
        let regionCode = pair[0];
        let regionName = pair[1];
        $("#region").append('<option value=' + regionCode + '>' + regionName + '</option>');
      });

      drawMap();

    });
  }

  init();

});
""
