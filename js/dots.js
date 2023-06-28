document.addEventListener("DOMContentLoaded", function() {
    var numDots = 200;  // Increase this if you want more dots
    var bodyRect = document.body.getBoundingClientRect();
    var directions = ['top', 'right', 'bottom', 'left'];

    for (var i = 0; i < numDots; i++) {
        var dot = document.createElement("div");
        var direction = directions[Math.floor(Math.random() * directions.length)];
        dot.classList.add("dot");
        dot.classList.add(direction);
        switch (direction) {
            case 'top':
                dot.style.top = "0px";
                dot.style.left = Math.random() * bodyRect.width + "px";
                break;
            case 'right':
                dot.style.top = Math.random() * bodyRect.height + "px";
                dot.style.right = "0px";
                break;
            case 'bottom':
                dot.style.bottom = "0px";
                dot.style.left = Math.random() * bodyRect.width + "px";
                break;
            case 'left':
                dot.style.top = Math.random() * bodyRect.height + "px";
                dot.style.left = "0px";
                break;
        }
        dot.style.animationDuration = (5) + "s";
        document.body.appendChild(dot);
    }
});
