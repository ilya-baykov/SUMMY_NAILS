const bookings = [
  { id: 1, time: "10:00", duration: "120 мин", client: "Мария С.", service: "Маникюр + покрытие гель-лак", price: 3200, closed: false },
  { id: 2, time: "12:30", duration: "150 мин", client: "Ольга Д.", service: "Снятие + укрепление + дизайн", price: 4100, closed: false },
  { id: 3, time: "15:30", duration: "90 мин", client: "Виктория П.", service: "Маникюр комбинированный", price: 2400, closed: false },
  { id: 4, time: "17:30", duration: "130 мин", client: "Елена Т.", service: "Френч + ремонт 2 ногтей", price: 3600, closed: false },
];

const state = {
  shiftOpen: false,
  profile: {
    medical_book: null,
    education: [],
    portfolio: [],
  },
};

const money = new Intl.NumberFormat("ru-RU").format;
const bookingList = document.querySelector("#bookingList");
const portfolioGrid = document.querySelector("#portfolioGrid");
const shiftCard = document.querySelector(".shift-card");
const shiftButton = document.querySelector("#shiftButton");
const shiftTotal = document.querySelector("#shiftTotal");
const closedCount = document.querySelector("#closedCount");
const revenue = document.querySelector("#revenue");
const todayHint = document.querySelector("#todayHint");
const medicalCard = document.querySelector("#medicalCard");
const medicalForm = document.querySelector("#medicalForm");
const editMedicalButton = document.querySelector("#editMedicalButton");
const cancelMedicalButton = document.querySelector("#cancelMedicalButton");
const educationList = document.querySelector("#educationList");
const educationForm = document.querySelector("#educationForm");
const showEducationFormButton = document.querySelector("#showEducationFormButton");
const cancelEducationButton = document.querySelector("#cancelEducationButton");
const portfolioCount = document.querySelector("#portfolioCount");
const portfolioForm = document.querySelector("#portfolioForm");
const addWorkButton = document.querySelector("#addWorkButton");
const cancelPortfolioButton = document.querySelector("#cancelPortfolioButton");

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);

  if (parts.length === 2) {
    return parts.pop().split(";").shift();
  }

  return "";
}

function getStatusClass(status) {
  if (status === "confirmed" || status === "valid") {
    return "success";
  }

  if (status === "review") {
    return "warn";
  }

  return "danger";
}

