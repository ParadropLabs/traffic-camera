var lastTime = 0;

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

$.get("/output/counts.json", {}, function(data) {
  var newValues = [];
  for (var i = 0; i < data.length; i++) {
    newValues.push({
      time: data[i].time,
      y: data[i].count
    });
  }
  lastTime = data[data.length-1].time;

  var newData = [
    {
      label: "Count",
      values: newValues
    }
  ];
  chart.update(newData);
});

setInterval(function() {
  var src = "/output/marked.jpg?x=" + Math.random();
  $("#markedImage").attr("src", src);

  $.get("/output/counts.json?x="+Math.random(), {}, function(data) {
    for (var i = 0; i < data.length; i++) {
      if (data[i].time > lastTime) {
        chart.push([
          { time: data[i].time, y: data[i].count }
        ]);
        lastTime = data[i].time;
      }
    }

    chart.redraw();
  });
}, 1000);
