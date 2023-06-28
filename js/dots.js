document.addEventListener("DOMContentLoaded", function() {
    var numDots = 100; // Increasing the number of dots
    var bodyRect = document.body.getBoundingClientRect();
    var diagonal = Math.sqrt(bodyRect.width**2 + bodyRect.height**2);

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.floor(Math.random() * bodyRect.height) + "px";
        dot.style.left = Math.floor(Math.random() * bodyRect.width) + "px"; // Random position for left and top
        dot.style.animationDuration = (diagonal / (Math.random() * 50 + 50)) + "s";
        document.body.appendChild(dot);
    }
});
