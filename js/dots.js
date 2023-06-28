document.addEventListener("DOMContentLoaded", function() {
    var numDots = 50;
    var container = document.querySelector(".container");
    var containerRect = container.getBoundingClientRect();
  
    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.random() * containerRect.height + "px";
        dot.style.left = Math.random() * containerRect.width + "px";
        dot.style.animationDelay = Math.random() * 10 + "s";
        container.appendChild(dot);
    }
});
