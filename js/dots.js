document.addEventListener("DOMContentLoaded", function() {
    var numDots = 1000;  // Increase this if you want more dots
    var bodyRect = document.body.getBoundingClientRect();

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.floor(Math.random() * bodyRect.height) + "px"; // Initial position randomly set within the body height
        dot.style.left = Math.floor(Math.random() * bodyRect.width) + "px"; // Initial position randomly set within the body width
        dot.style.animationDuration = (Math.random() * 5 + 5) + "s"; // Random animation duration between 5 to 10 seconds
        document.body.appendChild(dot);
    }
});
