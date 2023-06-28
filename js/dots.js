document.addEventListener("DOMContentLoaded", function() {
    var wrapper = document.getElementById('dot-wrapper');
    var wrapperRect = wrapper.getBoundingClientRect();

    function createDot() {
        var dot = document.createElement("div");
        dot.classList.add("dot");
        dot.style.top = Math.floor(Math.random() * wrapperRect.height) + "px";
        dot.style.left = Math.floor(Math.random() * wrapperRect.width) + "px";
        dot.style.animationDuration = (Math.random() * 5 + 5) + "s";
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
