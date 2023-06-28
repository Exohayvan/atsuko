document.addEventListener("DOMContentLoaded", function() {
    var numDots = 200; // Increase the number of dots for better coverage
    var bodyRect = document.body.getBoundingClientRect();

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.floor(Math.random() * bodyRect.height) + "px";
        dot.style.left = Math.floor(Math.random() * bodyRect.width) + "px";
        // Assign random ending points
        dot.style.setProperty('--end-left', Math.floor(Math.random() * bodyRect.width) + "px");
        dot.style.setProperty('--end-top', Math.floor(Math.random() * bodyRect.height) + "px");
        dot.style.animationDuration = Math.random() * 10 + "s";
        document.body.appendChild(dot);
    }
});
