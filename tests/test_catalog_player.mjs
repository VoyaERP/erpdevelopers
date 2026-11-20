/* Execute the shipped player. No external link element or network is available. */
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import {runInNewContext} from "node:vm";
const source = readFileSync(new URL("../erpdevelopers/public/js/catalog.js", import.meta.url), "utf8");
const playlistId = "PLabcdefghijklmnopqrst0123456";
function node(props={}) {
  const events = {};
  return Object.assign({events,dataset:{},hidden:false,isConnected:true,focused:0,
    addEventListener(name,fn){(events[name] ||= []).push(fn);},
    emit(name,event={}){for(const fn of events[name] || []) fn(event);},
    focus(){this.focused++;}},props);
}
function setup({id=playlistId,modalAvailable=true,modalThrows=false,statusPresent=true,missingDialog=false,missingFrame=false,loading=false}={}) {
  const frame=node({src:null,removeAttribute(name){assert.equal(name,"src");this.src=null;},getAttribute(name){assert.equal(name,"src");return this.src;}});
  const title=node({textContent:"Watch playlist"}), closeButton=node(), status=node({hidden:true});
  const control=node({disabled:true,dataset:{playlistId:id,playlistTitle:"Architecture Basics"}});
  const dialog=node({open:false,opens:0,
    querySelector(selector){return ({"[data-player-frame]":missingFrame?null:frame,"#ed-playlist-dialog-title":title,"[data-player-close]":closeButton,"[data-player-status]":statusPresent?status:null})[selector] || null;},
    close(){this.open=false;this.emit("close");},getBoundingClientRect(){return {left:20,right:900,top:20,bottom:600};}});
  if(modalAvailable) dialog.showModal=()=>{if(modalThrows) throw new Error("Dialog blocked");dialog.open=true;dialog.opens++;};
  const cards=[node({dataset:{catalogTopic:"ERP"}}),node({dataset:{catalogTopic:"Cloud"}})];
  const counter=node({textContent:""}),select=node({value:"",dataset:{catalogFilter:"#cards",countTarget:"#count"}});
  const document=node({readyState:loading?"loading":"complete",
    getElementById(name){return name==="ed-playlist-dialog"&&!missingDialog?dialog:null;},
    querySelectorAll(selector){if(selector==="[data-playlist-open]")return [control];if(selector==="[data-catalog-filter]")return [select];throw new Error(selector);},
    querySelector(selector){return selector==="#count"?counter:{querySelectorAll:()=>cards};}});
  const run=()=>runInNewContext(source,{document,URL});run();
  const click=()=>{let prevented=false;control.emit("click",{preventDefault(){prevented=true;}});return prevented;};
  return {frame,title,closeButton,status,control,dialog,document,select,cards,counter,click,run};
}
test("no embed request before explicit action",()=>{const d=setup();assert.equal(d.frame.src,null);assert.equal(d.dialog.open,false);assert.equal(d.control.disabled,false);});
test("player works without any external YouTube link element",()=>{const d=setup();assert.equal(d.click(),true);assert.equal(d.dialog.open,true);assert.equal(d.dialog.opens,1);assert.equal(d.title.textContent,"Architecture Basics");const url=new URL(d.frame.src);assert.equal(url.origin,"https://www.youtube-nocookie.com");assert.equal(url.pathname,"/embed/videoseries");assert.equal(url.searchParams.get("list"),playlistId);assert.equal(url.searchParams.get("autoplay"),"0");assert.equal(d.status.hidden,false);d.frame.emit("load");assert.equal(d.status.hidden,true);});
test("optional status missing does not break playback",()=>{const d=setup({statusPresent:false});d.click();assert.equal(d.dialog.open,true);assert.ok(d.frame.src);});
test("close stops playback and restores focus",()=>{const d=setup();d.click();d.closeButton.emit("click");assert.equal(d.frame.src,null);assert.equal(d.control.focused,1);});
test("Escape close clears the frame",()=>{const d=setup();d.click();d.dialog.open=false;d.dialog.emit("close");assert.equal(d.frame.src,null);});
test("unsupported dialogs cannot navigate away",()=>{const d=setup({modalAvailable:false});assert.equal(d.control.disabled,true);assert.equal(d.click(),true);assert.equal(d.frame.src,null);});
test("blocked modal consumes a legacy anchor click",()=>{const d=setup({modalThrows:true});d.control.href="https://www.youtube.com/playlist?list="+playlistId;assert.equal(d.click(),true);assert.equal(d.dialog.open,false);assert.equal(d.frame.src,null);assert.equal(d.control.disabled,true);});
test("invalid IDs do not reach a frame",()=>{const d=setup({id:"invalid<script>"});assert.equal(d.control.disabled,true);d.click();assert.equal(d.frame.src,null);});
test("missing dialog leaves filtering operational",()=>{const d=setup({missingDialog:true});assert.equal(d.click(),true);assert.equal(d.frame.src,null);assert.equal(d.counter.textContent,"2");});
test("missing required frame disables playback",()=>{const d=setup({missingFrame:true});assert.equal(d.control.disabled,true);d.click();assert.equal(d.dialog.open,false);});
test("head script binds on DOMContentLoaded",()=>{const d=setup({loading:true});assert.equal(d.control.disabled,true);d.document.emit("DOMContentLoaded");assert.equal(d.control.disabled,false);d.click();assert.equal(d.dialog.open,true);});
test("repeat initialization does not bind twice",()=>{const d=setup();d.run();d.click();assert.equal(d.control.events.click.length,1);assert.equal(d.dialog.opens,1);});
test("only an actual backdrop click dismisses the dialog",()=>{const d=setup();d.click();d.dialog.emit("click",{target:d.dialog,clientX:100,clientY:100});assert.equal(d.dialog.open,true);d.dialog.emit("click",{target:d.dialog,clientX:0,clientY:0});assert.equal(d.dialog.open,false);assert.equal(d.frame.src,null);});
test("filters retain visible counts",()=>{const d=setup();d.select.value="Cloud";d.select.emit("change");assert.equal(d.counter.textContent,"1");assert.equal(d.cards[0].hidden,true);assert.equal(d.cards[1].hidden,false);});
