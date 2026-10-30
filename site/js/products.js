/*
 * The pre-sale collection: seven earrings.
 * Single source of truth for the landing page, shop grid and product pages.
 *
 * Translatable fields are keyed by locale ({ en: "...", fr: "...", es: "..." })
 * so French and Spanish can be added without touching the markup.
 *
 * name    = "Earring 01" … "Earring 06" until the real names are supplied.
 *           The seventh piece, the Calima nariguera, has its own hand-written page.
 * culture = null until confirmed (the photo file names hint at one; see comments).
 * Museum, date and archaeological original are not filled in until confirmed.
 * url     = product page, relative to the site root. Pages for earring-01 … 06 are generated
 *           by scripts/build_product_pages.py — re-run it after changing a name or price.
 *
 * hero    = photo on black, used on cards and as the product page image.
 * image   = transparent cut-out (kept for later use).
 * Image paths are relative to the site root; scripts prefix them for nested pages.
 */
window.AMARU_PRODUCTS = [
  {
    id: "earring-01",
    name: { en: "Earring 01" }, // [PLACEHOLDER] real name
    culture: null, // photo file name suggests Tairona — not shown until confirmed
    price: 145, // [PLACEHOLDER] EUR
    image: "assets/earrings/earring-01.png",
    hero: "assets/products/earring-01/hero.jpg", // product page hero, on black
    url: "shop/earring-01.html",
    modelImage: null, // e.g. "assets/model/earring-01.jpg" — enables hover swap
  },
  {
    id: "earring-02",
    name: { en: "Earring 02" }, // [PLACEHOLDER] real name
    culture: null, // photo file name suggests Zenú — not shown until confirmed
    price: 95, // [PLACEHOLDER] EUR
    image: "assets/earrings/earring-02.png",
    hero: "assets/products/earring-02/hero.jpg", // product page hero, on black
    url: "shop/earring-02.html",
    modelImage: null, // e.g. "assets/model/earring-02.jpg" — enables hover swap
  },
  {
    id: "earring-03",
    name: { en: "Earring 03" }, // [PLACEHOLDER] real name
    culture: null, // photo file name suggests Quimbaya — not shown until confirmed
    price: 120, // [PLACEHOLDER] EUR
    image: "assets/earrings/earring-03.png",
    hero: "assets/products/earring-03/hero.jpg", // product page hero, on black
    url: "shop/earring-03.html",
    modelImage: null, // e.g. "assets/model/earring-03.jpg" — enables hover swap
  },
  {
    id: "earring-04",
    name: { en: "Earring 04" }, // [PLACEHOLDER] real name
    culture: null, // photo file name suggests Zenú — not shown until confirmed
    price: 240, // [PLACEHOLDER] EUR
    image: "assets/earrings/earring-04.png",
    hero: "assets/products/earring-04/hero.jpg", // product page hero, on black
    url: "shop/earring-04.html",
    modelImage: null, // e.g. "assets/model/earring-04.jpg" — enables hover swap
  },
  {
    id: "earring-05",
    name: { en: "Earring 05" }, // [PLACEHOLDER] real name
    culture: null, // photo file name suggests Zenú — not shown until confirmed
    price: 210, // [PLACEHOLDER] EUR
    image: "assets/earrings/earring-05.png",
    hero: "assets/products/earring-05/hero.jpg", // product page hero, on black
    url: "shop/earring-05.html",
    modelImage: null, // e.g. "assets/model/earring-05.jpg" — enables hover swap
  },
  {
    id: "earring-06",
    name: { en: "Earring 06" }, // [PLACEHOLDER] real name
    culture: null, // photo file name suggests Zenú — not shown until confirmed
    price: 320, // [PLACEHOLDER] EUR
    image: "assets/earrings/earring-06.png",
    hero: "assets/products/earring-06/hero.jpg", // product page hero, on black
    url: "shop/earring-06.html",
    modelImage: null, // e.g. "assets/model/earring-06.jpg" — enables hover swap
  },
  {
    id: "calima-nariguera",
    name: { en: "Nariguera Earrings" }, // [PLACEHOLDER] final name
    culture: { en: "Calima" },
    price: 180, // [PLACEHOLDER] EUR
    image: "assets/products/calima-nariguera/worn.webp",
    hero: "assets/products/calima-nariguera/hero.webp",
    url: "shop/calima-nariguera.html",
  },
];
