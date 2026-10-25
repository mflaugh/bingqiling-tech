// Demo project: Ember & Oak (fictional). All data below is sample content.
const BEANS = [
  { name: "Morning Ember", roast: "light", notes: "Citrus, honey, jasmine", price: 16 },
  { name: "Oak House Blend", roast: "medium", notes: "Chocolate, caramel, almond", price: 15 },
  { name: "Highland Sample", roast: "light", notes: "Berry, black tea", price: 18 },
  { name: "Copper Kettle", roast: "medium", notes: "Brown sugar, cherry", price: 17 },
  { name: "Night Shift", roast: "dark", notes: "Cocoa, smoke, molasses", price: 15 },
  { name: "Decaf Hearth", roast: "dark", notes: "Toffee, walnut", price: 16 },
];
const grid = document.getElementById("bean-grid");
function renderBeans(filter = "all") {
  grid.innerHTML = BEANS.filter(b => filter === "all" || b.roast === filter).map(b => `
    <article class="card">
      <span class="tag">${b.roast} roast</span>
      <h3>${b.name}</h3><p>${b.notes}</p>
      <span class="price">$${b.price} / 250g <small>(sample price)</small></span>
    </article>`).join("");
}
document.querySelectorAll(".chip").forEach(chip => chip.addEventListener("click", () => {
  document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
  chip.classList.add("active"); renderBeans(chip.dataset.filter);
}));
renderBeans();

// Mobile nav
const toggle = document.querySelector(".nav-toggle"), links = document.querySelector(".nav-links");
toggle.addEventListener("click", () => { const o = links.classList.toggle("open"); toggle.setAttribute("aria-expanded", o); });
links.addEventListener("click", e => { if (e.target.tagName === "A") links.classList.remove("open"); });

// Open/closed status from opening hours
const HOURS = { 0: null, 1: [7, 17], 2: [7, 17], 3: [7, 17], 4: [7, 17], 5: [7, 17], 6: [8, 14] };
(function () {
  const now = new Date(), h = HOURS[now.getDay()], hr = now.getHours() + now.getMinutes() / 60;
  const el = document.getElementById("open-status"), open = h && hr >= h[0] && hr < h[1];
  el.textContent = open ? "Open now" : "Closed now"; el.classList.add(open ? "open" : "closed");
})();

// Contact form (client-side validation only; sends nothing)
const form = document.getElementById("contact-form"), result = document.getElementById("form-result");
form.addEventListener("submit", e => {
  e.preventDefault(); let ok = true;
  form.querySelectorAll("input,textarea").forEach(f => { const v = f.checkValidity(); f.classList.toggle("invalid", !v); ok = ok && v; });
  if (!ok) { result.style.color = "#b23b3b"; result.textContent = "Please fill in all fields (message: 10+ characters, valid email)."; return; }
  const name = new FormData(form).get("name");
  result.style.color = "#2e7d32";
  result.textContent = `Thanks, ${name}! (Demo only: nothing was sent.)`;
  form.reset();
});
