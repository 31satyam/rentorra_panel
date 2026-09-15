/**
 * Rentorra Core Front-End JavaScript
 * Handles dynamic modal fills, gallery thumbnails, and lead interaction.
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Dynamic Enquiry Modal Data Population
    const enquiryModal = document.getElementById('globalEnquiryModal');
    if (enquiryModal) {
        document.querySelectorAll('.open-enquiry-modal-btn').forEach(button => {
            button.addEventListener('click', function () {
                const propId = this.getAttribute('data-property-id') || '';
                const propTitle = this.getAttribute('data-property-title') || 'Selected Property';
                const propCity = this.getAttribute('data-property-city') || '';
                const propBhk = this.getAttribute('data-property-bhk') || '';
                const propRent = this.getAttribute('data-property-rent') || '';

                const inputId = document.getElementById('modal_input_property_id');
                const inputCity = document.getElementById('modal_input_city');
                const inputBhk = document.getElementById('modal_input_bhk');
                const inputMinBudget = document.getElementById('modal_input_min_budget');
                const inputMaxBudget = document.getElementById('modal_input_max_budget');
                const subtitle = document.getElementById('modalPropertySubtitle');
                const modalTitle = document.getElementById('globalEnquiryModalLabel');

                if (inputId) inputId.value = propId;
                if (inputCity) inputCity.value = propCity;
                if (inputBhk) inputBhk.value = propBhk;
                if (inputMinBudget) inputMinBudget.value = propRent;
                if (inputMaxBudget) inputMaxBudget.value = propRent;

                if (subtitle) {
                    subtitle.textContent = propTitle ? `Enquiring for: ${propTitle}` : 'Our rental specialist will reach out within 15 minutes.';
                }
                if (modalTitle && propTitle) {
                    modalTitle.textContent = `Enquire: ${propTitle}`;
                }
            });
        });
    }

    // 2. Mobile Phone Inputs - Restrict to digits only
    document.querySelectorAll('input[type="tel"]').forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9+]/g, '');
        });
    });

    // 3. Double-submission prevention on all forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                // Allow form to serialize before disabling
                setTimeout(() => {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Submitting...';
                }, 100);
            }
        });
    });

    // 4. Auto-dismiss Alert Messages after 5 seconds
    const flashAlerts = document.querySelectorAll('.alert-dismissible');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });
});
