document.addEventListener("DOMContentLoaded", function() {
    var numDots = 50;
    var dotsContainer = document.createElement("div");
    dotsContainer.classList.add("dots-container");
    document.body.appendChild(dotsContainer);
    var containerRect = document.querySelector(".container").getBoundingClientRect();

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.random() * containerRect.height + "px";
        dot.style.left = Math.random() * containerRect.width + "px";
        dot.style.animationDelay = Math.random() * 10 + "s";
        dotsContainer.appendChild(dot);
    }
});
