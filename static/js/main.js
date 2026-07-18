document.addEventListener('DOMContentLoaded', () => {
    initFadeIn();
    initStaggerCards();
    initNavHoverSound();
    initSidebarActive();
    initPulseBadge();
    initCountUp();
});

function initFadeIn() {
    const elements = document.querySelectorAll('.main > *');
    elements.forEach((el, i) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(12px)';
        el.style.transition = `opacity 0.4s ease ${i * 0.06}s, transform 0.4s ease ${i * 0.06}s`;
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
        card.style.transform = 'translateY(16px) scale(0.97)';
        card.style.transition = `opacity 0.35s ease ${i * 0.08}s, transform 0.35s cubic-bezier(0.16, 1, 0.3, 1) ${i * 0.08}s, border-color 0.25s ease, box-shadow 0.25s ease`;
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0) scale(1)';
            });
        });

        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-4px) scale(1.01)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });
}

function initNavHoverSound() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            const icon = item.querySelector('.icon');
            if (icon) {
                icon.style.transition = 'transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)';
                icon.style.transform = 'scale(1.2)';
            }
        });
        item.addEventListener('mouseleave', () => {
            const icon = item.querySelector('.icon');
            if (icon) {
                icon.style.transition = 'transform 0.2s ease';
                icon.style.transform = 'scale(1)';
            }
        });
    });
}

function initSidebarActive() {
    const active = document.querySelector('.nav-item.active');
    if (active) {
        active.style.background = 'var(--accent-dim)';
        active.style.borderLeftColor = 'var(--accent)';
    }
}

function initPulseBadge() {
    const badges = document.querySelectorAll('.badge-role');
    badges.forEach(badge => {
        badge.addEventListener('mouseenter', () => {
            badge.style.transform = 'scale(1.08)';
            badge.style.transition = 'transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)';
        });
        badge.addEventListener('mouseleave', () => {
            badge.style.transform = 'scale(1)';
        });
    });
}

function initCountUp() {
    const panels = document.querySelectorAll('.panel');
    panels.forEach((panel, i) => {
        panel.style.opacity = '0';
        panel.style.transform = 'translateY(10px)';
        panel.style.transition = `opacity 0.35s ease ${0.2 + i * 0.1}s, transform 0.35s ease ${0.2 + i * 0.1}s`;
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                panel.style.opacity = '1';
                panel.style.transform = 'translateY(0)';
            });
        });
    });
}
