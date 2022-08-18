// ==PieChartLib.js==
// @author Mike Shamory
// @version 0.1.0
// @description A simple library for drawing a pie chart on an HTML5 canvas

var PIECHARTLIB = "0.1.0";
console.log("Running PieChartLib.js version " + PIECHARTLIB);

// This class controls the drawing of the pie chart
// Unexpected errors may occur when settings are outside of expected ranges
function PieChart(canvas, radius, x, y) {
  // Keep a referece to the object for anonymous functions
  var self = this;

  // Keep local settings in object properties
  this.ctx = canvas.getContext("2d");
  this.radius = radius;
  this.center = {x: x, y: y};
  this.background = "rgba(255,255,255,0)";
  this.border = {size: 3, color: "rgba(255,255,255,0.3)"};
  this.shadow = {offsetX: 0, offsetY: 0, blur: 10, color: "rgba(0,0,0,.3)"};
  this.offsetAngle = 0;

  // Create an array for data items
  this.items = new Array();

  // Object functions
  this.draw = function() {
    var ctx = self.ctx;
    // Clear the canvas
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

    // If there no items, draw nothing
    if (self.items.length < 1) {
      return;
    }

    // Draw the background and shadow
    ctx.fillStyle = self.background;
    ctx.shadowColor = self.shadow.color;
    ctx.shadowBlur = self.shadow.blur;
    ctx.shadowOffsetX = self.shadow.offsetX;
    ctx.shadowOffsetY = self.shadow.offsetY;

    ctx.beginPath();
    ctx.arc(self.center.x, self.center.y, self.radius, 0, 2 * Math.PI);
    ctx.fill();

    // Set the shadow color to transparent
    ctx.shadowColor = "transparent";

    // Draw the border
    ctx.lineWidth = self.border.size;
    ctx.strokeStyle = self.border.color;
    ctx.beginPath();
    ctx.arc(self.center.x, self.center.y, self.radius - self.border.size / 2, 0, 2 * Math.PI);
    ctx.stroke();

    // Set the offset to the inital angle offset from -Math.PI/2
    var offset = -Math.PI / 2 + self.offsetAngle / 100 * 2 * Math.PI;

    // Draw each of the items
    for (var i = 0; i < self.items.length; i++) {
      // Get the angle of the arc to draw for each item
      var arcAngle = self.items[i].percentOfPie / 100 * 2 * Math.PI;

      // Draw the item
      ctx.fillStyle = self.items[i].color;
      ctx.beginPath();
      ctx.arc(self.center.x, self.center.y, self.radius - self.border.size, offset, offset + arcAngle);
      ctx.lineTo(self.center.x, self.center.y);
      ctx.fill();

      // Increase the offset by the arc angle
      offset += arcAngle;
    }
  }
}

function PieChartDataItem(percent, color) {
  this.percentOfPie = percent;
  this.color = color;
}
