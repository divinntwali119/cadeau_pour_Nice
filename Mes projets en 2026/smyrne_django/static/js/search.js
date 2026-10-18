// ========================================
// SCRIPT PRINCIPAL - TOUTES LES FONCTIONNALITÉS
// ========================================

document.addEventListener('DOMContentLoaded', function() {

  // ========================================
  // 1. RECHERCHE GLOBALE INSTANTANÉE (CTRL+K / LIVE COMMAND PALETTE)
  // ========================================
  const searchModal = document.getElementById('searchModalBackdrop');
  const searchInput = document.getElementById('searchModalInput');
  const searchResultsList = document.getElementById('searchLiveResultsList');
  const searchSuggestions = document.getElementById('searchSuggestionsSection');
  const searchSpinner = document.getElementById('searchSpinner');
  const searchClearBtn = document.getElementById('searchModalClear');
  const searchCloseBtn = document.getElementById('searchModalClose');
  const searchCatBar = document.getElementById('searchCatBar');
  const searchToggles = document.querySelectorAll('#searchToggle, [data-open-search]');

  let searchDebounceTimer = null;
  let currentResults = [];
  let activeFilter = 'all';
  let selectedIndex = -1;
  let lastSearchTrigger = null;

  searchToggles.forEach(btn => {
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', 'searchModalBackdrop');
  });

  function openSearchModal(trigger) {
    if (!searchModal) return;
    lastSearchTrigger = trigger || document.activeElement;
    searchModal.inert = false;
    searchModal.classList.add('active');
    searchModal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
    searchToggles.forEach(btn => btn.setAttribute('aria-expanded', 'true'));
    setTimeout(() => {
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }, 100);
  }

  function closeSearchModal() {
    if (!searchModal) return;
    searchModal.classList.remove('active');
    searchModal.setAttribute('aria-hidden', 'true');
    searchModal.inert = true;
    document.body.classList.remove('modal-open');
    searchToggles.forEach(btn => btn.setAttribute('aria-expanded', 'false'));
    if (lastSearchTrigger && lastSearchTrigger.isConnected) {
      lastSearchTrigger.focus({ preventScroll: true });
    }
    lastSearchTrigger = null;
  }

  // Ouverture via boutons
  searchToggles.forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      openSearchModal(btn);
    });
  });
  if (searchCloseBtn) searchCloseBtn.addEventListener('click', closeSearchModal);

  // Raccourci clavier, fermeture et maintien du focus dans la recherche.
  document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault();
      if (searchModal && searchModal.classList.contains('active')) {
        closeSearchModal();
      } else {
        openSearchModal(document.activeElement);
      }
    } else if (e.key === 'Escape' && searchModal && searchModal.classList.contains('active')) {
      e.preventDefault();
      closeSearchModal();
    } else if (e.key === 'Tab' && searchModal && searchModal.classList.contains('active')) {
      const focusable = Array.from(searchModal.querySelectorAll(
        'button:not([disabled]), input:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
      )).filter(element => element.getClientRects().length);
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && (document.activeElement === first || !searchModal.contains(document.activeElement))) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && (document.activeElement === last || !searchModal.contains(document.activeElement))) {
        e.preventDefault();
        first.focus();
      }
    }
  });

  // Fermeture au clic sur le backdrop
  if (searchModal) {
    searchModal.addEventListener('click', function(e) {
      if (e.target === searchModal) {
        closeSearchModal();
      } else if (e.target instanceof Element && e.target.closest('a[href]')) {
        closeSearchModal();
      }
    });
  }

  // Bouton effacer le champ
  if (searchClearBtn && searchInput) {
    searchClearBtn.addEventListener('click', function() {
      searchInput.value = '';
      searchInput.focus();
      searchClearBtn.style.display = 'none';
      renderResults([]);
      if (searchSuggestions) searchSuggestions.style.display = 'block';
    });
  }

  // Filtrage par catégories
  if (searchCatBar) {
    searchCatBar.querySelectorAll('.search-cat-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        searchCatBar.querySelectorAll('.search-cat-btn').forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-pressed', 'false');
        });
        this.classList.add('active');
        this.setAttribute('aria-pressed', 'true');
        activeFilter = this.getAttribute('data-filter') || 'all';
        renderResults(currentResults);
      });
    });
  }

  // Clic sur les chips de suggestion
  document.querySelectorAll('[data-search-term]').forEach(chip => {
    chip.addEventListener('click', function() {
      const term = this.getAttribute('data-search-term');
      if (searchInput) {
        searchInput.value = term;
        executeLiveSearch(term);
      }
    });
  });

  // Exécution de la recherche AJAX
  function executeLiveSearch(query) {
    query = (query || '').trim();
    if (searchClearBtn) {
      searchClearBtn.style.display = query.length > 0 ? 'inline-block' : 'none';
    }

    if (query.length < 2) {
      if (searchSpinner) searchSpinner.style.display = 'none';
      if (searchResultsList) searchResultsList.innerHTML = '';
      if (searchSuggestions) searchSuggestions.style.display = 'block';
      currentResults = [];
      return;
    }

    if (searchSpinner) searchSpinner.style.display = 'flex';
    if (searchSuggestions) searchSuggestions.style.display = 'none';

    fetch('/recherche-globale/?q=' + encodeURIComponent(query))
      .then(res => res.json())
      .then(data => {
        if (searchSpinner) searchSpinner.style.display = 'none';
        currentResults = data.results || [];
        renderResults(currentResults);
      })
      .catch(err => {
        console.error('[Search] Erreur recherche en direct:', err);
        if (searchSpinner) searchSpinner.style.display = 'none';
      });
  }

  function renderResults(results) {
    if (!searchResultsList) return;
    selectedIndex = -1;

    let filtered = results;
    if (activeFilter !== 'all') {
      filtered = results.filter(r => r.category === activeFilter);
    }

    if (filtered.length === 0 && searchInput && searchInput.value.trim().length >= 2) {
      searchResultsList.innerHTML = `
        <div style="padding: 30px 20px; text-align: center; color: var(--modal-muted);">
          <i class="fa-solid fa-face-meh" style="font-size: 32px; margin-bottom: 12px; color: var(--modal-muted);"></i>
          <div style="font-weight: 700; font-size: 15px; margin-bottom: 6px; color: var(--modal-text);">Aucun résultat pour « ${searchInput.value.trim()} »</div>
          <p style="font-size: 13px; margin: 0;">Essayez un autre mot-clé (ex: <em>culte</em>, <em>foi</em>, <em>amour</em>, <em>pasteur</em>...)</p>
        </div>
      `;
      return;
    }

    let html = '';
    filtered.forEach((item, idx) => {
      const icon = item.icon || 'fa-solid fa-file-lines';
      html += `
        <a href="${item.url}" class="search-live-item" data-index="${idx}">
          <div class="search-item-icon-box"><i class="${icon}"></i></div>
          <div class="search-item-info">
            <div class="search-item-title-row">
              <span class="search-item-title">${item.title}</span>
              <span class="search-item-badge">${item.badge || item.category}</span>
            </div>
            <div class="search-item-subtitle">${item.subtitle || ''}</div>
          </div>
        </a>
      `;
    });

    searchResultsList.innerHTML = html;
  }

  // Écoute de l'input avec debounce
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        executeLiveSearch(searchInput.value);
      }, 250);
    });

    // Navigation clavier dans les résultats
    searchInput.addEventListener('keydown', function(e) {
      const items = searchResultsList ? searchResultsList.querySelectorAll('.search-live-item') : [];
      if (items.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIndex = (selectedIndex + 1) % items.length;
        updateSelectedResult(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIndex = (selectedIndex - 1 + items.length) % items.length;
        updateSelectedResult(items);
      } else if (e.key === 'Enter') {
        if (selectedIndex >= 0 && items[selectedIndex]) {
          e.preventDefault();
          items[selectedIndex].click();
        }
      }
    });
  }

  function updateSelectedResult(items) {
    items.forEach((item, idx) => {
      if (idx === selectedIndex) {
        item.classList.add('is-selected');
        item.scrollIntoView({ block: 'nearest' });
      } else {
        item.classList.remove('is-selected');
      }
    });
  }

  // ========================================
  // 2. MENU HAMBURGER
  // ========================================
  // Le menu mobile est contrôlé dans templates/base.html pour éviter les doublons
  // et garantir un comportement identique sur toutes les pages.
  if (!window.__smyrneLegacyMenuHandled) {
    window.__smyrneLegacyMenuHandled = true;
  }

  // ========================================
  // 3. MODE SOMBRE / CLAIR
  // ========================================
  var themeToggleBtn = document.getElementById('themeToggleBtn');
  var themeIcon = document.getElementById('themeIcon');
  var themeText = document.getElementById('themeText');

  if (themeToggleBtn) {
    var savedTheme = localStorage.getItem('theme');
    var currentTheme = (savedTheme === 'dark' || savedTheme === 'light') ? savedTheme : 'light';
    
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeUI(currentTheme);

    themeToggleBtn.addEventListener('click', function() {
      var theme = document.documentElement.getAttribute('data-theme');
      var newTheme = theme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeUI(newTheme);
    });

    function updateThemeUI(theme) {
      if (theme === 'dark') {
        if (themeIcon) themeIcon.className = 'fa-solid fa-sun';
        if (themeText) themeText.textContent = 'Mode Clair';
      } else {
        if (themeIcon) themeIcon.className = 'fa-solid fa-moon';
        if (themeText) themeText.textContent = 'Mode Sombre';
      }
    }
  }

  // ========================================
  // 4. ANIMATIONS FADE-IN
  // ========================================
  var observerOptions = { threshold: 0.15 };
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('appear');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.fade-in').forEach(function(el) {
    observer.observe(el);
  });

  // ========================================
  // 5. GALERIE BADGES
  // ========================================
  document.querySelectorAll('.gallery-item').forEach(function(item) {
    item.addEventListener('click', function() {
      document.querySelectorAll('.gallery-item').forEach(function(el) {
        el.classList.remove('active-badge');
      });
      this.classList.add('active-badge');
      var self = this;
      setTimeout(function() {
        self.classList.remove('active-badge');
      }, 3000);
    });
  });

  document.addEventListener('click', function(e) {
    if (!e.target.closest('.gallery-item')) {
      document.querySelectorAll('.gallery-item').forEach(function(el) {
        el.classList.remove('active-badge');
      });
    }
  });

  // ========================================
  // 6. AVATARS
  // ========================================
  try {
    document.querySelectorAll('img.user-avatar').forEach(function(img) {
      if (img.getAttribute('data-original-src') == null) {
        img.setAttribute('data-original-src', img.src || '');
      }
      img.src = 'images/photo.jpg';
    });
  } catch (e) { /* fail silently */ }

  // ========================================
  // 7. SCROLL BUTTON (pour la page d'accueil)
  // ========================================
  var scrollBtn = document.getElementById('scrollBtn');
  if (scrollBtn) {
    scrollBtn.addEventListener('click', function() {
      var target = document.getElementById('vie-eglise');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }

  // ========================================
  // 9. SCROLL-SPY NAV ACTIVE
  // ========================================
  var sections = document.querySelectorAll('section[id]');
  var navLinks = document.querySelectorAll('.nav-links a');

  if (sections.length > 0 && navLinks.length > 0) {
    window.addEventListener('scroll', function() {
      var current = '';
      var scrollPosition = window.scrollY + 150;

      sections.forEach(function(section) {
        if (scrollPosition >= section.offsetTop) {
          current = section.getAttribute('id');
        }
      });

      navLinks.forEach(function(link) {
        link.classList.remove('active');
        var href = link.getAttribute('href');
        if (href === '#' + current) {
          link.classList.add('active');
        }
      });
    });
  }

  // ========================================
  // 10. MODALE D'IMAGE (pour nos-ministeres)
  // ========================================
  var modal = document.getElementById('imageModal');
  var modalImage = document.getElementById('modalImage');
  var modalName = document.getElementById('modalName');
  var modalRole = document.getElementById('modalRole');
  var isModalOpen = false;

  if (modal) {
    window.openModal = function(src, name, role) {
      if (!src || src === '') {
        console.warn('Source de l\'image invalide');
        return;
      }

      var img = new Image();
      img.onload = function() {
        modalImage.src = src;
        modalName.textContent = name || 'Photo';
        modalRole.textContent = role || '';
        modal.classList.add('active');
        document.body.classList.add('modal-open');
        isModalOpen = true;
      };
      img.onerror = function() {
        modalImage.src = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=200';
        modalName.textContent = name || 'Photo';
        modalRole.textContent = role || '';
        modal.classList.add('active');
        document.body.classList.add('modal-open');
        isModalOpen = true;
      };
      img.src = src;
    };

    window.closeModal = function() {
      modal.classList.remove('active');
      document.body.classList.remove('modal-open');
      isModalOpen = false;
      setTimeout(function() {
        if (!isModalOpen) {
          modalImage.src = '';
        }
      }, 300);
    };

    window.closeModalOutside = function(e) {
      if (e.target === modal) {
        window.closeModal();
      }
    };

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && isModalOpen) {
        window.closeModal();
      }
    });

    var modalContent = modal.querySelector('.modal-content');
    if (modalContent) {
      modalContent.addEventListener('click', function(e) {
        e.stopPropagation();
      });
    }

    var modalClose = modal.querySelector('.modal-close');
    if (modalClose) {
      modalClose.addEventListener('click', function(e) {
        e.stopPropagation();
        window.closeModal();
      });
    }
  }

  // ========================================
  // 11. GESTION DES IMAGES EN ERREUR
  // ========================================
  document.querySelectorAll('img').forEach(function(img) {
    img.addEventListener('error', function() {
      if (!this.dataset.fallback) {
        this.dataset.fallback = 'true';
        this.src = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=200';
      }
    });
  });

});


  document.addEventListener('DOMContentLoaded', function() {
    // Le menu mobile est géré une seule fois dans templates/base.html.
    // On laisse ce bloc inactif pour éviter les conflits de clic et d'état.
  });