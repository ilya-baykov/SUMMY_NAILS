const state = {
  shiftOpen: false,
  dashboard: {
    medical_book: null,
    education: [],
    portfolio: [],
    appointments: [],
    shift: { is_open: false },
    finance: { balance: 0, operations: [] },
    services: [],
  },
};

const money = new Intl.NumberFormat("ru-RU").format;
const bookingList = document.querySelector("#bookingList");
const portfolioGrid = document.querySelector("#portfolioGrid");
const shiftCard = document.querySelector(".shift-card");
const shiftButton = document.querySelector("#shiftButton");
const shiftTotal = document.querySelector("#shiftTotal");
const closedCount = document.querySelector("#closedCount");
const appointmentsCount = document.querySelector("#appointmentsCount");
const revenue = document.querySelector("#revenue");
const todayHint = document.querySelector("#todayHint");
const balance = document.querySelector("#balance");
const financeList = document.querySelector("#financeList");
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
  if (status === "confirmed" || status === "valid" || status === "closed") {
    return "success";
  }

  if (status === "review" || status === "new") {
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

async function loadDashboard() {
  state.dashboard = await apiFetch("/api/dashboard/");
  state.shiftOpen = state.dashboard.shift.is_open;
  renderAll();
}

function renderBookings() {
  bookingList.innerHTML = "";

  if (state.dashboard.appointments.length === 0) {
    bookingList.innerHTML = `<div class="empty-state">На сегодня записей нет</div>`;
    return;
  }

  state.dashboard.appointments.forEach((appointment) => {
    const isClosed = appointment.status === "closed";
    const item = document.createElement("article");
    item.className = `booking${isClosed ? " closed" : ""}`;
    item.innerHTML = `
      <div class="booking-main">
        <div class="booking-time">
          <span>${appointment.time_display}</span>
          <span class="time-chip">${appointment.service.duration_minutes} мин</span>
        </div>
        <h2>${appointment.client_name}</h2>
        <p>${appointment.service.title} · ${money(appointment.service.price)} ₽</p>
        <p>${appointment.client_phone} · ${appointment.status_display}</p>
      </div>
      <button type="button" ${state.shiftOpen && !isClosed ? "" : "disabled"}>
        ${isClosed ? "Запись закрыта" : "Закрыть запись"}
      </button>
    `;

    item.querySelector("button").addEventListener("click", async () => {
      const data = await apiFetch(`/api/appointments/${appointment.id}/close/`, { method: "POST" });
      state.dashboard.appointments = state.dashboard.appointments.map((record) => (record.id === data.appointment.id ? data.appointment : record));
      state.dashboard.shift = data.shift;
      state.dashboard.finance = data.finance;
      renderToday();
      renderFinance();
    });

    bookingList.append(item);
  });
}

function renderMedicalBook() {
  const medicalBook = state.dashboard.medical_book;

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

  state.dashboard.education.forEach((item) => {
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
      state.dashboard.education = state.dashboard.education.filter((record) => record.id !== item.id);
      renderEducation();
    });

    educationList.append(card);
  });
}

function renderPortfolio() {
  portfolioGrid.innerHTML = "";
  portfolioCount.textContent = state.dashboard.portfolio.length;

  if (state.dashboard.portfolio.length === 0) {
    portfolioGrid.innerHTML = `<div class="empty-state">Добавьте первую работу с фото и подписью</div>`;
    return;
  }

  state.dashboard.portfolio.forEach((work) => {
    const item = document.createElement("article");
    item.className = "work-card";
    item.innerHTML = `
      <img src="${work.image_url}" alt="${work.title}" />
      <button class="icon-button" type="button" aria-label="Удалить работу">×</button>
      <span>${work.title}</span>
    `;

    item.querySelector("button").addEventListener("click", async () => {
      await apiFetch(`/api/portfolio/${work.id}/`, { method: "DELETE" });
      state.dashboard.portfolio = state.dashboard.portfolio.filter((record) => record.id !== work.id);
      renderPortfolio();
    });

    portfolioGrid.append(item);
  });
}

function renderSummary() {
  const closed = state.dashboard.appointments.filter((appointment) => appointment.status === "closed");
  const total = closed.reduce((sum, appointment) => sum + appointment.service.price, 0);

  state.shiftOpen = state.dashboard.shift.is_open;
  shiftCard.classList.toggle("open", state.shiftOpen);
  shiftButton.textContent = state.shiftOpen ? "Закрыть смену" : "Открыть смену";
  shiftCard.querySelector(".status").lastChild.textContent = state.shiftOpen ? " Смена открыта" : " Смена закрыта";
  shiftTotal.textContent = state.shiftOpen ? `${money(total)} ₽` : "—";
  closedCount.textContent = closed.length;
  appointmentsCount.textContent = state.dashboard.appointments.length;
  revenue.textContent = `${money(total)} ₽`;
  todayHint.textContent = state.shiftOpen ? "Закрывайте записи после завершения услуги" : "Чтобы закрывать записи, откройте смену";
}

function renderFinance() {
  balance.textContent = `${money(state.dashboard.finance.balance)} ₽`;
  financeList.innerHTML = "";

  if (state.dashboard.finance.operations.length === 0) {
    financeList.innerHTML = `<div class="empty-state">Финансовых операций пока нет</div>`;
    return;
  }

  state.dashboard.finance.operations.forEach((operation) => {
    const item = document.createElement("article");
    item.className = "operation";
    item.innerHTML = `
      <div>
        <strong>${operation.title}</strong>
        <p>${operation.operation_type_display} · ${operation.created_at_display}</p>
      </div>
      <b class="${operation.amount > 0 ? "positive" : ""}">${operation.amount > 0 ? "+" : ""}${money(operation.amount)} ₽</b>
    `;
    financeList.append(item);
  });
}

function renderToday() {
  renderSummary();
  renderBookings();
}

function renderProfile() {
  renderMedicalBook();
  renderEducation();
}

function renderAll() {
  renderToday();
  renderProfile();
  renderPortfolio();
  renderFinance();
}

document.querySelectorAll("[data-tab]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-tab]").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll("[data-panel]").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(`[data-panel="${button.dataset.tab}"]`).classList.add("active");
  });
});

shiftButton.addEventListener("click", async () => {
  state.dashboard.shift = await apiFetch("/api/shift/toggle/", { method: "POST" });
  renderToday();
});

editMedicalButton.addEventListener("click", () => {
  const medicalBook = state.dashboard.medical_book;

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

  const profile = await apiFetch("/api/profile/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  state.dashboard.medical_book = profile.medical_book;
  state.dashboard.education = profile.education;
  state.dashboard.portfolio = profile.portfolio;
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

  state.dashboard.education.unshift(record);
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

  state.dashboard.portfolio.unshift(work);
  renderPortfolio();
  portfolioForm.classList.add("hidden");
});

loadDashboard();
