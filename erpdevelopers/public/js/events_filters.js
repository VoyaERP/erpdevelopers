/* Progressive-enhancement event filters: server-side pagination and query remain authoritative. */
(() => {
  "use strict";
  const form = document.querySelector("[data-events-filter-form]");
  if (!form) return;
  let debounce;
  const search = form.querySelector("input[name=q]");
  const submit = () => {
    const page = form.querySelector("input[name=page]");
    if (page) page.value = "1";
    if (typeof form.requestSubmit === "function") form.requestSubmit();
    else form.submit();
  };
  form.querySelectorAll("select").forEach(select => {
    select.addEventListener("change", submit);
  });
  if (search) search.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(submit, 450);
  });
})();
