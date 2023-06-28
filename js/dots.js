document.addEventListener("DOMContentLoaded", function() {
    var numDots = 50;
    var bodyRect = document.body.getBoundingClientRect();

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.random() * (bodyRect.height - 10) + "px";
        dot.style.animationDelay = Math.random() * 10 + "s";
        document.body.appendChild(dot);
    }
});
