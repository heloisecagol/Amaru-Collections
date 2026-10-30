/*
 * Shared behaviour: nav state, mobile menu, pre-order bag, product cards,
 * product gallery, reveal-on-scroll, light parallax and the waitlist form.
 */
(function () {
  const cfg = window.AMARU_CONFIG || {};
  const locale = document.documentElement.lang || cfg.defaultLocale || "en";
  const base = document.documentElement.dataset.base || ""; // "../" on nested pages
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const tr = (field) => (field && (field[locale] || field.en)) || "";
  const money = new Intl.NumberFormat(locale, {
    style: "currency",
    currency: cfg.currency || "EUR",
    maximumFractionDigits: 0,
  });

  document.documentElement.classList.remove("no-js");

  /* ---- Navigation: transparent over hero, solid black on scroll ---- */
  const nav = document.getElementById("site-nav");
  const hero = document.querySelector(".hero");
  if (hero) document.body.classList.add("has-hero");

  function updateNav() {
    if (!nav) return;
    nav.classList.toggle("is-solid", window.scrollY > 24);
  }
  updateNav();
  window.addEventListener("scroll", updateNav, { passive: true });

  /* ---- Mobile menu ---- */
  const toggle = document.querySelector(".menu-toggle");
  const menu = document.getElementById("mobile-menu");
  function setMenu(open) {
    nav.classList.toggle("is-open", open);
    menu.classList.toggle("is-open", open);
    menu.setAttribute("aria-hidden", String(!open));
    toggle.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("menu-open", open);
  }
  if (toggle && menu) {
    toggle.addEventListener("click", () => setMenu(!menu.classList.contains("is-open")));
    menu.addEventListener("click", (e) => e.target.closest("a") && setMenu(false));
    document.addEventListener("keydown", (e) => e.key === "Escape" && setMenu(false));
  }

  /* ---- Pre-order bag (localStorage until Stripe checkout is connected) ---- */
  const CART_KEY = "amaru-cart";
  function readCart() {
    try {
      return JSON.parse(localStorage.getItem(CART_KEY) || "[]");
    } catch (_) {
      return [];
    }
  }
  function updateCartCount() {
    const count = readCart().reduce((n, item) => n + (item.qty || 0), 0);
    document.querySelectorAll("[data-cart-count]").forEach((el) => {
      el.textContent = count;
      el.hidden = count === 0;
    });
  }
  function addToCart(id) {
    const cart = readCart();
    const line = cart.find((item) => item.id === id);
    if (line) line.qty += 1;
    else cart.push({ id, qty: 1 });
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    updateCartCount();
  }
  updateCartCount();
  window.addEventListener("storage", updateCartCount);

  document.querySelectorAll("[data-add-to-cart]").forEach((btn) => {
    const status = document.querySelector("[data-cart-status]");
    btn.addEventListener("click", () => {
      addToCart(btn.dataset.addToCart);
      if (status) {
        status.hidden = false;
        status.textContent = "";
        // Re-set the text so screen readers announce it on every click.
        requestAnimationFrame(() => (status.textContent = status.dataset.message));
      }
    });
  });

  /* ---- Product cards: collection grid and "You may also like" ---- */
  const products = window.AMARU_PRODUCTS || [];
  // Jewelry is always shown on black: the product photo where there is one.
  function card(p) {
    const name = tr(p.name);
    const culture = p.culture ? tr(p.culture) : "";
    const tag = p.url ? "a" : "div";
    const href = p.url ? ` href="${base}${p.url}"` : "";
    return `
      <${tag} class="piece reveal"${href}>
        <div class="piece__tile">
          <img class="piece__img" src="${base}${p.hero || p.image}" alt="${name}${culture ? ", " + culture : ""}" loading="lazy">
        </div>
        <div class="piece__meta">
          <h3 class="piece__name">${name}</h3>
          <p class="piece__row">
            <span>${money.format(p.price)} <span class="ph">[PLACEHOLDER]</span></span>
            <span class="tag">Pre-order</span>
          </p>
        </div>
      </${tag}>`;
  }

  const grid = document.querySelector("[data-collection]");
  if (grid) grid.innerHTML = products.map(card).join("");

  const related = document.querySelector("[data-related]");
  if (related) {
    const current = related.dataset.related;
    related.innerHTML = products
      .filter((p) => p.id !== current)
      .map(card)
      .join("");
  }

  /* ---- Product gallery: swipe on phones, dots follow the visible image ---- */
  document.querySelectorAll("[data-gallery]").forEach((gallery) => {
    const track = gallery.querySelector(".gallery__track");
    const dots = Array.from(gallery.querySelectorAll(".gallery__dots button"));
    if (!track || !dots.length) return;
    const slides = Array.from(track.children);
    dots.forEach((dot, i) =>
      dot.addEventListener("click", () =>
        track.scrollTo({ left: slides[i].offsetLeft - track.offsetLeft, behavior: reduceMotion ? "auto" : "smooth" })
      )
    );
    track.addEventListener(
      "scroll",
      () => {
        const i = Math.round(track.scrollLeft / track.clientWidth);
        dots.forEach((d, j) => d.setAttribute("aria-current", String(i === j)));
      },
      { passive: true }
    );
  });

  /* ---- Reveal on scroll ---- */
  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("is-visible"));
  }

  /* ---- Light parallax: objects drift a few pixels relative to the page ---- */
  const drifters = Array.from(document.querySelectorAll("[data-parallax]"));
  if (drifters.length && !reduceMotion) {
    let ticking = false;
    function drift() {
      const vh = window.innerHeight;
      drifters.forEach((el) => {
        const speed = parseFloat(el.dataset.parallax) || 0.06;
        const rect = el.getBoundingClientRect();
        const offset = rect.top + rect.height / 2 - vh / 2;
        el.style.transform = `translate3d(0, ${(-offset * speed).toFixed(1)}px, 0)`;
      });
      ticking = false;
    }
    window.addEventListener(
      "scroll",
      () => {
        if (!ticking) {
          ticking = true;
          requestAnimationFrame(drift);
        }
      },
      { passive: true }
    );
    drift();
  }

  /* ---- Waitlist form → Supabase ---- */
  document.querySelectorAll("[data-waitlist]").forEach((form) => {
    const error = form.querySelector(".form__error");
    const button = form.querySelector("button[type=submit]");
    const emailInput = form.querySelector("input[name=email]");
    const done = document.getElementById(form.dataset.waitlist);

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      error.textContent = "";
      emailInput.removeAttribute("aria-invalid");

      const data = new FormData(form);
      if (data.get("company")) return; // honeypot: silently drop bots

      const email = String(data.get("email") || "").trim();
      const name = String(data.get("name") || "").trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        emailInput.setAttribute("aria-invalid", "true");
        error.textContent = "Please enter a valid email address.";
        emailInput.focus();
        return;
      }

      button.disabled = true;
      const original = button.textContent;
      button.textContent = "Sending…";

      try {
        await saveSignup({ email, name: name || null, locale, source: form.dataset.source || "landing" });
        if (name && done) {
          const greet = done.querySelector("[data-greet]");
          if (greet) greet.textContent = `Thank you, ${name}.`;
        }
        form.hidden = true;
        if (done) {
          done.hidden = false;
          done.focus();
        }
      } catch (err) {
        console.error(err);
        error.textContent = "Something went wrong on our side. Please try again in a moment.";
        button.disabled = false;
        button.textContent = original;
      }
    });
  });

  async function saveSignup(row) {
    if (!cfg.supabaseUrl || !cfg.supabaseAnonKey) {
      // Not connected yet: keep sign-ups locally so the flow can be tested.
      console.warn("[Amaru] Supabase is not configured in js/config.js — sign-up stored locally only.", row);
      const list = JSON.parse(localStorage.getItem("amaru-waitlist-dev") || "[]");
      list.push({ ...row, created_at: new Date().toISOString() });
      localStorage.setItem("amaru-waitlist-dev", JSON.stringify(list));
      return;
    }
    const res = await fetch(`${cfg.supabaseUrl}/rest/v1/waitlist`, {
      method: "POST",
      headers: {
        apikey: cfg.supabaseAnonKey,
        Authorization: `Bearer ${cfg.supabaseAnonKey}`,
        "Content-Type": "application/json",
        Prefer: "return=minimal",
      },
      body: JSON.stringify(row),
    });
    // 409 = email already on the list: treat as success, no need to tell anyone twice.
    if (!res.ok && res.status !== 409) {
      throw new Error(`Supabase insert failed: ${res.status} ${await res.text()}`);
    }
  }
})();
