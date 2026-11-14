"use strict";

// Zero-dependency DOM harness for the decorative /login JavaScript.
// It deliberately keeps the Frappe native <main> and <form> as identity sentinels.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");

const loginSource = fs.readFileSync(
  path.join(__dirname, "../erpdevelopers/public/js/login_chrome.js"),
  "utf8",
);

function element(tag) {
  const node = {
    tag, className: "", id: "", dir: "", children: [], parent: null,
    attributes: {}, dataset: {}, textContent: "",

    setAttribute(name, value) { this.attributes[name] = value; },
    getAttribute(name) { return this.attributes[name] || null; },

    append(...children) { for (const child of children) attach(this, child); },
    appendChild(child) { attach(this, child); return child; },
    prepend(...children) {
      const siblings = [...children];
      for (const child of siblings) detach(child);
      for (const child of siblings) child.parent = this;
      this.children.unshift(...siblings);
    },
    before(other) {
      assert.ok(this.parent, "Cannot move a native selector without a parent");
      detach(other);
      const index = this.parent.children.indexOf(this);
      this.parent.children.splice(index, 0, other);
      other.parent = this.parent;
    },
    querySelector(selector) {
      return descendants(this).find((child) => matches(child, selector)) || null;
    },
  };
  node.classList = {
    add(name) {
      const entries = new Set(node.className.split(/\s+/).filter(Boolean));
      entries.add(name);
      node.className = [...entries].join(" ");
    },
  };
  return node;
}

function detach(child) {
  if (!child.parent) return;
  const index = child.parent.children.indexOf(child);
  if (index >= 0) child.parent.children.splice(index, 1);
  child.parent = null;
}

function attach(parent, child) {
  detach(child);
  parent.children.push(child);
  child.parent = parent;
}

function descendants(parent) {
  return parent.children.flatMap((child) => [child, ...descendants(child)]);
}

function matches(node, selector) {
  if (selector.startsWith(".")) {
    return node.className.split(/\s+/).includes(selector.slice(1));
  }
  if (selector.startsWith("#")) return node.id === selector.slice(1);
  return node.tag === selector;
}

function fixture(language = "en", pathname = "/login") {
  const body = element("body");
  const nativeNavbar = element("nav");
  nativeNavbar.className = "navbar";
  const picker = element("div");
  picker.id = "language-switcher";
  picker.append(element("select"));
  nativeNavbar.append(picker);

  const page = element("div");
  page.id = "page-login";
  const wrapper = element("div");
  wrapper.className = "page-content-wrapper";
  const main = element("main");
  const form = element("form"); // the native Frappe form must be unchanged
  main.append(form);
  wrapper.append(main);
  page.append(wrapper);
  body.append(nativeNavbar, page);

  const document = {
    body,
    documentElement: {lang: language},
    readyState: "complete",
    createElement: element,
    getElementById(id) {
      return descendants(body).find((child) => child.id === id) || null;
    },
    querySelector(selector) { return body.querySelector(selector); },
  };
  const window = {location: {pathname}};
  const render = () => vm.runInNewContext(loginSource, {window, document, Date});
  const count = (selector) => descendants(body).filter((node) => matches(node, selector)).length;
  return {body, nativeNavbar, picker, wrapper, main, form, render, count};
}

test("native login form and picker survive once-only branded rendering", () => {
  const f = fixture("en");
  f.render();
  assert.equal(f.count(".ed-login-header"), 1);
  assert.equal(f.count(".ed-login-footer"), 1);
  assert.equal(f.count(".ed-login-story"), 1);
  assert.equal(f.count("form"), 1);
  assert.strictEqual(f.form.parent, f.main);
  assert.strictEqual(f.main.parent, f.wrapper);
  assert.equal(f.count("#language-switcher"), 1);
  assert.equal(f.picker.parent.className, "ed-login-header-inner");
  assert.equal(f.body.dataset.edLoginEnhanced, "1");

  f.render(); // Simulate stale/repeated script without adding duplicate chrome.
  assert.equal(f.count(".ed-login-header"), 1);
  assert.equal(f.count(".ed-login-footer"), 1);
  assert.equal(f.count(".ed-login-story"), 1);
  assert.equal(f.count("form"), 1);
  assert.equal(f.count("#language-switcher"), 1);
});

test("Arabic locale renders the original story in RTL", () => {
  const f = fixture("ar");
  f.render();
  const aside = f.body.querySelector(".ed-login-story");
  assert.ok(aside);
  assert.equal(aside.dir, "rtl");
  assert.match(aside.querySelector(".ed-login-story-title").textContent, /مساحة تجمع/);
  assert.equal(f.count("form"), 1);
});

test("non-login routes are not altered", () => {
  const f = fixture("en", "/about");
  f.render();
  assert.equal(f.count(".ed-login-header"), 0);
  assert.equal(f.count(".ed-login-story"), 0);
  assert.equal(f.count("form"), 1);
  assert.equal(f.body.dataset.edLoginEnhanced, undefined);
});
