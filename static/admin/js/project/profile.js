// ==================== ИЗМЕНЕНИЕ АВАТАРКИ ====================
const avatarInput = document.getElementById('avatarInput');

if (avatarInput) {
    avatarInput.addEventListener('change', async function () {
        const file = this.files[0];
        if (!file) return;

        // Проверка типа файла
        if (!file.type.startsWith('image/')) {
            alert('Пожалуйста, выберите изображение (jpg, png, webp и т.д.)');
            this.value = '';
            return;
        }

        // Проверка размера (максимум 5 МБ)
        if (file.size > 5 * 1024 * 1024) {
            alert('Файл слишком большой! Максимум 5 МБ.');
            this.value = '';
            return;
        }

        const formData = new FormData();
        formData.append('avatar', file);

        try {
            const res = await fetch('/change_avatar/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });

            const data = await res.json();

            if (data.success) {
                // Обновляем аватарку на странице
                let avatarImg = document.querySelector('.avatar');

                if (avatarImg) {
                    // Добавляем timestamp, чтобы браузер не брал из кэша
                    avatarImg.src = data.avatar_url + '?t=' + new Date().getTime();
                } else {
                    // Если был плейсхолдер — обновляем всю страницу
                    location.reload();
                }

                alert('✅ Аватарка успешно обновлена!');
            } else {
                alert(data.error || 'Ошибка при загрузке аватарки');
            }
        } catch (err) {
            console.error(err);
            alert('Ошибка соединения с сервером');
        }

        // Очищаем поле, чтобы можно было загрузить тот же файл заново
        this.value = '';
    });
}

// ==================== РЕДАКТИРОВАНИЕ ИМЕНИ ====================
const usernameText = document.getElementById("usernameText");
const editBox = document.getElementById("usernameEdit");
const input = document.getElementById("usernameInput");
const btn = document.getElementById("saveUsernameBtn");

// открыть редактирование
if (usernameText) {
    usernameText.addEventListener("click", () => {
        editBox.classList.remove("hidden");
        input.focus();
        input.select();
    });
}

// сохранить
if (btn) {
    btn.addEventListener("click", async () => {
        const newName = input.value.trim();

        if (!newName) {
            alert("Имя пользователя не может быть пустым");
            return;
        }

        try {
            const res = await fetch("/change_username/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ username: newName })
            });

            const data = await res.json();

            if (data.success) {
                usernameText.textContent = newName;
                editBox.classList.add("hidden");
                alert("✅ Имя пользователя обновлено");
            } else {
                alert(data.error || "Не удалось изменить имя");
            }
        } catch (err) {
            console.error(err);
            alert("Ошибка соединения");
        }
    });
}

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ==================== ПОИСК ====================
const searchInput = document.getElementById('searchInput');
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

if (searchInput) {
    searchInput.addEventListener('focus', function () {
        if (this.value.trim() === '') {
            showPlaceholder();
        }
    });

    searchInput.addEventListener('input', function () {
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
                .catch(err => {
                    console.error(err);
                    resultsContainer.innerHTML = `
                        <div class="search-placeholder">
                            <p style="color:#f66;">Ошибка при поиске</p>
                        </div>
                    `;
                });
        }, 300);
    });
}

// Закрытие поиска
document.addEventListener('click', function(e) {
    if (!e.target.closest('.header-search-wrapper')) {
        resultsContainer.classList.remove('show');
        toggleOverlay(false);
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === "Escape") {
        resultsContainer.classList.remove('show');
        toggleOverlay(false);
        if (searchInput) searchInput.blur();
    }
});

// ==================== УДАЛЕНИЕ ИЗ ИЗБРАННОГО ====================
document.addEventListener('click', async function(e) {
    const btn = e.target.closest('.remove-favourite-btn');
    if (!btn) return;

    const filmId = btn.dataset.filmId;
    const card = btn.closest('.film-card');

    if (!filmId) return;

    try {
        const res = await fetch(`/favourite/${filmId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ action: 'remove' })
        });

        const data = await res.json();

        if (data.success) {
            card.classList.add('removing');

            setTimeout(() => {
                card.remove();

                // Обновляем счётчики
                document.querySelectorAll('.info-value').forEach(el => {
                    const title = el.parentElement.querySelector('.info-title');
                    if (title && (title.textContent.includes('Избранное') ||
                                 title.textContent.includes('Любимых'))) {
                        let count = parseInt(el.textContent) || 0;
                        el.textContent = Math.max(0, count - 1);
                    }
                });

                // Если фильмов больше нет
                if (document.querySelectorAll('.film-card').length === 0) {
                    const emptyMsg = document.getElementById('emptyMessage');
                    if (emptyMsg) emptyMsg.style.display = 'block';
                }
            }, 400);
        } else {
            alert(data.message || data.error || 'Не удалось удалить');
        }
    } catch (err) {
        console.error(err);
        alert('Ошибка соединения с сервером');
    }
});