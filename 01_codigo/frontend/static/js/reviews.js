/**
 * RentaMaq - Sistema de Reviews
 * Carga, muestra y permite enviar valoraciones de maquinaria y operarios
 */

/**
 * Devuelve HTML con estrellas visuales (filled / empty) para un rating dado.
 * @param {number} rating - 0 a 5
 * @param {boolean} interactive - si true, genera inputs clicables
 * @param {string} inputName - nombre del grupo de radio inputs
 */
function buildStars(rating, interactive = false, inputName = 'review_rating') {
    if (!interactive) {
        let html = '<span class="stars-display">';
        for (let i = 1; i <= 5; i++) {
            html += `<span class="star ${i <= Math.round(rating) ? 'star-filled' : 'star-empty'}">&#9733;</span>`;
        }
        html += '</span>';
        return html;
    }
    // Estrellas interactivas via radio buttons ocultos
    let html = '<span class="stars-input" id="starsInput_' + inputName + '">';
    for (let i = 5; i >= 1; i--) {
        html += `<input type="radio" id="star${i}_${inputName}" name="${inputName}" value="${i}">`;
        html += `<label for="star${i}_${inputName}" title="${i} estrella${i > 1 ? 's' : ''}">&#9733;</label>`;
    }
    html += '</span>';
    return html;
}

/**
 * Carga y renderiza reviews de un target dentro de un contenedor.
 * @param {string} targetType - 'machinery' | 'operator'
 * @param {number} targetId
 * @param {string} containerId - id del elemento DOM donde renderizar
 */
async function loadReviews(targetType, targetId, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<p class="reviews-loading">Cargando valoraciones...</p>';

    try {
        const [reviewsData, summaryData] = await Promise.all([
            apiRequest(`/reviews?target_type=${targetType}&target_id=${targetId}`),
            apiRequest(`/reviews/summary?target_type=${targetType}&target_id=${targetId}`)
        ]);

        const reviews = Array.isArray(reviewsData) ? reviewsData : [];
        const summary = summaryData || { avg_rating: 0, total: 0 };

        let html = '<div class="reviews-section">';

        // Cabecera con resumen
        html += `<div class="reviews-header">
            <h4 class="reviews-title">Valoraciones</h4>
            <div class="reviews-summary">
                ${buildStars(summary.avg_rating)}
                <span class="reviews-avg">${summary.total > 0 ? summary.avg_rating.toFixed(1) : '—'}</span>
                <span class="reviews-count">(${summary.total} ${summary.total === 1 ? 'valoración' : 'valoraciones'})</span>
            </div>
        </div>`;

        // Formulario para añadir review (solo si está autenticado y no ha reviewado ya)
        if (appState.isAuthenticated) {
            const alreadyReviewed = reviews.some(r => r.reviewer_id === appState.currentUser.id);
            if (!alreadyReviewed) {
                const inputName = `${targetType}_${targetId}`;
                html += `<div class="review-form-wrap">
                    <h5>Deja tu valoración</h5>
                    <form onsubmit="submitReview(event, '${targetType}', ${targetId}, '${containerId}')">
                        <div class="review-form-stars">
                            ${buildStars(0, true, inputName)}
                        </div>
                        <textarea class="form-control review-comment" id="reviewComment_${containerId}"
                            placeholder="Escribe un comentario (opcional, máx. 500 caracteres)"
                            maxlength="500" rows="2"></textarea>
                        <button type="submit" class="btn btn-primary btn-sm" style="margin-top:0.5rem;">
                            Publicar valoración
                        </button>
                    </form>
                </div>`;
            }
        }

        // Lista de reviews
        if (reviews.length === 0) {
            html += '<p class="reviews-empty">Todavía no hay valoraciones para este elemento.</p>';
        } else {
            html += '<div class="reviews-list">';
            reviews.forEach(r => {
                const author = r.reviewer ? escHtml(r.reviewer.username) : 'Usuario';
                const date = new Date(r.created_at).toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric' });
                html += `<div class="review-item">
                    <div class="review-item-header">
                        <span class="review-author">${author}</span>
                        ${buildStars(r.rating)}
                        <span class="review-date">${date}</span>
                    </div>
                    ${r.comment ? `<p class="review-text">${escHtml(r.comment)}</p>` : ''}
                </div>`;
            });
            html += '</div>';
        }

        html += '</div>';
        container.innerHTML = html;

    } catch (e) {
        container.innerHTML = '<p class="reviews-error">No se pudieron cargar las valoraciones.</p>';
    }
}

/**
 * Envía una nueva review al backend.
 */
async function submitReview(event, targetType, targetId, containerId) {
    event.preventDefault();
    const form = event.target;
    const inputName = `${targetType}_${targetId}`;
    const ratingInput = form.querySelector(`input[name="${inputName}"]:checked`);
    if (!ratingInput) {
        showAlert('Selecciona una puntuación antes de publicar.', 'warning');
        return;
    }
    const rating = parseInt(ratingInput.value);
    const commentEl = document.getElementById('reviewComment_' + containerId);
    const comment = commentEl ? commentEl.value.trim() : '';

    try {
        await apiRequest('/reviews', {
            method: 'POST',
            body: JSON.stringify({
                target_type: targetType,
                target_id: targetId,
                rating,
                comment: comment || null
            })
        });
        showAlert('Valoración publicada correctamente.', 'success');
        loadReviews(targetType, targetId, containerId);
    } catch (e) {
        const msg = e.message || '';
        if (msg.includes('409') || msg.toLowerCase().includes('ya has')) {
            showAlert('Ya has valorado este elemento.', 'warning');
        } else {
            showAlert('Error al publicar la valoración.', 'danger');
        }
    }
}
