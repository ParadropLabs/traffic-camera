// Store the last timestamp shown on the chart so that we only push new data.
var lastTime = 0;

// Request a new image periodically (time in milliseconds). Setting
// this too results in too much flickering in the webpage.
var imageUpdateInterval = 5000;

// Request new vehicle counts periodically (time in milliseconds).
var dataUpdateInterval = 1000;

// Initialize the vehicle count chart using the epoch library.
var chart = $("#countChart").epoch({
  type: "time.area",
  data: [
    {
      label: "Count",
      values: []
    }
  ],
  axes: ["left", "right", "bottom"],
  tickFormats: { time: function(d) { return new Date(time*1000).toString(); } }
});

// Request an initial set of data to show in the chart.
$.get("/output/counts.json", {}, function(data) {
  var newValues = [];
  for (var i = 0; i < data.length; i++) {
    newValues.push({
      time: data[i].time,
      y: data[i].count
    });
  }
  lastTime = data[data.length-1].time;

  // Epoch requires the data to be structured in this specific way.  It is
  // designed to show multiple data series on the same chart.  Here we have
  // just one, the vehicle count.
  var newData = [
    {
      label: "Count",
      values: newValues
    }
  ];
  chart.update(newData);

  // Start updating the chart periodically.
  setInterval(function() {
    $.get("/output/counts.json?x="+Math.random(), {}, function(data) {
      for (var i = 0; i < data.length; i++) {
        if (data[i].time > lastTime) {
          chart.push([
            { time: data[i].time, y: data[i].count }
          ]);
          lastTime = data[i].time;
        }
      }
    });
  }, dataUpdateInterval);
});

// Start updating the image periodically.
setInterval(function() {
  var src = "/output/marked.jpg?x=" + Math.random();
  $("#markedImage").attr("src", src);

  // Try to synchronize the chart with the new image.
}, imageUpdateInterval);
