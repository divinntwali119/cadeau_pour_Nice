/* Carrousel d'accueil et chargement progressif du fil, réinitialisables en navigation SPA. */
(function() {
  'use strict';

  var cleanups = [];

  function cleanupHomeWidgets() {
    cleanups.forEach(function(cleanup) { cleanup(); });
    cleanups = [];
  }

  function initHomeWidgets() {
    cleanupHomeWidgets();

    var slides = document.querySelector('.hero-slides');
    if (slides) {
      var slideElements = slides.querySelectorAll('.hero-slide');
      var dots = document.querySelectorAll('.carousel-dot');
      var heroCarousel = document.querySelector('.hero-carousel');
      var currentIndex = 0;
      var autoPlayInterval = null;

      function goToSlide(index) {
        if (!slideElements.length) return;
        if (index < 0) index = slideElements.length - 1;
        if (index >= slideElements.length) index = 0;
        currentIndex = index;
        slides.style.transform = 'translateX(-' + (currentIndex * 100) + '%)';
        dots.forEach(function(dot, dotIndex) {
          dot.classList.toggle('active', dotIndex === currentIndex);
        });
      }

      function stopAutoPlay() {
        if (autoPlayInterval) {
          window.clearInterval(autoPlayInterval);
          autoPlayInterval = null;
        }
      }

      function startAutoPlay() {
        stopAutoPlay();
        if (slideElements.length > 1) {
          autoPlayInterval = window.setInterval(function() {
            goToSlide(currentIndex + 1);
          }, 4000);
        }
      }

      var dotHandlers = [];
      dots.forEach(function(dot, index) {
        var handler = function() {
          stopAutoPlay();
          goToSlide(index);
          startAutoPlay();
        };
        dot.addEventListener('click', handler);
        dotHandlers.push([dot, handler]);
      });

      var stopOnHover = function() { stopAutoPlay(); };
      var resumeOnHover = function() { startAutoPlay(); };
      if (heroCarousel) {
        heroCarousel.addEventListener('mouseenter', stopOnHover);
        heroCarousel.addEventListener('mouseleave', resumeOnHover);
      }

      goToSlide(0);
      startAutoPlay();
      cleanups.push(function() {
        stopAutoPlay();
        dotHandlers.forEach(function(pair) { pair[0].removeEventListener('click', pair[1]); });
        if (heroCarousel) {
          heroCarousel.removeEventListener('mouseenter', stopOnHover);
          heroCarousel.removeEventListener('mouseleave', resumeOnHover);
        }
      });
    }

    var feed = document.querySelector('[data-home-feed]');
    if (!feed) return;

    var list = feed.querySelector('[data-feed-items]');
    var status = feed.querySelector('[data-feed-status]');
    var observer = null;
    var loading = false;

    function getCookie(name) {
      var prefix = name + '=';
      var parts = document.cookie ? document.cookie.split(';') : [];
      for (var i = 0; i < parts.length; i += 1) {
        var part = parts[i].trim();
        if (part.indexOf(prefix) === 0) {
          return decodeURIComponent(part.slice(prefix.length));
        }
      }
      return '';
    }

    function getCsrfToken(element) {
      var card = element && element.closest('.home-feed-card');
      var tokenInput = card && card.querySelector('[name="csrfmiddlewaretoken"]');
      return tokenInput ? tokenInput.value : getCookie('csrftoken');
    }

    function observeNextLink() {
      if (observer) observer.disconnect();
      var nextLink = list && list.querySelector('[data-feed-next]');
      if (!nextLink || !('IntersectionObserver' in window)) return;
      observer = new IntersectionObserver(function(entries) {
        if (entries.some(function(entry) { return entry.isIntersecting; })) {
          loadNextPage(nextLink);
        }
      }, { rootMargin: '480px 0px' });
      observer.observe(nextLink);
    }

    async function loadNextPage(nextLink) {
      if (loading || !nextLink || !nextLink.isConnected) return;
      loading = true;
      nextLink.setAttribute('aria-disabled', 'true');
      if (status) status.textContent = 'Chargement des publications…';

      try {
        var response = await fetch(nextLink.href, {
          credentials: 'same-origin',
          headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'text/html' }
        });
        if (!response.ok) throw new Error('Réponse réseau invalide');

        var fragment = document.createElement('template');
        fragment.innerHTML = await response.text();
        var incomingItems = fragment.content.querySelectorAll('[data-feed-item]');
        var incomingLink = fragment.content.querySelector('[data-feed-next]');
        nextLink.remove();
        incomingItems.forEach(function(item) { list.appendChild(item); });
        if (incomingLink) list.appendChild(incomingLink);
        if (status) status.textContent = '';
        window.dispatchEvent(new CustomEvent('smyrne:home-feed-updated'));
        observeNextLink();
      } catch (error) {
        nextLink.removeAttribute('aria-disabled');
        if (status) status.textContent = 'Le chargement a échoué. Touchez « Charger plus d’actualités » pour réessayer.';
        if (observer) observer.disconnect();
      } finally {
        loading = false;
      }
    }

    async function toggleFeedLike(button) {
      if (button.disabled) return;
      var likeUrl = button.getAttribute('data-like-url');
      if (!likeUrl) return;

      button.disabled = true;
      button.setAttribute('aria-busy', 'true');

      try {
        var response = await fetch(likeUrl, {
          method: 'POST',
          credentials: 'same-origin',
          headers: {
            'X-CSRFToken': getCsrfToken(button),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          }
        });

        var payload = await response.json();
        if (response.status === 401 && payload.login_url) {
          window.location.assign(payload.login_url);
          return;
        }
        if (!response.ok) throw new Error(payload.error || 'Le like n’a pas pu être appliqué.');
        var countNode = button.querySelector('[data-like-count]');
        if (countNode && typeof payload.count !== 'undefined') {
          countNode.textContent = payload.count;
        }
        if (payload.action === 'like') {
          button.classList.add('is-liked');
          button.setAttribute('aria-pressed', 'true');
          button.setAttribute('aria-label', 'Retirer le like');
        } else if (payload.action === 'unlike') {
          button.classList.remove('is-liked');
          button.setAttribute('aria-pressed', 'false');
          button.setAttribute('aria-label', 'Aimer cette publication');
        }
      } catch (error) {
        if (status) status.textContent = error.message || 'Le like n’a pas pu être appliqué. Réessayez.';
      } finally {
        button.disabled = false;
        button.removeAttribute('aria-busy');
      }
    }

    async function submitFeedComment(form) {
      var submitButton = form.querySelector('[type="submit"]');
      var panel = form.closest('[data-feed-comment-panel]');
      var feedback = panel && panel.querySelector('[data-feed-comment-feedback]');
      if (submitButton && submitButton.disabled) return;
      if (submitButton) submitButton.disabled = true;
      if (feedback) feedback.textContent = '';

      try {
        var response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          credentials: 'same-origin',
          headers: {
            'X-CSRFToken': getCsrfToken(form),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
          }
        });
        var payload = await response.json();
        if (response.status === 401 && payload.login_url) {
          window.location.assign(payload.login_url);
          return;
        }
        if (!response.ok) throw new Error(payload.error || 'Le commentaire n’a pas pu être envoyé.');

        form.reset();
        if (feedback) feedback.textContent = payload.message;
        var card = form.closest('.home-feed-card');
        var countNode = card && card.querySelector('[data-comment-count]');
        if (countNode && typeof payload.count !== 'undefined') {
          countNode.textContent = payload.count;
        }
      } catch (error) {
        if (feedback) feedback.textContent = error.message || 'Le commentaire n’a pas pu être envoyé. Réessayez.';
      } finally {
        if (submitButton) submitButton.disabled = false;
      }
    }

    function handleFeedClick(event) {
      var target = event.target instanceof Element ? event.target : null;
      var commentToggle = target && target.closest('[data-feed-comment-toggle]');
      if (commentToggle) {
        event.preventDefault();
        var panelId = commentToggle.getAttribute('aria-controls');
        var panel = panelId && document.getElementById(panelId);
        if (panel) {
          var opening = panel.hidden;
          panel.hidden = !opening;
          commentToggle.setAttribute('aria-expanded', String(opening));
          if (opening) {
            var textarea = panel.querySelector('textarea');
            if (textarea) textarea.focus({ preventScroll: true });
          }
        }
        return;
      }
      var likeButton = target && target.closest('[data-feed-like]');
      if (likeButton) {
        event.preventDefault();
        toggleFeedLike(likeButton);
        return;
      }
      var nextLink = target && target.closest('[data-feed-next]');
      if (!nextLink) return;
      event.preventDefault();
      loadNextPage(nextLink);
    }

    function handleFeedSubmit(event) {
      var form = event.target;
      if (!(form instanceof HTMLFormElement) || !form.matches('[data-feed-comment-form]')) return;
      event.preventDefault();
      event.stopPropagation();
      submitFeedComment(form);
    }

    if (list) {
      list.addEventListener('click', handleFeedClick);
      list.addEventListener('submit', handleFeedSubmit);
      observeNextLink();
    }

    cleanups.push(function() {
      if (observer) observer.disconnect();
      if (list) list.removeEventListener('click', handleFeedClick);
      if (list) list.removeEventListener('submit', handleFeedSubmit);
    });
  }

  window.__smyrneHomeWidgetsCleanup = cleanupHomeWidgets;
  window.__smyrneInitHomeWidgets = initHomeWidgets;
  document.addEventListener('DOMContentLoaded', initHomeWidgets);
})();
