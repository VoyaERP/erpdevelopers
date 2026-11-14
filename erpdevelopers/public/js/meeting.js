/* ERP Developers meeting calendar. ERPNext is the slot and appointment authority.
 * No fabricated availability, browser persistence, third-party calendar or CRM writes.
 */
(() => {
  "use strict";
  function start() {
    const form = document.querySelector("#ed-meeting-form");
    if (!form) return;
    const el = id => form.querySelector("#" + id);
    const topic = el("ed-meeting-topic");
    const zone = el("ed-meeting-zone");
    const calendar = el("ed-meeting-days");
    const weekdays = form.querySelector(".ed-meeting-weekdays");
    const title = el("ed-meeting-month");
    const prev = el("ed-month-prev");
    const next = el("ed-month-next");
    const slots = el("ed-meeting-slots");
    const summary = el("ed-meeting-selection-value");
    const feedback = el("ed-meeting-feedback");
    const nextButton = el("ed-meeting-next");
    const back = el("ed-meeting-back");
    const submit = el("ed-meeting-submit");
    const panes = form.querySelectorAll("[data-meeting-stage]");
    const progress = form.querySelectorAll(".ed-meeting-progress span");
    const rpc = "erpdevelopers.meeting_booking.";
    const language = document.documentElement.lang || "en";
    const state = { settings:null, today:"", max:"", date:"", time:"", month:null,
      loading:false, saving:false, finished:false, seq:0 };

    const t = key => form.dataset[key] || "";
    const setFeedback = (text, error=false) => {
      feedback.textContent = text;
      feedback.classList.toggle("is-error", error);
    };
    function todayInZone(tz) {
      const parts = new Intl.DateTimeFormat("en-GB", {
        timeZone:tz, year:"numeric", month:"2-digit", day:"2-digit"
      }).formatToParts(new Date());
      const value = key => parts.find(p => p.type === key).value;
      return value("year")+"-"+value("month")+"-"+value("day");
    }
    function iso(y,m,d) {
      return [String(y).padStart(4,"0"),String(m+1).padStart(2,"0"),String(d).padStart(2,"0")].join("-");
    }
    function monthDate(month) {
      return new Date(Date.UTC(month.getUTCFullYear(), month.getUTCMonth(), 1, 12));
    }
    function localLabel(ymd) {
      const dt = new Date(ymd+"T12:00:00Z");
      return new Intl.DateTimeFormat(language,{day:"numeric",month:"short",year:"numeric",timeZone:"UTC"}).format(dt);
    }
    function updateSummary() {
      summary.textContent = state.date && state.time
        ? localLabel(state.date)+" · "+state.time.slice(0,5)+" · "+zone.value
        : t("chosen") || "";
      nextButton.disabled = !state.settings || !state.date || !state.time || state.loading || state.saving;
    }
    function showPane(name) {
      panes.forEach(pane=>{pane.hidden=pane.dataset.meetingStage!==name;});
      progress.forEach((p,i)=>p.classList.toggle("is-active",name==="time" ? i===0 : true));
      setFeedback("");
      if(name==="contact") el("ed-meeting-name").focus();
      if(name==="time") topic.focus();
    }
    function renderDays() {
      if(!state.month || !state.today) return;
      const y=state.month.getUTCFullYear(), m=state.month.getUTCMonth();
      const first=new Date(Date.UTC(y,m,1,12)).getUTCDay();
      const count=new Date(Date.UTC(y,m+1,0,12)).getUTCDate();
      title.textContent=new Intl.DateTimeFormat(language,{month:"long",year:"numeric",timeZone:"UTC"}).format(state.month);
      calendar.replaceChildren();
      for(let i=0;i<first;i++){
        const empty=document.createElement("span");
        empty.className="ed-meeting-day-empty";
        empty.setAttribute("aria-hidden","true");
        calendar.appendChild(empty);
      }
      for(let day=1;day<=count;day++){
        const value=iso(y,m,day);
        const btn=document.createElement("button");
        btn.type="button";
        btn.className="ed-meeting-day";
        btn.textContent=String(day);
        btn.disabled=value<state.today || value>state.max;
        btn.setAttribute("aria-label",(t("chooseDay") || "Choose date")+" "+localLabel(value));
        btn.setAttribute("aria-pressed",String(value===state.date));
        if(value===state.today)btn.classList.add("is-today");
        if(value===state.date)btn.classList.add("is-selected");
        btn.addEventListener("click",()=>{state.date=value; state.time=""; renderDays(); loadSlots();});
        calendar.appendChild(btn);
      }
      const thisMonth=iso(y,m,1), minMonth=state.today.slice(0,7)+"-01", maxMonth=state.max.slice(0,7)+"-01";
      prev.disabled=thisMonth<=minMonth;
      next.disabled=thisMonth>=maxMonth;
    }
    function renderWeekdays() {
      weekdays.replaceChildren();
      for(let day=4;day<=10;day++){ // Jan 4, 2026 is a Sunday.
        const dt=new Date(Date.UTC(2026,0,day,12));
        const label=document.createElement("span");
        label.textContent=new Intl.DateTimeFormat(language,{weekday:"short",timeZone:"UTC"}).format(dt);
        weekdays.appendChild(label);
      }
    }
    function renderSlotsHint(message,loading=false) {
      const p=document.createElement("p");
      p.className="ed-meeting-slot-placeholder";
      p.textContent=message;
      slots.replaceChildren(p);
      slots.setAttribute("aria-busy",String(loading));
    }
    function call(method,args,type="GET") {
      return new Promise((resolve,reject)=>{
        if(!window.frappe || typeof window.frappe.call!=="function") return reject(new Error("RPC unavailable"));
        window.frappe.call({
          method:rpc+method,args,type,
          callback:r=>r&& !r.exc ? resolve(r.message):reject(new Error("Request failed")),
          error:reject
        });
      });
    }
    async function loadSlots() {
      const seq=++state.seq;
      state.loading=true;
      updateSummary();
      renderSlotsHint(t("load"),true);
      try {
        const result=await call("get_meeting_slots",{date:state.date,timezone:zone.value});
        if(seq!==state.seq)return;
        slots.replaceChildren();
        let available=0;
        for(const entry of Array.isArray(result)?result:[]){
          const raw=String(entry.time||"");
          const match=raw.match(/(?:^|[T ])(\d{2}:\d{2}:\d{2})/);
          if(!match)continue;
          const time=match[1];
          const button=document.createElement("button");
          button.type="button";
          button.className="ed-meeting-slot";
          button.textContent=time.slice(0,5);
          button.disabled=!entry.availability;
          button.setAttribute("aria-pressed","false");
          button.addEventListener("click",()=>{
            state.time=time;
            slots.querySelectorAll("button").forEach(item=>{
              item.setAttribute("aria-pressed",String(item===button));
            });
            updateSummary();
          });
          slots.appendChild(button);
          if(entry.availability)available++;
        }
        if(!available)renderSlotsHint(t("noSlots"));
        else slots.setAttribute("aria-busy","false");
      } catch(error) {
        if(seq===state.seq){renderSlotsHint(t("slotError"));setFeedback(t("slotError"),true);}
      } finally {
        if(seq===state.seq){state.loading=false;updateSummary();}
      }
    }
    function resetCalendar() {
      if(!state.settings)return;
      state.seq++;
      state.date="";state.time="";
      state.today=todayInZone(zone.value);
      const maxMs=Date.parse(state.today+"T12:00:00Z")+
        Math.min(90,Math.max(1,Number(state.settings.advance_booking_days)||7))*86400000;
      state.max=new Date(maxMs).toISOString().slice(0,10);
      state.month=monthDate(new Date(state.today+"T12:00:00Z"));
      renderDays();
      renderSlotsHint(t("dateHint"));
      updateSummary();
    }
    function setZone() {
      try {
        const detected=Intl.DateTimeFormat().resolvedOptions().timeZone;
        if(!detected)return;
        let opt=Array.from(zone.options).find(x=>x.value===detected);
        if(!opt) {
          opt=new Option(detected.replaceAll("_"," "),detected);
          zone.add(opt);
        }
        zone.value=detected;
      } catch(error) { /* Stay with server-visible default timezone. */ }
    }
    prev.addEventListener("click",()=>{state.month=new Date(Date.UTC(state.month.getUTCFullYear(),state.month.getUTCMonth()-1,1,12));renderDays();});
    next.addEventListener("click",()=>{state.month=new Date(Date.UTC(state.month.getUTCFullYear(),state.month.getUTCMonth()+1,1,12));renderDays();});
    zone.addEventListener("change",resetCalendar);
    nextButton.addEventListener("click",()=>{
      if(nextButton.disabled || !topic.reportValidity())return;
      showPane("contact");
    });
    back.addEventListener("click",()=>showPane("time"));
    form.addEventListener("submit",async event=>{
      event.preventDefault();
      if(state.saving || state.finished || !state.date || !state.time)return;
      if(!form.reportValidity())return;
      state.saving=true;submit.disabled=true;back.disabled=true;
      setFeedback(t("submit"));
      const values=Object.fromEntries(new FormData(form).entries());
      const contact={
        name:values.name||"",email:values.email||"",phone:values.phone||"",
        company:values.company||"",topic:topic.value,message:values.message||"",
        consent:el("ed-meeting-consent").checked?1:0,website:values.website||""
      };
      try {
        const result=await call("book_meeting",{
          date:state.date,time:state.time,timezone:zone.value,
          contact:JSON.stringify(contact)
        },"POST");
        if(!result || !result.accepted)throw new Error("Not accepted");
        state.finished=true;
        showPane("done");
        setFeedback(t("verified"));
      } catch(error) {
        setFeedback(t("submitError"),true);
      } finally {
        state.saving=false;
        submit.disabled=state.finished;
        back.disabled=state.finished;
      }
    });
    renderWeekdays();
    setZone();
    call("get_meeting_settings",{}).then(data=>{
      if(!data || !data.enabled)throw new Error("Scheduler disabled");
      state.settings=data;
      resetCalendar();
    }).catch(()=>{renderSlotsHint(t("connection"));setFeedback(t("connection"),true);});
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",start);
  else start();
})();