async function apiFetch(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

async function loadProfile() {
  state.profile = await apiFetch("/api/profile/");
  renderProfile();
  renderPortfolio();
}

function renderBookings() {
  bookingList.innerHTML = "";

  bookings.forEach((booking) => {
    const item = document.createElement("article");
    item.className = `booking${booking.closed ? " closed" : ""}`;
    item.innerHTML = `
      <div class="booking-main">
        <div class="booking-time">
          <span>${booking.time}</span>
          <span class="time-chip">${booking.duration}</span>
        </div>
        <h2>${booking.client}</h2>
        <p>${booking.service} · ${money(booking.price)} ₽</p>
      </div>
      <button type="button" ${state.shiftOpen || booking.closed ? "" : "disabled"}>
        ${booking.closed ? "Запись закрыта" : "Закрыть запись"}
      </button>
    `;

    item.querySelector("button").addEventListener("click", () => {
      booking.closed = true;
      renderToday();
    });

    bookingList.append(item);
  });
}

function renderMedicalBook() {
  const medicalBook = state.profile.medical_book;

  if (!medicalBook) {
    return;
  }

  medicalCard.innerHTML = `
    <div>
      <strong>${medicalBook.number}</strong>
      <p>Действует до ${medicalBook.valid_until_display}</p>
    </div>
    <span class="pill ${getStatusClass(medicalBook.status)}">${medicalBook.status_display}</span>
  `;
}

function renderEducation() {
  educationList.innerHTML = "";

  state.profile.education.forEach((item) => {
    const card = document.createElement("article");
    card.className = "info-card";
    card.innerHTML = `
      <div>
        <strong>${item.record_type_display} · ${item.title}</strong>
        <p>${item.issuer} · ${item.year}</p>
      </div>
      <div class="card-actions">
        <span class="pill ${getStatusClass(item.status)}">${item.status_display}</span>
        <button class="icon-button" type="button" aria-label="Удалить запись">×</button>
      </div>
    `;

    card.querySelector("button").addEventListener("click", async () => {
      await apiFetch(`/api/education/${item.id}/`, { method: "DELETE" });
      state.profile.education = state.profile.education.filter((record) => record.id !== item.id);
      renderEducation();
    });

    educationList.append(card);
  });
}

function renderPortfolio() {
  portfolioGrid.innerHTML = "";
  portfolioCount.textContent = state.profile.portfolio.length;

  if (state.profile.portfolio.length === 0) {
    portfolioGrid.innerHTML = `<div class="empty-state">Добавьте первую работу с фото и подписью</div>`;
    return;
  }

  state.profile.portfolio.forEach((work) => {
    const item = document.createElement("article");
    item.className = "work-card";
    item.innerHTML = `
      <img src="${work.image_url}" alt="${work.title}" />
      <button class="icon-button" type="button" aria-label="Удалить работу">×</button>
      <span>${work.title}</span>
    `;

    item.querySelector("button").addEventListener("click", async () => {
      await apiFetch(`/api/portfolio/${work.id}/`, { method: "DELETE" });
      state.profile.portfolio = state.profile.portfolio.filter((record) => record.id !== work.id);
      renderPortfolio();
    });

    portfolioGrid.append(item);
  });
}

function renderSummary() {
  const closed = bookings.filter((booking) => booking.closed);
  const total = closed.reduce((sum, booking) => sum + booking.price, 0);

  shiftCard.classList.toggle("open", state.shiftOpen);
  shiftButton.textContent = state.shiftOpen ? "Закрыть смену" : "Открыть смену";
  shiftCard.querySelector(".status").lastChild.textContent = state.shiftOpen ? " Смена открыта" : " Смена закрыта";
  shiftTotal.textContent = state.shiftOpen ? `${money(total)} ₽` : "—";
  closedCount.textContent = closed.length;
  revenue.textContent = `${money(total)} ₽`;
  todayHint.textContent = state.shiftOpen ? "Закрывайте записи после завершения услуги" : "Чтобы закрывать записи, откройте смену";
}

function renderToday() {
  renderSummary();
  renderBookings();
}

function renderProfile() {
  renderMedicalBook();
  renderEducation();
}

document.querySelectorAll("[data-tab]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-tab]").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll("[data-panel]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(`[data-panel="${button.dataset.tab}"]`).classList.add("active");
  });
});

shiftButton.addEventListener("click", () => {
  state.shiftOpen = !state.shiftOpen;
  renderToday();
});

editMedicalButton.addEventListener("click", () => {
  const medicalBook = state.profile.medical_book;

  medicalForm.elements.namedItem("number").value = medicalBook.number;
  medicalForm.elements.namedItem("valid_until").value = medicalBook.valid_until;
  medicalForm.elements.namedItem("status").value = medicalBook.status;
  medicalForm.classList.remove("hidden");
});

cancelMedicalButton.addEventListener("click", () => {
  medicalForm.classList.add("hidden");
});

medicalForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    number: medicalForm.elements.namedItem("number").value.trim(),
    valid_until: medicalForm.elements.namedItem("valid_until").value,
    status: medicalForm.elements.namedItem("status").value,
  };

  state.profile = await apiFetch("/api/profile/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  renderProfile();
  medicalForm.classList.add("hidden");
});

showEducationFormButton.addEventListener("click", () => {
  educationForm.reset();
  educationForm.classList.remove("hidden");
  educationForm.elements.namedItem("title").focus();
});

cancelEducationButton.addEventListener("click", () => {
  educationForm.classList.add("hidden");
});

educationForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const record = await apiFetch("/api/education/", {
    method: "POST",
    body: new FormData(educationForm),
  });

  state.profile.education.unshift(record);
  renderEducation();
  educationForm.classList.add("hidden");
});

addWorkButton.addEventListener("click", () => {
  portfolioForm.reset();
  portfolioForm.classList.remove("hidden");
  portfolioForm.elements.namedItem("image").focus();
});

cancelPortfolioButton.addEventListener("click", () => {
  portfolioForm.classList.add("hidden");
});

portfolioForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const work = await apiFetch("/api/portfolio/", {
    method: "POST",
    body: new FormData(portfolioForm),
  });

  state.profile.portfolio.unshift(work);
  renderPortfolio();
  portfolioForm.classList.add("hidden");
});

renderToday();
loadProfile();
