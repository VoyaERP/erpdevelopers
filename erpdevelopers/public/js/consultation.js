/* Guest-only request submission using native Frappe RPC and its CSRF handling. */
(() => {
  "use strict";
  function init() {
    const form = document.querySelector("#ed-consultation-form");
    if (!form) return;
    const submit = form.querySelector('[type="submit"]');
    const feedback = form.querySelector("#ed-form-feedback");
    const timezone = form.querySelector("#ed-timezone");
    const dateField = form.querySelector("#ed-preferred-date");

    try {
      const iana = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if (iana && iana.length <= 64) timezone.value = iana;
    } catch (_) { /* UTC default remains usable */ }

    // Browser convenience only. The server validates the requested date.
    const today = new Date();
    const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000)
      .toISOString().slice(0, 10);
    dateField.min = localToday;
    const max = new Date(today.getTime());
    max.setDate(max.getDate() + 90);
    dateField.max = new Date(max.getTime() - max.getTimezoneOffset() * 60000)
      .toISOString().slice(0, 10);

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      if (!form.reportValidity() || submit.disabled) return;
      if (!window.frappe || typeof frappe.call !== "function") {
        feedback.textContent = "Connection is unavailable. Please retry.";
        return;
      }
      submit.disabled = true;
      feedback.textContent = "";
      const data = Object.fromEntries(new FormData(form).entries());
      data.contact_consent = form.querySelector('[name="contact_consent"]').checked ? 1 : 0;
      frappe.call({
        method: "erpdevelopers.appointments.request_consultation",
        args: data,
        callback: (response) => {
          if (response && response.message && response.message.accepted) {
            form.reset();
            feedback.textContent = form.dataset.success ||
              "Request received. A meeting is not confirmed until our team responds.";
          } else {
            feedback.textContent = "Unable to submit your request. Please try again.";
          }
          submit.disabled = false;
        },
        error: () => {
          feedback.textContent = "Unable to submit your request. Please review the details.";
          submit.disabled = false;
        },
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
