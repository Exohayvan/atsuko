document.addEventListener("DOMContentLoaded", function() {
    var bodyRect = document.body.getBoundingClientRect();
    var directions = ['left', 'right'];

    function createDot() {
        var dot = document.createElement("div");
        var direction = directions[Math.floor(Math.random() * directions.length)];
        dot.classList.add("dot");
        dot.classList.add(direction);
        dot.style.top = Math.floor(Math.random() * bodyRect.height) + "px";
        dot.style.animationDuration = Math.random() * 5 + 5 + "s";
        document.body.appendChild(dot);

        // Remove dot after it finishes animating
        dot.addEventListener('animationend', function() {
            document.body.removeChild(dot);
        });

        // Limit the number of dots
        if (document.querySelectorAll('.dot').length < 200) {
            setTimeout(createDot, 100);  // Create a new dot every 100ms
        }
    }
    createDot();  // Start creating dots
});
