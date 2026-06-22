function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

async function ajaxSubmit(form, successCallback) {
    const formData = new FormData(form);

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        });

        const data = await response.json();

        if (data.success) {
            successCallback(data);
            form.reset();
        } else {
            alert(data.error || 'Ошибка при отправке');
        }

    } catch (e) {
        alert('Ошибка соединения');
        console.error(e);
    }
}


/* =========================
   ГЛАВНЫЙ КОММЕНТАРИЙ
========================= */
const mainForm = document.getElementById('main-comment-form');

if (mainForm) {
    mainForm.addEventListener('submit', function(e) {
        e.preventDefault();

        ajaxSubmit(this, function(data) {
            const list = document.getElementById('comments-list');
            const noComments = document.getElementById('no-comments');

            if (noComments) noComments.style.display = 'none';

            const c = data.comment;

            const html = `
                <div class="comment-item" id="comment-${c.id}">
                    <div class="comment-header">
                        <div class="comment-avatar">
                            ${c.avatar ? `<img src="${c.avatar}">` :
                            `<div class="avatar-placeholder"><i class="fas fa-user"></i></div>`}
                        </div>

                        <div class="comment-meta">
                            <span class="comment-author">${c.username}</span>
                            <span class="comment-date">${c.date}</span>
                        </div>
                    </div>

                    <div class="comment-body">
                        <p>${c.text}</p>
                    </div>

                    <div class="comment-actions">
                        <button type="button" class="action-btn reply-btn"
                                onclick="toggleReply(${c.id})">
                            <i class="far fa-reply"></i> Ответить
                        </button>
                    </div>

                    <div class="reply-form" id="reply-form-${c.id}" style="display:none;">
                        <form class="reply-form-ajax" data-id="${c.id}"
                              action="/comment/reply/${c.id}" method="POST">
                            <textarea name="reply" placeholder="Напишите ответ..." required></textarea>
                            <button type="submit" class="submit-comment-btn">
                                <i class="fas fa-paper-plane"></i> Ответить
                            </button>
                        </form>
                    </div>
                </div>
            `;

            list.insertAdjacentHTML('beforeend', html);
        });
    });
}


/* =========================
   ЛАЙКИ
========================= */
document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('like-form')) {
        e.preventDefault();

        const form = e.target;
        const countSpan = form.querySelector('.like-count');
        const icon = form.querySelector('i');

        ajaxSubmit(form, function(data) {
            countSpan.textContent = data.likes;

            if (data.liked) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                icon.style.color = 'red';
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                icon.style.color = '';
            }
        });
    }
});


/* =========================
   ОТВЕТЫ (REPLIES)
========================= */
document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('reply-form-ajax')) {
        e.preventDefault();

        const form = e.target;
        const commentId = form.dataset.id;

        ajaxSubmit(form, function(data) {
            const r = data.reply;
            const parent = document.getElementById(`comment-${commentId}`);
            const replyForm = document.getElementById(`reply-form-${commentId}`);

            replyForm.style.display = 'none';

            const html = `
                <div class="reply-item">
                    <div class="reply-header">
                        <div class="comment-avatar" style="width:40px;height:40px;">
                            ${r.avatar ? `<img src="${r.avatar}">` :
                            `<div class="avatar-placeholder"><i class="fas fa-user"></i></div>`}
                        </div>

                        <div class="comment-meta">
                            <span class="comment-author">${r.username}</span>
                            <span class="comment-date">${r.date}</span>
                        </div>
                    </div>

                    <div class="comment-body" style="margin-top:8px;">
                        ${r.text}
                    </div>
                </div>
            `;

            parent.insertAdjacentHTML('beforeend', html);
        });
    }
});


/* =========================
   ИЗБРАННОЕ — КРАСИВОЕ
========================= */
const favForm = document.getElementById('favourite-form');
const favBtn = document.getElementById('favourite-btn');
const btnText = favBtn ? favBtn.querySelector('.btn-text') : null;
const heartIcon = favBtn ? favBtn.querySelector('i') : null;

if (favForm && favBtn) {
    favForm.addEventListener('submit', function(e) {
        e.preventDefault();

        ajaxSubmit(this, function(data) {
            const isNowAdded = data.message && data.message.includes('Добавлено');

            // Переключаем состояние кнопки
            if (isNowAdded) {
                favBtn.classList.add('added');
                btnText.textContent = 'В избранном';
                heartIcon.classList.add('fas');
                heartIcon.classList.remove('far');

                // Короткое уведомление
                showToast('✅ Добавлено в избранное!', 'success');
            } else {
                favBtn.classList.remove('added');
                btnText.textContent = 'Добавить в избранное';
                heartIcon.classList.remove('fas');
                heartIcon.classList.add('far');

                showToast('❤️‍🔥 Удалено из избранного', 'remove');
            }
        });
    });
}

/* Красивое всплывающее уведомление */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#e50914' : '#1a1a24'};
        color: white;
        padding: 14px 24px;
        border-radius: 12px;
        font-weight: 500;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: addedToast 2.5s forwards;
    `;
    toast.innerHTML = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 2500);
}


/* =========================
   TOGGLE REPLY FORM
========================= */
function toggleReply(id) {
    const form = document.getElementById(`reply-form-${id}`);

    document.querySelectorAll('.reply-form').forEach(el => {
        if (el !== form) el.style.display = 'none';
    });

    form.style.display =
        (form.style.display === 'none' || form.style.display === '')
        ? 'block'
        : 'none';
}

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