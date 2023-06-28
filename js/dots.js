document.addEventListener("DOMContentLoaded", function() {
    var numDots = 50;
    var bodyRect = document.body.getBoundingClientRect();

    document.body.setAttribute("data-width", bodyRect.width);
    document.body.setAttribute("data-height", bodyRect.height);

    var diagonal = Math.sqrt(bodyRect.width**2 + bodyRect.height**2);

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.floor(Math.random() * bodyRect.height) + "px";
        dot.style.left = "0px";
        dot.style.animationDuration = (diagonal / (Math.random() * 50 + 50)) + "s";
        document.body.appendChild(dot);
    }

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = "0px";
        dot.style.left = Math.floor(Math.random() * bodyRect.width) + "px";
        dot.style.animationDuration = (diagonal / (Math.random() * 50 + 50)) + "s";
        document.body.appendChild(dot);
    }
});
