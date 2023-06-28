document.addEventListener("DOMContentLoaded", function() {
    var wrapper = document.getElementById('dot-wrapper');
    var wrapperRect = wrapper.getBoundingClientRect();
    var directions = ['left', 'right'];

    function createDot() {
        var dot = document.createElement("div");
        var direction = directions[Math.floor(Math.random() * directions.length)];
        dot.classList.add("dot");
        dot.classList.add(direction);
        dot.style.top = Math.floor(Math.random() * wrapperRect.height) + "px";
        dot.style.animationDuration = Math.random() * 5 + 5 + "s";
        wrapper.appendChild(dot);

        // Remove dot after it finishes animating
        dot.addEventListener('animationend', function() {
            wrapper.removeChild(dot);
        });

        // Limit the number of dots
        if (wrapper.querySelectorAll('.dot').length < 200) {
            setTimeout(createDot, 100);  // Create a new dot every 100ms
        }
    }
    createDot();  // Start creating dots
});
