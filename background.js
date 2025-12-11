

document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.createElement("canvas");
    const c = canvas.getContext("2d");
    document.body.appendChild(canvas);

    canvas.style.position = "fixed";
    canvas.style.top = 0;
    canvas.style.left = 0;
    canvas.style.zIndex = -3;
    canvas.style.pointerEvents = "none";
    canvas.style.opacity = 0.25;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener("resize", resize);
    resize();

    const particles = [];
    for (let i = 0; i < 110; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            s: Math.random() * 2 + 1,
            d: Math.random() * 0.5
        });
    }

    function draw() {
        c.clearRect(0, 0, canvas.width, canvas.height);
        c.fillStyle = "#00ff99";

        particles.forEach(p => {
            c.beginPath();
            c.arc(p.x, p.y, p.s, 0, Math.PI * 2);
            c.fill();
        });

        update();
        requestAnimationFrame(draw);
    }

    function update() {
        particles.forEach(p => {
            p.y -= p.d;
            if (p.y <= 0) p.y = canvas.height;
        });
    }

    draw();
});
