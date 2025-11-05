// About Us Page - Card Flip Animation

document.addEventListener('DOMContentLoaded', function() {
    const developerCards = document.querySelectorAll('.developer-card');
    
    developerCards.forEach(card => {
        const cardInner = card.querySelector('.card-inner');
        
        // Flip on card click
        cardInner.addEventListener('click', function() {
            card.classList.toggle('flipped');
        });
        
        // Optional: Flip on button click as well
        const btn = card.querySelector('.developer-name-btn');
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            card.classList.toggle('flipped');
        });
    });
});
