/*
 * Shared navigation + footer, injected into every page so they live in one place.
 * Pages provide <header id="site-header"></header> and <footer id="site-footer"></footer>.
 * Strings are grouped per locale so FR/ES can be added later.
 */
(function () {
  const cfg = window.AMARU_CONFIG || {};
  const base = document.documentElement.dataset.base || ""; // e.g. "../" for nested pages
  const locale = document.documentElement.lang || cfg.defaultLocale || "en";

  const STRINGS = {
    en: {
      skip: "Skip to content",
      nav: [
        { href: "shop.html", label: "Shop", key: "shop" },
        { href: "our-story.html", label: "Our Story", key: "story" },
        { href: "craftsmanship.html", label: "Craftsmanship", key: "craft" },
        { href: "our-commitments.html", label: "Our Commitments", key: "commitments" },
      ],
      cart: "Cart",
      menu: "Menu",
      tagline: "Ancestral Colombian goldwork, made again by living hands.",
      explore: "Explore",
      contact: "Contact",
      care: "Pre-order",
      careLinks: [
        { href: "shop.html", label: "Shop the pre-sale" },
        { href: "index.html#waitlist", label: "Join the waitlist" },
        { href: "shipping.html", label: "Shipping & returns [PLACEHOLDER]" },
        { href: "faq.html", label: "FAQ [PLACEHOLDER]" },
      ],
      rights: "Amaru Collections",
      legal: "Handmade in Colombia",
      menuNote: "Pre-sale now open · Collection I",
    },
  };
  const t = STRINGS[locale] || STRINGS.en;
  const page = document.body.dataset.page || "";
  const year = new Date().getFullYear();

  const cartIcon =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.1" aria-hidden="true">' +
    '<path d="M5 8h14l-1.2 12H6.2L5 8Z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/></svg>';

  const navItems = t.nav
    .map(
      (n) =>
        `<li><a href="${base}${n.href}"${n.key === page ? ' aria-current="page"' : ""}>${n.label}</a></li>`
    )
    .join("");

  const header = document.getElementById("site-header");
  if (header) {
    header.outerHTML = `
      <a class="skip-link" href="#main">${t.skip}</a>
      <nav class="site-nav" id="site-nav" aria-label="Main">
        <a class="wordmark" href="${base}index.html" aria-label="Amaru Collections, home">Amaru<small>Collections</small></a>
        <ul class="nav-links">${navItems}</ul>
        <div class="nav-actions">
          <a class="icon-btn" href="${base}cart.html" aria-label="${t.cart}">
            ${cartIcon}<span class="cart-count" data-cart-count hidden>0</span>
          </a>
          <button class="icon-btn menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="${t.menu}">
            <span class="bars"><span class="bar"></span><span class="bar"></span></span>
          </button>
        </div>
      </nav>
      <div class="mobile-menu" id="mobile-menu" aria-hidden="true">
        <ul>${navItems}</ul>
        <p class="caption">${t.menuNote}</p>
      </div>`;
  }

  const footer = document.getElementById("site-footer");
  if (footer) {
    footer.outerHTML = `
      <footer class="site-footer">
        <div class="footer-grid">
          <div class="footer-brand">
            <a class="wordmark" href="${base}index.html">Amaru<small>Collections</small></a>
            <p>${t.tagline}</p>
          </div>
          <div class="footer-col">
            <h2>${t.explore}</h2>
            <ul>
              <li><a href="${base}index.html">Home</a></li>
              ${t.nav.map((n) => `<li><a href="${base}${n.href}">${n.label}</a></li>`).join("")}
            </ul>
          </div>
          <div class="footer-col">
            <h2>${t.care}</h2>
            <ul>${t.careLinks.map((l) => `<li><a href="${base}${l.href}">${l.label}</a></li>`).join("")}</ul>
          </div>
          <div class="footer-col">
            <h2>${t.contact}</h2>
            <ul>
              <li><a href="${cfg.instagram}" target="_blank" rel="noopener">Instagram ${cfg.instagramHandle}</a></li>
              <li><a href="mailto:${cfg.email}">${cfg.email}</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-base">
          <p class="caption">© ${year} ${t.rights}</p>
          <p class="caption">${t.legal}</p>
        </div>
      </footer>`;
  }
})();
