document.addEventListener("DOMContentLoaded", function() {
    // Number of dots to generate
    var numDots = 50;

    // Generate the dots dynamically
    var container = document.querySelector(".container");
    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.random() * 100 + "vh";
        dot.style.left = Math.random() * 100 + "vw";
        dot.style.animationDelay = Math.random() * 10 + "s";
        container.appendChild(dot);
    }
});
