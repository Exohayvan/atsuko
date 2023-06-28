document.addEventListener("DOMContentLoaded", function() {
    var numDots = 50;
    var containerRect = document.querySelector(".container").getBoundingClientRect();

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.random() * (containerRect.height - 10) + "px";
        dot.style.left = Math.random() * (containerRect.width - 10) + "px";
        dot.style.animationDelay = Math.random() * 10 + "s";
        document.body.appendChild(dot);
    }
});
