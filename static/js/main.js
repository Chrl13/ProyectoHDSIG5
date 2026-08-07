// ==========================================================
// EFECTOS VISUALES DEL DASHBOARD
// Inicializa las animaciones de la interfaz cuando carga la página
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {

    // Inicializar todos los efectos visuales
    initAuroraCanvas();
    initFadeIn();
    initStaggerCards();
    initNavHover();
    initPulseBadge();
    initPanelReveal();

});


// ==========================================================
// FONDO ANIMADO (AURORA)
// Genera el efecto de partículas en movimiento del fondo
// ==========================================================

function initAuroraCanvas() {

    const canvas = document.getElementById('aurora-canvas');

    // Si el canvas no existe, finalizar la función
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Ajustar el tamaño del canvas al tamaño de la ventana
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    resize();
    window.addEventListener('resize', resize);

    const particles = [];

    // Colores utilizados por las partículas
    const colors = [
        'rgba(34, 211, 238, 0.15)',
        'rgba(167, 139, 250, 0.12)',
        'rgba(52, 211, 153, 0.1)',
        'rgba(244, 114, 182, 0.08)',
        'rgba(96, 165, 250, 0.1)',
    ];

    // Crear las partículas del fondo
    for (let i = 0; i < 50; i++) {

        particles.push({

            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 2 + 0.5,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.3,
            color: colors[Math.floor(Math.random() * colors.length)],
            pulse: Math.random() * Math.PI * 2,
            pulseSpeed: 0.005 + Math.random() * 0.01,

        });

    }

    // Animación continua del fondo
    function animate() {

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Actualizar la posición de cada partícula
        particles.forEach(p => {

            p.x += p.vx;
            p.y += p.vy;
            p.pulse += p.pulseSpeed;

            if (p.x < 0) p.x = canvas.width;
            if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height;
            if (p.y > canvas.height) p.y = 0;

            const alpha = 0.5 + Math.sin(p.pulse) * 0.5;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius * alpha, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.fill();

        });

        // Dibujar líneas entre partículas cercanas
        for (let i = 0; i < particles.length; i++) {

            for (let j = i + 1; j < particles.length; j++) {

                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 120) {

                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);

                    ctx.strokeStyle =
                        `rgba(34, 211, 238, ${0.04 * (1 - dist / 120)})`;

                    ctx.lineWidth = 0.5;
                    ctx.stroke();

                }

            }

        }

        requestAnimationFrame(animate);

    }

    animate();

}


// ==========================================================
// EFECTO FADE IN
// Hace que los elementos aparezcan suavemente al cargar
// ==========================================================

function initFadeIn() {

    const elements = document.querySelectorAll('.main > *');

    elements.forEach((el, i) => {

        el.style.opacity = '0';
        el.style.transform = 'translateY(16px)';

        // Configurar la animación de aparición
        el.style.transition =
            `opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s,
            transform 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s`;

        requestAnimationFrame(() => {

            requestAnimationFrame(() => {

                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';

            });

        });

    });

}


// ==========================================================
// ANIMACIÓN DE TARJETAS
// Aplica efectos al cargar y al pasar el mouse
// ==========================================================

function initStaggerCards() {

    

}


// ==========================================================
// EFECTO DEL MENÚ LATERAL
// Agranda el ícono cuando el usuario pasa el mouse
// ==========================================================

function initNavHover() {



}


// ==========================================================
// ANIMACIÓN DEL BADGE DEL ROL
// Resalta el rol del usuario al pasar el cursor
// ==========================================================

function initPulseBadge() {



}


// ==========================================================
// ANIMACIÓN DE PANELES
// Hace que los paneles aparezcan suavemente
// ==========================================================

function initPanelReveal() {

    

}