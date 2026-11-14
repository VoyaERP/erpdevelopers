/* One-page, Greenbox-style meeting calendar. ERPNext owns real availability,
 * Appointment verification, Lead matching and Calendar Events.
 * No client-side storage, fabricated slots, CRM writes or third-party embeds.
 */
(() => {
  "use strict";
  function start() {
    const form = document.querySelector("#ed-meeting-form");
    if (!form) return;
    const el = id => document.getElementById(id);
    const fields = form.querySelector(".ed-meet-fields");
    const topic = el("ed-meeting-topic");
    const zone = el("ed-meeting-zone");
    const days = el("ed-meeting-days");
    const weekdays = form.querySelector(".ed-meeting-weekdays");
    const monthLabel = el("ed-meeting-month");
    const prev = el("ed-month-prev");
    const next = el("ed-month-next");
    const slots = el("ed-meeting-slots");
    const summary = el("ed-meeting-selection-value");
    const asideSummary = el("ed-meet-aside-selection");
    const feedback = el("ed-meeting-feedback");
    const submit = el("ed-meeting-submit");
    const finished = form.querySelector('[data-meeting-stage="done"]');
    const language = document.documentElement.lang || "en";
    const state = {
      ready: form.dataset.bookingReady === "1",
      active: false, settings: null, today: "", max: "",
      month: null, date: "", time: "", seq: 0, loading: false,
      saving: false, sent: false
    };
    const rpc = "erpdevelopers.meeting_booking.";
    const message = key => form.dataset[key] || "";

    function setFeedback(text, isError = false) {
      feedback.textContent = text;
      feedback.classList.toggle("is-error", isError);
    }
    function iso(y, m, d) {
      return String(y).padStart(4, "0") + "-" + String(m + 1).padStart(2, "0") + "-" + String(d).padStart(2, "0");
    }
    function zoneToday() {
      const parts = new Intl.DateTimeFormat("en-GB", {
        year: "numeric", month: "2-digit", day: "2-digit", timeZone: zone.value
      }).formatToParts(new Date());
      const v = name => parts.find(part => part.type === name)?.value;
      return v("year") + "-" + v("month") + "-" + v("day");
    }
    function dateLabel(value) {
      const dt = new Date(value + "T12:00:00Z");
      return new Intl.DateTimeFormat(language, {
        day: "numeric", month: "short", year: "numeric", timeZone: "UTC"
      }).format(dt);
    }
    function updateSummary() {
      const content = state.date && state.time
        ? dateLabel(state.date) + " · " + state.time.slice(0, 5) + " · " + zone.value
        : form.dataset.chosen || "";
      summary.textContent = content;
      if (asideSummary) asideSummary.textContent = state.date && state.time
        ? content : asideSummary.dataset.hint;
      submit.disabled = !(state.active && state.date && state.time && !state.loading &&
        !state.saving && !state.sent && form.checkValidity());
    }
    function renderDays() {
      if (!state.month || !state.today) return;
      const year = state.month.getUTCFullYear(), month = state.month.getUTCMonth();
      const first = new Date(Date.UTC(year, month, 1, 12)).getUTCDay();
      const count = new Date(Date.UTC(year, month + 1, 0, 12)).getUTCDate();
      monthLabel.textContent = new Intl.DateTimeFormat(language, {
        month: "long", year: "numeric", timeZone: "UTC"
      }).format(state.month);
      days.replaceChildren();
      for (let i = 0; i < first; i++) {
        const empty = document.createElement("span");
        empty.className = "ed-meeting-day-empty";
        empty.setAttribute("aria-hidden", "true");
        days.appendChild(empty);
      }
      for (let day = 1; day <= count; day++) {
        const value = iso(year, month, day);
        const button = document.createElement("button");
        button.type = "button";
        button.className = "ed-meeting-day";
        button.textContent = String(day);
        button.disabled = !state.active || value < state.today || value > state.max;
        button.setAttribute("aria-label", (message("chooseDay") || "Choose date") + " " + dateLabel(value));
        button.setAttribute("aria-pressed", String(state.date === value));
        if (value === state.today) button.classList.add("is-today");
        if (value === state.date) button.classList.add("is-selected");
        button.addEventListener("click", () => {
          state.date = value;
          state.time = "";
          renderDays();
          loadSlots();
        });
        days.appendChild(button);
      }
      const firstOfMonth = iso(year, month, 1);
      prev.disabled = !state.active || firstOfMonth <= state.today.slice(0, 7) + "-01";
      next.disabled = !state.active || firstOfMonth >= state.max.slice(0, 7) + "-01";
    }
    function renderWeekdays() {
      weekdays.replaceChildren();
      // 2026-01-04 was a Sunday, preserving the native calendar's Sunday-first order.
      for (let day = 4; day <= 10; day++) {
        const value = new Date(Date.UTC(2026, 0, day, 12));
        const label = document.createElement("span");
        label.textContent = new Intl.DateTimeFormat(language, {
          weekday: "short", timeZone: "UTC"
        }).format(value);
        weekdays.appendChild(label);
      }
    }
    function slotHint(value, busy = false) {
      const p = document.createElement("p");
      p.className = "ed-meeting-slot-placeholder";
      p.textContent = value;
      slots.replaceChildren(p);
      slots.setAttribute("aria-busy", String(busy));
    }
    function call(method, args, type = "GET") {
      return new Promise((resolve, reject) => {
        if (!window.frappe || typeof window.frappe.call !== "function") {
          reject(new Error("Booking service unavailable"));
          return;
        }
        window.frappe.call({
          method: rpc + method, args, type,
          callback: reply => reply && !reply.exc
            ? resolve(reply.message)
            : reject(new Error("Booking request failed")),
          error: reject
        });
      });
    }
    async function loadSlots() {
      if (!state.active || !state.date) return;
      const seq = ++state.seq;
      state.loading = true;
      slotHint(message("load"), true);
      updateSummary();
      try {
        const result = await call("get_meeting_slots", { date: state.date, timezone: zone.value });
        if (seq !== state.seq) return;
        slots.replaceChildren();
        let count = 0;
        for (const entry of Array.isArray(result) ? result : []) {
          const match = String(entry.time || "").match(/(?:^|[T ])(\d{2}:\d{2}:\d{2})/);
          if (!match) continue;
          const time = match[1];
          const option = document.createElement("button");
          option.type = "button";
          option.className = "ed-meeting-slot";
          option.textContent = time.slice(0, 5);
          option.disabled = !entry.availability;
          option.setAttribute("aria-pressed", "false");
          option.addEventListener("click", () => {
            state.time = time;
            slots.querySelectorAll("button").forEach(button => {
              button.setAttribute("aria-pressed", String(button === option));
            });
            updateSummary();
          });
          slots.appendChild(option);
          if (entry.availability) count++;
        }
        if (!count) slotHint(message("noSlots"));
        else slots.setAttribute("aria-busy", "false");
      } catch (error) {
        if (seq === state.seq) {
          slotHint(message("slotError"));
          setFeedback(message("slotError"), true);
        }
      } finally {
        if (seq === state.seq) {
          state.loading = false;
          updateSummary();
        }
      }
    }
    function resetCalendar() {
      ++state.seq;
      state.date = "";
      state.time = "";
      state.today = zoneToday();
      const daysAhead = Math.min(90, Math.max(1, Number(state.settings?.advance_booking_days) || 7));
      const last = new Date(Date.parse(state.today + "T12:00:00Z") + daysAhead * 86400000);
      state.max = last.toISOString().slice(0, 10);
      const base = new Date(state.today + "T12:00:00Z");
      state.month = new Date(Date.UTC(base.getUTCFullYear(), base.getUTCMonth(), 1, 12));
      renderDays();
      slotHint(state.active ? message("dateHint") : message("offline"));
      updateSummary();
    }
    function detectTimezone() {
      try {
        const found = Intl.DateTimeFormat().resolvedOptions().timeZone;
        if (!found) return;
        if (!Array.from(zone.options).some(option => option.value === found)) {
          zone.add(new Option(found.replaceAll("_", " "), found));
        }
        zone.value = found;
      } catch (_) {
        // The displayed default remains Cairo when detection is unavailable.
      }
    }
    prev.addEventListener("click", () => {
      state.month = new Date(Date.UTC(state.month.getUTCFullYear(), state.month.getUTCMonth() - 1, 1, 12));
      renderDays();
    });
    next.addEventListener("click", () => {
      state.month = new Date(Date.UTC(state.month.getUTCFullYear(), state.month.getUTCMonth() + 1, 1, 12));
      renderDays();
    });
    zone.addEventListener("change", resetCalendar);
    form.addEventListener("input", updateSummary);
    form.addEventListener("change", updateSummary);
    form.addEventListener("submit", async event => {
      event.preventDefault();
      if (!state.active || state.saving || state.sent || !state.date || !state.time) return;
      if (!form.reportValidity()) return;
      state.saving = true;
      submit.disabled = true;
      setFeedback(message("submit"));
      const entries = Object.fromEntries(new FormData(form).entries());
      const contact = {
        name: entries.name || "", email: entries.email || "",
        company: entries.company || "", phone: entries.phone || "",
        message: entries.message || "", topic: topic.value,
        consent: el("ed-meeting-consent").checked ? 1 : 0,
        website: entries.website || ""
      };
      try {
        const reply = await call("book_meeting", {
          date: state.date, time: state.time, timezone: zone.value,
          contact: JSON.stringify(contact)
        }, "POST");
        if (!reply || !reply.accepted) throw new Error("Booking not accepted");
        state.sent = true;
        fields.hidden = true;
        finished.hidden = false;
        setFeedback(message("verified"));
        finished.querySelector("h3")?.focus?.();
      } catch (error) {
        setFeedback(message("submitError"), true);
      } finally {
        state.saving = false;
        updateSummary();
      }
    });

    renderWeekdays();
    detectTimezone();
    // The public page keeps the complete calendar layout while the site is
    // unconfigured. In this state dates/fields are disabled and no API is called.
    if (!state.ready) {
      fields.disabled = true;
      resetCalendar();
      return;
    }
    call("get_meeting_settings", {}).then(settings => {
      if (!settings?.enabled) throw new Error("Calendar unavailable");
      state.settings = settings;
      state.active = true;
      fields.disabled = false;
      resetCalendar();
    }).catch(() => {
      state.active = false;
      fields.disabled = true;
      resetCalendar();
      setFeedback(message("connection"), true);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
