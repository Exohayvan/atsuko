document.addEventListener("DOMContentLoaded", function() {
    var numDots = 50;
    var bodyRect = document.body.getBoundingClientRect();
    var dotSize = 10;

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = getRandomPosition(0, bodyRect.height - dotSize) + "px";
        dot.style.left = getRandomPosition(0, bodyRect.width - dotSize) + "px";
        dot.style.animationDelay = Math.random() * 10 + "s";
        document.body.appendChild(dot);
    }
});

function getRandomPosition(min, max) {
    return Math.random() * (max - min) + min;
}
