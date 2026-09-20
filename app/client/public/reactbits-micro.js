/**
 * ReactBits Micro-Interaction Enhancements for Emory Lab Atlas
 * Injects fluid, spring-physics micro-interactions inspired by https://reactbits.dev/c/micro
 */
(function() {
  'use strict';

  // 1. Fluid Custom Smooth Cursor Glow (Dodge Field / Magnetic hover vibe)
  function initMagneticCursor() {
    if (window.matchMedia('(pointer: coarse)').matches) return;
    const dot = document.createElement('div');
    dot.className = 'rb-cursor-dot';
    document.body.appendChild(dot);

    let mouseX = -100, mouseY = -100;
    let dotX = -100, dotY = -100;
    let isHoveringInteractive = false;

    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    }, { passive: true });

    function renderCursor() {
      // Lerp for fluid glide
      dotX += (mouseX - dotX) * 0.22;
      dotY += (mouseY - dotY) * 0.22;

      dot.style.transform = `translate3d(${dotX}px, ${dotY}px, 0) translate(-50%, -50%) scale(${isHoveringInteractive ? 1.75 : 1})`;
      requestAnimationFrame(renderCursor);
    }
    requestAnimationFrame(renderCursor);

    document.addEventListener('mouseover', (e) => {
      const target = e.target.closest('button, a, input, select, textarea, .card, .unit-card, .pub, .chip, [role="button"]');
      if (target) {
        isHoveringInteractive = true;
        dot.classList.add('active');
      }
    });

    document.addEventListener('mouseout', (e) => {
      const target = e.target.closest('button, a, input, select, textarea, .card, .unit-card, .pub, .chip, [role="button"]');
      if (target) {
        isHoveringInteractive = false;
        dot.classList.remove('active');
      }
    });
  }

  // 2. Swipe Toast Micro-Interaction (ReactBits /c/micro/swipe-toast)
  function initSwipeToast() {
    let container = document.getElementById('rb-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'rb-toast-container';
      container.className = 'rb-toast-container';
      document.body.appendChild(container);
    }

    window.showReactBitsToast = function(options) {
      const {
        title = 'Notice',
        description = '',
        icon = '✨',
        actionLabel = '',
        onAction = null,
        duration = 4200
      } = typeof options === 'string' ? { title: options } : options;

      const toast = document.createElement('div');
      toast.className = 'rb-swipe-toast';

      toast.innerHTML = `
        <div class="rb-toast-card">
          <div class="rb-toast-icon">${icon}</div>
          <div class="rb-toast-content">
            <div class="rb-toast-title">${title}</div>
            ${description ? `<div class="rb-toast-desc">${description}</div>` : ''}
          </div>
          ${actionLabel ? `<button class="rb-toast-action">${actionLabel}</button>` : ''}
          <button class="rb-toast-close" aria-label="Dismiss">✕</button>
          <div class="rb-toast-fuse" style="animation-duration: ${duration}ms"></div>
        </div>
      `;

      container.appendChild(toast);

      // Force layout then activate entry
      requestAnimationFrame(() => {
        toast.classList.add('on');
      });

      let timer = setTimeout(dismiss, duration);

      function dismiss() {
        clearTimeout(timer);
        toast.classList.remove('on');
        toast.classList.add('exit');
        setTimeout(() => {
          if (toast.parentNode) toast.parentNode.removeChild(toast);
        }, 340);
      }

      // Close button
      const closeBtn = toast.querySelector('.rb-toast-close');
      if (closeBtn) closeBtn.onclick = dismiss;

      // Action button
      if (actionLabel && onAction) {
        const actBtn = toast.querySelector('.rb-toast-action');
        if (actBtn) {
          actBtn.onclick = () => {
            onAction();
            dismiss();
          };
        }
      }

      // Pause on hover
      toast.addEventListener('mouseenter', () => {
        const fuse = toast.querySelector('.rb-toast-fuse');
        if (fuse) fuse.style.animationPlayState = 'paused';
        clearTimeout(timer);
      });

      toast.addEventListener('mouseleave', () => {
        const fuse = toast.querySelector('.rb-toast-fuse');
        if (fuse) fuse.style.animationPlayState = 'running';
        timer = setTimeout(dismiss, 1800);
      });

      // Swipe to dismiss gesture
      let startX = 0;
      let currentX = 0;
      let isDragging = false;

      toast.addEventListener('pointerdown', (e) => {
        startX = e.clientX;
        isDragging = true;
        toast.style.transition = 'none';
      });

      window.addEventListener('pointermove', (e) => {
        if (!isDragging) return;
        currentX = e.clientX - startX;
        if (currentX > 0) {
          toast.style.transform = `translateX(${currentX}px) scale(${1 - currentX / 600})`;
          toast.style.opacity = `${1 - currentX / 240}`;
        }
      });

      window.addEventListener('pointerup', () => {
        if (!isDragging) return;
        isDragging = false;
        toast.style.transition = '';
        if (currentX > 80) {
          dismiss();
        } else {
          toast.style.transform = '';
          toast.style.opacity = '';
        }
        currentX = 0;
      });
    };
  }

  // 3. Warm Tooltip Micro-Interaction (ReactBits /c/micro/warm-tooltip)
  function initWarmTooltips() {
    let tooltipEl = document.getElementById('rb-warm-tooltip');
    if (!tooltipEl) {
      tooltipEl = document.createElement('div');
      tooltipEl.id = 'rb-warm-tooltip';
      tooltipEl.className = 'rb-warm-tooltip';
      tooltipEl.innerHTML = '<span class="rb-warm-text"></span><span class="rb-warm-arrow"></span>';
      document.body.appendChild(tooltipEl);
    }

    let activeTrigger = null;
    let hideTimer = null;
    let showTimer = null;
    let isWarm = false;
    let warmTimer = null;

    function showTooltip(el, text) {
      clearTimeout(hideTimer);
      clearTimeout(showTimer);

      const delay = isWarm ? 40 : 280;

      showTimer = setTimeout(() => {
        activeTrigger = el;
        const rect = el.getBoundingClientRect();
        const textSpan = tooltipEl.querySelector('.rb-warm-text');
        textSpan.textContent = text;

        tooltipEl.style.display = 'block';
        const ttRect = tooltipEl.getBoundingClientRect();

        let top = rect.top - ttRect.height - 8;
        let left = rect.left + (rect.width - ttRect.width) / 2;

        if (top < 10) {
          top = rect.bottom + 8;
          tooltipEl.classList.add('bottom');
        } else {
          tooltipEl.classList.remove('bottom');
        }

        left = Math.max(10, Math.min(window.innerWidth - ttRect.width - 10, left));

        tooltipEl.style.top = `${top + window.scrollY}px`;
        tooltipEl.style.left = `${left + window.scrollX}px`;

        requestAnimationFrame(() => {
          tooltipEl.classList.add('visible');
        });

        isWarm = true;
        clearTimeout(warmTimer);
      }, delay);
    }

    function hideTooltip() {
      clearTimeout(showTimer);
      hideTimer = setTimeout(() => {
        tooltipEl.classList.remove('visible');
        setTimeout(() => {
          if (!tooltipEl.classList.contains('visible')) {
            tooltipEl.style.display = 'none';
          }
        }, 180);

        warmTimer = setTimeout(() => {
          isWarm = false;
        }, 600);
      }, 80);
    }

    document.addEventListener('mouseover', (e) => {
      const el = e.target.closest('[title], [data-tooltip], [data-why], .why, .key-toggle, #themeSeg button');
      if (el) {
        const text = el.getAttribute('data-tooltip') || el.getAttribute('title') || (el.classList.contains('why') ? 'Methodology & data notes' : null);
        if (text) {
          if (el.getAttribute('title')) {
            el.setAttribute('data-original-title', el.getAttribute('title'));
            el.removeAttribute('title'); // Prevent native browser tooltip collision
          }
          showTooltip(el, text);
        }
      }
    });

    document.addEventListener('mouseout', (e) => {
      const el = e.target.closest('[data-tooltip], [data-original-title], [data-why], .why, .key-toggle, #themeSeg button');
      if (el) {
        hideTooltip();
      }
    });
  }

  // 4. Squish Switch Enhancement (ReactBits /c/micro/squish-switch)
  // Upgrades #themeSeg into an elastic pill switch
  function initSquishThemeSwitch() {
    const themeSeg = document.getElementById('themeSeg');
    if (!themeSeg) return;

    themeSeg.classList.add('rb-squish-seg');
    const indicator = document.createElement('div');
    indicator.className = 'rb-squish-pill';
    themeSeg.appendChild(indicator);

    function updateIndicator(animate = true) {
      const activeBtn = themeSeg.querySelector('button[aria-pressed="true"]');
      if (!activeBtn) return;

      const segRect = themeSeg.getBoundingClientRect();
      const btnRect = activeBtn.getBoundingClientRect();

      const left = btnRect.left - segRect.left;
      const width = btnRect.width;

      if (!animate) {
        indicator.style.transition = 'none';
      } else {
        indicator.style.transition = 'transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1), width 0.28s ease';
      }

      indicator.style.transform = `translateX(${left}px)`;
      indicator.style.width = `${width}px`;
    }

    // Update on click with squish stretch
    themeSeg.addEventListener('pointerdown', (e) => {
      indicator.style.transform += ' scaleX(1.15) scaleY(0.92)';
    });

    themeSeg.addEventListener('click', () => {
      setTimeout(() => updateIndicator(true), 30);
    });

    window.addEventListener('resize', () => updateIndicator(false));
    setTimeout(() => updateIndicator(false), 100);
  }

  // 5. Thought Line AI Research Guide (ReactBits /c/micro/thought-line)
  // Provides active live thinking indicator for search queries and matching
  function initThoughtLineIndicator() {
    const masthead = document.querySelector('.masthead');
    if (!masthead) return;

    const thoughtContainer = document.createElement('div');
    thoughtContainer.id = 'rb-thought-line';
    thoughtContainer.className = 'rb-thought-line';
    thoughtContainer.innerHTML = `
      <div class="rb-thought-pill">
        <span class="rb-thought-sparkle">✦</span>
        <span class="rb-thought-label">Atlas live index</span>
        <span class="rb-thought-timer">3,492 PIs</span>
      </div>
    `;

    // Insert after masthead note
    const mastNote = document.getElementById('mastNote');
    if (mastNote) {
      mastNote.parentNode.insertBefore(thoughtContainer, mastNote.nextSibling);
    }

    // Listen for search input in Directory and Graph
    const dQ = document.getElementById('dQ');
    const gSearch = document.getElementById('gSearch');
    const label = thoughtContainer.querySelector('.rb-thought-label');
    const timer = thoughtContainer.querySelector('.rb-thought-timer');
    const sparkle = thoughtContainer.querySelector('.rb-thought-sparkle');

    function pulseSearch(inputEl, queryDesc) {
      inputEl.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        if (val) {
          thoughtContainer.classList.add('working');
          label.textContent = `Analyzing ${queryDesc} "${val.slice(0, 18)}${val.length > 18 ? '…' : ''}"`;
          timer.textContent = 'Filtering…';
          sparkle.classList.add('spinning');
        } else {
          thoughtContainer.classList.remove('working');
          label.textContent = 'Atlas live index';
          timer.textContent = '3,492 PIs';
          sparkle.classList.remove('spinning');
        }
      });
    }

    if (dQ) pulseSearch(dQ, 'directory for');
    if (gSearch) pulseSearch(gSearch, 'network of');
  }

  // 6. Interactive 3D Tilt & Glare on Cards (ReactBits /c/micro/flip-card / folder-float)
  function initCardTilts() {
    document.addEventListener('pointermove', (e) => {
      const card = e.target.closest('.card, .unit-card, .specimen, .dcard, .note');
      if (!card || window.matchMedia('(pointer: coarse)').matches) return;

      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -4.5;
      const rotateY = ((x - centerX) / centerX) * 4.5;

      card.style.setProperty('--rb-glare-x', `${(x / rect.width) * 100}%`);
      card.style.setProperty('--rb-glare-y', `${(y / rect.height) * 100}%`);
      card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-2px)`;
    });

    document.addEventListener('pointerout', (e) => {
      const card = e.target.closest('.card, .unit-card, .specimen, .dcard, .note');
      if (!card) return;
      card.style.transform = '';
    });
  }

  // 7. Micro-Feedback for interactive actions (Button ripples & Spring pops)
  function initMicroButtons() {
    document.addEventListener('pointerdown', (e) => {
      const btn = e.target.closest('button.act, button.mini-act, .rail button, .seg button, .chip, .key-toggle');
      if (!btn) return;

      btn.classList.add('rb-active-spring');
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const ripple = document.createElement('span');
      ripple.className = 'rb-ripple';
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      btn.appendChild(ripple);

      setTimeout(() => {
        if (ripple.parentNode) ripple.parentNode.removeChild(ripple);
      }, 600);
    });

    document.addEventListener('pointerup', (e) => {
      const btn = e.target.closest('.rb-active-spring');
      if (btn) btn.classList.remove('rb-active-spring');
    });

    // Notify user on helpful events
    const copyShareBtn = document.getElementById('openFind');
    if (copyShareBtn) {
      copyShareBtn.addEventListener('click', () => {
        if (window.showReactBitsToast) {
          window.showReactBitsToast({
            title: 'Lab Matchmaker activated',
            description: 'Answer questions step-by-step or skip freely to filter Emory labs.',
            icon: '🧭'
          });
        }
      });
    }

    const resetAllBtn = document.getElementById('gResetAll');
    if (resetAllBtn) {
      resetAllBtn.addEventListener('click', () => {
        if (window.showReactBitsToast) {
          window.showReactBitsToast({
            title: 'All network graph filters reset',
            description: 'Returning to full multi-school department map view.',
            icon: '↺'
          });
        }
      });
    }
  }

  // 8. Custom ReactBits Badge & Tooling Bar
  function initReactBitsDock() {
    const dock = document.createElement('div');
    dock.id = 'rb-micro-dock';
    dock.className = 'rb-micro-dock';
    dock.innerHTML = `
      <div class="rb-dock-content">
        <span class="rb-dock-brand">✨ ReactBits Micro UI</span>
        <span class="rb-dock-divider"></span>
        <button class="rb-dock-btn" id="rbBtnQuickToast" data-tooltip="Trigger fluid swipe toast">Test Toast</button>
        <button class="rb-dock-btn" id="rbBtnToggleMotion" data-tooltip="Switch fluid spring dampening">Spring Dynamics: Active</button>
        <a href="https://reactbits.dev/c/micro" target="_blank" rel="noopener" class="rb-dock-link" data-tooltip="View ReactBits Micro documentation">ReactBits Docs ↗</a>
      </div>
    `;
    document.body.appendChild(dock);

    document.getElementById('rbBtnQuickToast').onclick = () => {
      window.showReactBitsToast({
        title: 'Micro-interaction triggered',
        description: 'ReactBits physics spring toast with swipe-to-dismiss gesture.',
        icon: '⚡',
        actionLabel: 'Undo',
        onAction: () => console.log('Toast action undone')
      });
    };

    let springActive = true;
    document.getElementById('rbBtnToggleMotion').onclick = (e) => {
      springActive = !springActive;
      document.body.classList.toggle('rb-reduced-spring', !springActive);
      e.target.textContent = springActive ? 'Spring Dynamics: Active' : 'Spring Dynamics: Calm';
      window.showReactBitsToast({
        title: springActive ? 'Fluid Spring Physics enabled' : 'Calm Spring mode enabled',
        description: springActive ? 'Spring overshoot and micro bounces are dynamic.' : 'Transitions are muted to standard ease curves.',
        icon: springActive ? '🌊' : '🍃'
      });
    };
  }

  // Boot all micro-interactions once DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }

  function initAll() {
    initMagneticCursor();
    initSwipeToast();
    initWarmTooltips();
    initSquishThemeSwitch();
    initThoughtLineIndicator();
    initCardTilts();
    initMicroButtons();
    initReactBitsDock();

    // Auto-dismiss the initial disclaimer after short preview so user gets directly into the atlas
    setTimeout(() => {
      const discOk = document.getElementById('discOk');
      const disc = document.getElementById('disc');
      if (disc && disc.classList.contains('on') && discOk) discOk.click();
    }, 700);

    // Trigger welcoming toast
    setTimeout(() => {
      if (window.showReactBitsToast) {
        window.showReactBitsToast({
          title: 'Emory Lab Atlas enhanced',
          description: 'Loaded with ReactBits fluid micro-interactions, spring switches, & warm tooltips.',
          icon: '✦',
          duration: 4800
        });
      }
    }, 900);
  }

})();
