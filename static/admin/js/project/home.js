        const input = document.getElementById('searchInput');
        const resultsContainer = document.getElementById('searchResults');
        const overlay = document.getElementById('searchOverlay');

        let timeout = null;

        function toggleOverlay(show) {
            if (show) {
                overlay.classList.add('active');
            } else {
                overlay.classList.remove('active');
            }
        }

        function showPlaceholder() {
            resultsContainer.innerHTML = `
                <div class="search-placeholder">
                    <i class="fas fa-film"></i>
                    <p>Напишите название фильма или сериала</p>
                    <small>Результаты будут появляться здесь</small>
                </div>
            `;
            resultsContainer.classList.add('show');
            toggleOverlay(true);
        }

        input.addEventListener('focus', function () {
            if (this.value.trim() === '') {
                showPlaceholder();
            }
        });

        input.addEventListener('input', function () {
            clearTimeout(timeout);
            const query = this.value.trim();

            if (query.length === 0) {
                showPlaceholder();
                return;
            }

            timeout = setTimeout(() => {
                fetch(`/search/?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        resultsContainer.innerHTML = `<div class="search-film-grid"></div>`;
                        const grid = resultsContainer.querySelector('.search-film-grid');

                        if (data.length === 0) {
                            grid.innerHTML = `
                                <div style="grid-column: 1 / -1; text-align:center; padding: 3rem 1rem; color:var(--text-secondary);">
                                    <i class="fas fa-search" style="font-size:2.5rem; opacity:0.3; margin-bottom:1rem;"></i>
                                    <p>Ничего не найдено по запросу «${query}»</p>
                                </div>
                            `;
                        } else {
                            data.forEach(film => {
                                const year = film.film_date ? new Date(film.film_date).getFullYear() : '';
                                const html = `
                                    <a href="/film/${film.film_slug}" class="search-film-item">
                                        <div class="search-film-poster-wrapper">
                                            <img src="${film.film_poster || '/static/default_poster.jpg'}"
                                                 alt="${film.film_name}">
                                            <div class="search-film-name-overlay">
                                                ${film.film_name}
                                            </div>
                                        </div>

                                        <div class="search-film-content">
                                            <h2 class="film-name">${film.film_name}</h2>
                                            <p class="search-description-preview">
                                                ${film.film_description ? film.film_description.substring(0, 180) + '...' : 'Описание отсутствует'}
                                            </p>
                                            <div class="search-film-meta">
                                                <span>${film.film_category || ''}</span>
                                                <span class="rating">★ ${film.film_rating || '—'}</span>
                                                ${year ? `<span>${year}</span>` : ''}
                                            </div>
                                        </div>
                                    </a>
                                `;
                                grid.innerHTML += html;
                            });
                        }
                        resultsContainer.classList.add('show');
                        toggleOverlay(true);
                    })
                    .catch(() => {
                        resultsContainer.innerHTML = `
                            <div class="search-placeholder">
                                <p style="color:#f66;">Ошибка при поиске</p>
                            </div>
                        `;
                    });
            }, 300);
        });

        // Закрытие поиска и оверлея
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.header-search-wrapper')) {
                resultsContainer.classList.remove('show');
                toggleOverlay(false);
            }
        });

        // Закрытие по Esc
        document.addEventListener('keydown', function(e) {
            if (e.key === "Escape") {
                resultsContainer.classList.remove('show');
                toggleOverlay(false);
                input.blur();
            }
        });