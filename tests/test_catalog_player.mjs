/* Run the shipped script, including stale markup and failure paths. No network. */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import {runInNewContext} from "node:vm";

const source = readFileSync(new URL("../erpdevelopers/public/js/catalog.js", import.meta.url), "utf8");
const playlistId = "PLabcdefghijklmnopqrst0123456";
function node(props={}) {
  const events = {};
  return Object.assign({
    events, dataset:{}, hidden:false, isConnected:true, focused:0,
    addEventListener(name, fn) { (events[name] ||= []).push(fn); },
    emit(name, event={}) { for (const fn of events[name] || []) fn(event); },
    focus() { this.focused++; },
  }, props);
}
function setup({id=playlistId, modalAvailable=true, modalThrows=false,
  statusPresent=true, missingDialog=false, missingFrame=false, loading=false}={}) {
  const frame = node({
    src:null,
    removeAttribute(name) { assert.equal(name,"src"); this.src=null; },
    getAttribute(name) { assert.equal(name,"src"); return this.src; },
  });
  const title = node({textContent:"Watch playlist"});
  const external = node({href:"https://www.youtube.com/"});
  const closeButton = node();
  const status = node({hidden:true});
  const control = node({disabled:true, dataset:{playlistId:id,playlistTitle:"Architecture Basics"}});
  const dialog = node({
    open:false, opens:0,
    querySelector(selector) { return ({
      "[data-player-frame]":missingFrame ? null : frame,
      "#ed-playlist-dialog-title":title,
      "[data-player-external]":external,
      "[data-player-close]":closeButton,
      "[data-player-status]":statusPresent ? status : null,
    })[selector] || null; },
    close() { this.open=false; this.emit("close"); },
    getBoundingClientRect() { return {left:20,right:900,top:20,bottom:600}; },
  });
  if (modalAvailable) dialog.showModal = () => {
    if (modalThrows) throw new Error("Dialog blocked");
    dialog.open=true; dialog.opens++;
  };
  const cards = [node({dataset:{catalogTopic:"ERP"}}),node({dataset:{catalogTopic:"Cloud"}})];
  const counter = node({textContent:""});
  const select = node({value:"",dataset:{catalogFilter:"#cards",countTarget:"#count"}});
  const document = node({
    readyState:loading ? "loading" : "complete",
    getElementById(name) { return name === "ed-playlist-dialog" && !missingDialog ? dialog : null; },
    querySelectorAll(selector) {
      if (selector === "[data-playlist-open]") return [control];
      if (selector === "[data-catalog-filter]") return [select];
      throw new Error("Unexpected selector: " + selector);
    },
    querySelector(selector) {
      return selector === "#count" ? counter : {querySelectorAll:() => cards};
    },
  });
  const run = () => runInNewContext(source, {document, URL});
  run();
  const click = () => {
    let prevented=false;
    control.emit("click",{preventDefault(){prevented=true;}});
    return prevented;
  };
  return {frame,title,external,closeButton,status,control,dialog,document,select,cards,counter,click,run};
}

test("no embed request before a visitor explicitly watches", () => {
  const d=setup();
  assert.equal(d.frame.src,null);
  assert.equal(d.dialog.open,false);
  assert.equal(d.control.disabled,false);
  assert.equal(d.external.events.click,undefined);
});
test("Watch here opens one modal and only assigns the privacy-enhanced iframe", () => {
  const d=setup();
  assert.equal(d.click(),true);
  assert.equal(d.dialog.open,true);
  assert.equal(d.dialog.opens,1);
  assert.equal(d.title.textContent,"Architecture Basics");
  const url=new URL(d.frame.src);
  assert.equal(url.origin,"https://www.youtube-nocookie.com");
  assert.equal(url.pathname,"/embed/videoseries");
  assert.equal(url.searchParams.get("list"),playlistId);
  assert.equal(url.searchParams.get("autoplay"),"0");
  assert.equal(d.external.href,"https://www.youtube.com/playlist?list="+playlistId);
  assert.equal(d.status.hidden,false);
  d.frame.emit("load");
  assert.equal(d.status.hidden,true);
});
test("optional loading message absent in stale markup does not break playback", () => {
  const d=setup({statusPresent:false});
  assert.equal(d.click(),true);
  assert.equal(d.dialog.open,true);
  assert.ok(d.frame.src);
});
test("close stops playback and returns keyboard focus", () => {
  const d=setup(); d.click(); d.closeButton.emit("click");
  assert.equal(d.frame.src,null);
  assert.equal(d.dialog.open,false);
  assert.equal(d.control.focused,1);
});
test("native Escape close event clears the frame too", () => {
  const d=setup(); d.click(); d.dialog.open=false; d.dialog.emit("close");
  assert.equal(d.frame.src,null);
});
test("unsupported dialogs disable the local button, never navigate", () => {
  const d=setup({modalAvailable:false});
  assert.equal(d.control.disabled,true);
  assert.equal(d.click(),true);
  assert.equal(d.frame.src,null);
});
test("failed showModal cannot fall through to legacy YouTube anchor navigation", () => {
  const d=setup({modalThrows:true});
  d.control.href="https://www.youtube.com/playlist?list="+playlistId;
  assert.equal(d.click(),true);
  assert.equal(d.dialog.open,false);
  assert.equal(d.frame.src,null);
  assert.equal(d.control.disabled,true);
});
test("invalid IDs never enter an iframe", () => {
  const d=setup({id:"invalid<script>"});
  assert.equal(d.control.disabled,true);
  assert.equal(d.click(),true);
  assert.equal(d.frame.src,null);
});
test("missing dialog suppresses legacy navigation without breaking filters", () => {
  const d=setup({missingDialog:true});
  assert.equal(d.click(),true);
  assert.equal(d.frame.src,null);
  assert.equal(d.counter.textContent,"2");
});
test("missing required frame disables playback rather than opening YouTube", () => {
  const d=setup({missingFrame:true});
  assert.equal(d.control.disabled,true);
  assert.equal(d.click(),true);
  assert.equal(d.dialog.open,false);
});
test("deferred head script initializes when DOMContentLoaded occurs", () => {
  const d=setup({loading:true});
  assert.equal(d.control.disabled,true);
  d.document.emit("DOMContentLoaded");
  assert.equal(d.control.disabled,false);
  d.click(); assert.equal(d.dialog.open,true);
});
test("repeat script evaluation does not register the player twice", () => {
  const d=setup(); d.run(); d.click();
  assert.equal(d.control.events.click.length,1);
  assert.equal(d.dialog.opens,1);
});
test("dialog padding is not treated as the backdrop", () => {
  const d=setup(); d.click();
  d.dialog.emit("click",{target:d.dialog,clientX:100,clientY:100});
  assert.equal(d.dialog.open,true);
  d.dialog.emit("click",{target:d.dialog,clientX:0,clientY:0});
  assert.equal(d.dialog.open,false);
  assert.equal(d.frame.src,null);
});
test("filtering still counts visible cards", () => {
  const d=setup(); d.select.value="Cloud"; d.select.emit("change");
  assert.equal(d.counter.textContent,"1");
  assert.equal(d.cards[0].hidden,true);
  assert.equal(d.cards[1].hidden,false);
});
