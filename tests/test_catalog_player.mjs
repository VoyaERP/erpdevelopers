/* Execute the real browser-facing script against a tiny DOM harness.
 * No third-party dependencies and no network access or browser cookies.
 */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import {runInNewContext} from "node:vm";

const source = readFileSync(new URL("../erpdevelopers/public/js/catalog.js", import.meta.url), "utf8");
const playlistId = "PLabcdefghijklmnopqrst0123456";

function setup({id=playlistId, modalAvailable=true, modalThrows=false}={}) {
  const calls = {open:0, close:0, focused:0, removed:0, blocked:0};
  const events = {};
  const frame = {
    src: null,
    removeAttribute(name) {
      assert.equal(name, "src");
      this.src = null;
      calls.removed++;
    },
  };
  const title = {textContent:""};
  const external = {href:"https://www.youtube.com/"};
  const closeButton = {
    focus(){ calls.focused++; },
    addEventListener(name, fn) { this[name] = fn; },
  };
  const link = {
    href:"https://www.youtube.com/playlist?list=" + playlistId,
    dataset:{playlistId:id,playlistTitle:"Architecture Basics"},
    isConnected:true,
    addEventListener(name, fn){ this[name] = fn; },
    focus(){ calls.focused++; },
  };
  const dialog = {
    open:false,
    querySelector(selector) {
      return ({
        "[data-player-frame]":frame,
        "#ed-playlist-dialog-title":title,
        "[data-player-external]":external,
        "[data-player-close]":closeButton
      })[selector] || null;
    },
    addEventListener(name, fn){ events[name] = fn; },
    close(){
      this.open = false;
      calls.close++;
      events.close?.();
    },
  };
  if (modalAvailable) dialog.showModal = () => {
    if (modalThrows) throw new Error("Dialog blocked");
    dialog.open = true;
    calls.open++;
  };
  const document = {
    readyState:"complete",
    getElementById(name) { return name === "ed-playlist-dialog" ? dialog : null; },
    querySelectorAll(selector) {
      if (selector === "[data-playlist-open]") return [link];
      if (selector === "[data-catalog-filter]") return [];
      throw new Error("Unexpected selector " + selector);
    },
  };
  runInNewContext(source, {document, URL});
  const click = () => {
    let prevented = false;
    link.click?.({
      target:link,
      preventDefault() { prevented = true; calls.blocked++; },
    });
    return prevented;
  };
  return {calls,frame,title,external,link,dialog,closeButton,click};
}

test("no iframe source is loaded before explicit user action", () => {
  const {frame,dialog,link} = setup();
  assert.equal(frame.src, null);
  assert.equal(dialog.open, false);
  assert.equal(link.href, "https://www.youtube.com/playlist?list=" + playlistId);
});

test("valid playlist opens native modal with official playlist embed URL", () => {
  const dom = setup();
  assert.equal(dom.click(), true, "intercept only when the dialog opens");
  assert.equal(dom.dialog.open, true);
  assert.equal(dom.calls.open, 1);
  assert.equal(dom.title.textContent, "Architecture Basics");
  const player = new URL(dom.frame.src);
  assert.equal(player.origin, "https://www.youtube-nocookie.com");
  assert.equal(player.pathname, "/embed/videoseries");
  assert.equal(player.searchParams.get("list"), playlistId);
  assert.equal(player.searchParams.get("autoplay"), "0");
  assert.equal(dom.external.href, "https://www.youtube.com/playlist?list=" + playlistId);
  dom.closeButton.click();
  assert.equal(dom.frame.src, null, "closing removes the source and stops playback");
  assert.equal(dom.calls.removed, 1);
});

test("unsupported dialog keeps the native external YouTube link functional", () => {
  const dom = setup({modalAvailable:false});
  assert.equal(dom.click(), false);
  assert.equal(dom.frame.src, null);
  assert.equal(dom.link.href, "https://www.youtube.com/playlist?list=" + playlistId);
});

test("a blocked showModal does not consume the link click", () => {
  const dom = setup({modalThrows:true});
  assert.equal(dom.click(), false);
  assert.equal(dom.dialog.open, false);
  assert.equal(dom.frame.src, null);
});

test("invalid playlist IDs never reach a frame", () => {
  const dom = setup({id:"invalid<script>"});
  assert.equal(dom.click(), false);
  assert.equal(dom.frame.src, null);
  assert.equal(dom.calls.open, 0);
});
