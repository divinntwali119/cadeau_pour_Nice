/**
 * LECTEUR AUDIO FLOTTANT PERSISTANT — Église Smyrne
 * Écoute continue et fluide des prédications avec mémorisation de l'état.
 */

(function() {
  'use strict';

  // Élément audio unique
  let audio = new Audio();
  window.__smyrneAudio = audio;

  const STORAGE_KEY = 'smyrne_audio_state';
  const speeds = [1, 1.25, 1.5, 2];
  let currentSpeedIdx = 0;
  let isDraggingProgress = false;

  // Récupérer l'état sauvegardé
  function getSavedState() {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  }

  function saveState(state) {
    try {
      const current = getSavedState() || {};
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...current, ...state }));
    } catch (e) {}
  }

  // Formatage secondes -> mm:ss ou hh:mm:ss
  function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '00:00';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    if (hrs > 0) {
      return `${hrs}:${mins < 10 ? '0' : ''}${mins}:${secs < 10 ? '0' : ''}${secs}`;
    }
    return `${mins < 10 ? '0' : ''}${mins}:${secs < 10 ? '0' : ''}${secs}`;
  }

  // Toast de notification global
  window.showSmyrneToast = function(message, iconClass = 'fa-solid fa-circle-check') {
    let toast = document.getElementById('smyrneGlobalToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'smyrneGlobalToast';
      toast.className = 'smyrne-toast';
      document.body.appendChild(toast);
    }
    toast.innerHTML = `<i class="${iconClass}"></i><span>${message}</span>`;
    toast.classList.add('show');
    clearTimeout(toast.__timer);
    toast.__timer = setTimeout(() => {
      toast.classList.remove('show');
    }, 3200);
  };

  // Initialisation à l'événement DOMContentLoaded
  document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('smyrneAudioPlayer');
    if (!container) return;

    const card = container.querySelector('.smyrne-audio-player-card');
    const playBtn = document.getElementById('playerPlayBtn');
    const playIcon = playBtn ? playBtn.querySelector('i') : null;
    const pillPlayBtn = document.getElementById('pillPlayBtn');
    const prevBtn = document.getElementById('playerSkipBackBtn');
    const nextBtn = document.getElementById('playerSkipFwdBtn');
    const closeBtn = document.getElementById('playerCloseBtn');
    const minimizeBtn = document.getElementById('playerMinimizeBtn');
    const pillView = document.getElementById('playerPillView');
    const speedBtn = document.getElementById('playerSpeedBtn');
    const volumeSlider = document.getElementById('playerVolumeSlider');
    const volumeBtn = document.getElementById('playerVolumeBtn');
    const progressWrap = document.getElementById('playerProgressBarWrap');
    const progressFill = document.getElementById('playerProgressFill');
    const progressThumb = document.getElementById('playerProgressThumb');
    const currentTimeEl = document.getElementById('playerCurrentTime');
    const totalTimeEl = document.getElementById('playerTotalTime');

    // UI Éléments d'infos
    const titleEl = document.getElementById('playerTrackTitle');
    const preacherEl = document.getElementById('playerTrackPreacher');
    const coverEl = document.getElementById('playerTrackCover');
    const pillTitleEl = document.getElementById('pillTrackTitle');
    const pillCoverEl = document.getElementById('pillTrackCover');

    // Fonction de chargement et lecture
    window.playSermonAudio = function({ url, title, preacher, cover, autoPlay = true, resumeTime = 0 }) {
      if (!url) {
        window.showSmyrneToast("L'audio de cette prédication n'est pas encore disponible.", 'fa-solid fa-triangle-exclamation');
        return;
      }

      const isSameTrack = audio.src.endsWith(url) || audio.src === url;

      if (!isSameTrack) {
        audio.src = url;
        audio.load();
      }

      if (titleEl) titleEl.textContent = title || 'Prédication';
      if (preacherEl) preacherEl.textContent = preacher || '5e CELPA Smyrne';
      if (coverEl && cover) coverEl.src = cover;
      if (pillTitleEl) pillTitleEl.textContent = title || 'Prédication';
      if (pillCoverEl && cover) pillCoverEl.src = cover;

      container.classList.add('active');
      container.classList.remove('minimized');

      saveState({
        url,
        title,
        preacher,
        cover,
        isActive: true,
        isMinimized: false
      });

      if (resumeTime > 0 && isFinite(resumeTime)) {
        audio.currentTime = resumeTime;
      }

      if (autoPlay) {
        audio.play().then(() => {
          updatePlayUI(true);
          window.showSmyrneToast(`Lecture : « ${title || 'Prédication'} »`, 'fa-solid fa-headphones');
        }).catch(err => {
          console.log('[Audio] Lecture en attente d’interaction utilisateur:', err);
          updatePlayUI(false);
        });
      }
    };

    function updatePlayUI(isPlaying) {
      if (card) {
        if (isPlaying) {
          card.classList.add('is-playing');
        } else {
          card.classList.remove('is-playing');
        }
      }
      if (playIcon) {
        playIcon.className = isPlaying ? 'fa-solid fa-pause' : 'fa-solid fa-play';
      }
      if (pillPlayBtn) {
        const icon = pillPlayBtn.querySelector('i');
        if (icon) icon.className = isPlaying ? 'fa-solid fa-pause' : 'fa-solid fa-play';
      }
    }

    // Toggle Play / Pause
    function togglePlay() {
      if (!audio.src) return;
      if (audio.paused) {
        audio.play().then(() => updatePlayUI(true)).catch(() => {});
      } else {
        audio.pause();
        updatePlayUI(false);
      }
    }

    if (playBtn) playBtn.addEventListener('click', togglePlay);
    if (pillPlayBtn) pillPlayBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      togglePlay();
    });

    // Clic sur la pilule pour agrandir
    if (pillView) {
      pillView.addEventListener('click', function() {
        container.classList.remove('minimized');
        saveState({ isMinimized: false });
      });
    }

    // Minimiser
    if (minimizeBtn) {
      minimizeBtn.addEventListener('click', function() {
        container.classList.toggle('minimized');
        saveState({ isMinimized: container.classList.contains('minimized') });
      });
    }

    // Fermer
    if (closeBtn) {
      closeBtn.addEventListener('click', function() {
        audio.pause();
        updatePlayUI(false);
        container.classList.remove('active');
        saveState({ isActive: false });
      });
    }

    // Saut -15s et +15s
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        audio.currentTime = Math.max(0, audio.currentTime - 15);
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 15);
      });
    }

    // Vitesse de lecture
    if (speedBtn) {
      speedBtn.addEventListener('click', () => {
        currentSpeedIdx = (currentSpeedIdx + 1) % speeds.length;
        const spd = speeds[currentSpeedIdx];
        audio.playbackRate = spd;
        speedBtn.textContent = `${spd}x`;
        saveState({ speed: spd });
      });
    }

    // Volume
    if (volumeSlider) {
      volumeSlider.addEventListener('input', () => {
        audio.volume = parseFloat(volumeSlider.value);
        audio.muted = (audio.volume === 0);
        updateVolumeIcon();
        saveState({ volume: audio.volume, muted: audio.muted });
      });
    }

    if (volumeBtn) {
      volumeBtn.addEventListener('click', () => {
        audio.muted = !audio.muted;
        if (volumeSlider) {
          volumeSlider.value = audio.muted ? 0 : audio.volume;
        }
        updateVolumeIcon();
        saveState({ muted: audio.muted });
      });
    }

    function updateVolumeIcon() {
      if (!volumeBtn) return;
      const icon = volumeBtn.querySelector('i');
      if (!icon) return;
      if (audio.muted || audio.volume === 0) {
        icon.className = 'fa-solid fa-volume-xmark';
      } else if (audio.volume < 0.5) {
        icon.className = 'fa-solid fa-volume-low';
      } else {
        icon.className = 'fa-solid fa-volume-high';
      }
    }

    // Progression & Seeking
    function updateProgressUI() {
      if (!isFinite(audio.duration) || audio.duration === 0) return;
      const pct = (audio.currentTime / audio.duration) * 100;
      if (progressFill) progressFill.style.width = `${pct}%`;
      if (progressThumb) progressThumb.style.left = `${pct}%`;
      if (currentTimeEl) currentTimeEl.textContent = formatTime(audio.currentTime);
      if (totalTimeEl) totalTimeEl.textContent = formatTime(audio.duration);
    }

    audio.addEventListener('timeupdate', function() {
      if (!isDraggingProgress) {
        updateProgressUI();
      }
      // Sauvegarder la position toutes les 3 secondes
      if (Math.floor(audio.currentTime) % 3 === 0) {
        saveState({ currentTime: audio.currentTime });
      }
    });

    audio.addEventListener('loadedmetadata', function() {
      if (totalTimeEl) totalTimeEl.textContent = formatTime(audio.duration);
      updateProgressUI();
    });

    audio.addEventListener('ended', function() {
      updatePlayUI(false);
      saveState({ currentTime: 0 });
    });

    // Clic sur la barre de progression
    if (progressWrap) {
      function seek(e) {
        const rect = progressWrap.getBoundingClientRect();
        const clickX = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
        const pct = clickX / rect.width;
        if (isFinite(audio.duration) && audio.duration > 0) {
          audio.currentTime = pct * audio.duration;
          updateProgressUI();
        }
      }

      progressWrap.addEventListener('click', seek);
    }

    // Gestion des boutons déclencheurs sur toute la page
    function bindPlayButtons() {
      document.querySelectorAll('[data-play-audio]').forEach(btn => {
        if (btn.__boundAudio) return;
        btn.__boundAudio = true;
        btn.addEventListener('click', function(e) {
          e.preventDefault();
          const url = this.getAttribute('data-play-audio');
          const title = this.getAttribute('data-title') || 'Prédication';
          const preacher = this.getAttribute('data-preacher') || '5e CELPA Smyrne';
          const cover = this.getAttribute('data-cover') || '';
          window.playSermonAudio({ url, title, preacher, cover, autoPlay: true });
        });
      });
    }

    bindPlayButtons();
    // Re-bind si le contenu dynamique change
    const observer = new MutationObserver(bindPlayButtons);
    observer.observe(document.body, { childList: true, subtree: true });

    // Restaurer l'état précédent si disponible
    const saved = getSavedState();
    if (saved && saved.url && saved.isActive) {
      if (saved.speed) {
        audio.playbackRate = saved.speed;
        if (speedBtn) speedBtn.textContent = `${saved.speed}x`;
      }
      if (saved.volume !== undefined) {
        audio.volume = saved.volume;
        if (volumeSlider) volumeSlider.value = saved.volume;
      }
      if (saved.muted) {
        audio.muted = true;
      }
      updateVolumeIcon();

      window.playSermonAudio({
        url: saved.url,
        title: saved.title,
        preacher: saved.preacher,
        cover: saved.cover,
        autoPlay: false,
        resumeTime: saved.currentTime || 0
      });

      if (saved.isMinimized) {
        container.classList.add('minimized');
      }
    }
  });
})();
