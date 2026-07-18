document.addEventListener('DOMContentLoaded', () => {
    initAuroraCanvas();
    initFadeIn();
    initStaggerCards();
    initNavHover();
    initPulseBadge();
    initPanelReveal();
});

function initAuroraCanvas() {
    const canvas = document.getElementById('aurora-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    const particles = [];
    const colors = [
        'rgba(34, 211, 238, 0.15)',
        'rgba(167, 139, 250, 0.12)',
        'rgba(52, 211, 153, 0.1)',
        'rgba(244, 114, 182, 0.08)',
        'rgba(96, 165, 250, 0.1)',
    ];

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

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

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

        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(34, 211, 238, ${0.04 * (1 - dist / 120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(animate);
    }
    animate();
}

function initFadeIn() {
    const elements = document.querySelectorAll('.main > *');
    elements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(16px)';
        el.style.transition = `opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s, transform 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s`;
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            });
        });
    });
}

function initStaggerCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px) scale(0.97)';
        card.style.transition = `opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1) ${0.1 + i * 0.08}s, transform 0.45s cubic-bezier(0.16, 1, 0.3, 1) ${0.1 + i * 0.08}s, border-color 0.3s ease, box-shadow 0.3s ease`;
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0) scale(1)';
            });
        });

        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-6px) scale(1.01)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function initNavHover() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            const icon = item.querySelector('.icon');
            if (icon) {
                icon.style.transition = 'transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1)';
                icon.style.transform = 'scale(1.2)';
            }
        });
        item.addEventListener('mouseleave', () => {
            const icon = item.querySelector('.icon');
            if (icon) {
                icon.style.transition = 'transform 0.25s ease';
                icon.style.transform = 'scale(1)';
            }
        });
    });
}

function initPulseBadge() {
    const badges = document.querySelectorAll('.badge-role');
    badges.forEach(badge => {
        badge.addEventListener('mouseenter', () => {
            badge.style.transform = 'scale(1.1)';
            badge.style.transition = 'transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1)';
        });
        badge.addEventListener('mouseleave', () => {
            badge.style.transform = 'scale(1)';
        });
    });
}

function initPanelReveal() {
    const panels = document.querySelectorAll('.panel');
    panels.forEach((panel, i) => {
        panel.style.opacity = '0';
        panel.style.transform = 'translateY(12px)';
        panel.style.transition = `opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1) ${0.25 + i * 0.12}s, transform 0.45s cubic-bezier(0.16, 1, 0.3, 1) ${0.25 + i * 0.12}s, border-color 0.3s ease, box-shadow 0.3s ease`;
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                panel.style.opacity = '1';
                panel.style.transform = 'translateY(0)';
            });
        });
    });
}
