const state = {
  services: [],
  appointments: [],
  finance: { balance: 0, operations: [] },
};

const money = new Intl.NumberFormat("ru-RU").format;
const serviceForm = document.querySelector("#serviceForm");
const serviceList = document.querySelector("#serviceList");
const staffService = document.querySelector("#staffService");
const staffAppointmentForm = document.querySelector("#staffAppointmentForm");
const staffAppointmentList = document.querySelector("#staffAppointmentList");
const payoutForm = document.querySelector("#payoutForm");
const staffFinanceList = document.querySelector("#staffFinanceList");

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(";").shift() : "";
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

async function loadManage() {
  const data = await apiFetch("/api/manage/");
  state.services = data.services;
  state.appointments = data.appointments;
  state.finance = data.finance;
  renderAll();
}

function renderServices() {
  serviceList.innerHTML = "";
  staffService.innerHTML = state.services
    .filter((service) => service.is_active)
    .map((service) => `<option value="${service.id}">${service.title}</option>`)
    .join("");

  state.services.forEach((service) => {
    const item = document.createElement("article");
    item.className = "info-card";
    item.innerHTML = `
      <div>
        <strong>${service.title}</strong>
        <p>${service.duration_minutes} мин · ${money(service.price)} ₽ · ${service.is_active ? "активна" : "скрыта"}</p>
      </div>
      ${service.is_active ? `<button class="icon-button" type="button" aria-label="Скрыть услугу">×</button>` : ""}
    `;

    const button = item.querySelector("button");
    if (button) {
      button.addEventListener("click", async () => {
        await apiFetch(`/api/manage/services/${service.id}/`, { method: "DELETE" });
        service.is_active = false;
        renderServices();
      });
    }

    serviceList.append(item);
  });
}

function renderAppointments() {
  staffAppointmentList.innerHTML = "";

  if (state.appointments.length === 0) {
    staffAppointmentList.innerHTML = `<div class="empty-state">Записей пока нет</div>`;
    return;
  }

  state.appointments.forEach((appointment) => {
    const item = document.createElement("article");
    item.className = "info-card";
    item.innerHTML = `
      <div>
        <strong>${appointment.date_display} ${appointment.time_display} · ${appointment.client_name}</strong>
        <p>${appointment.service.title} · ${appointment.client_phone} · ${appointment.status_display}</p>
      </div>
      <span class="pill ${appointment.status === "closed" ? "success" : "warn"}">${appointment.status_display}</span>
    `;
    staffAppointmentList.append(item);
  });
}

function renderFinance() {
  if (!staffFinanceList) {
    return;
  }

  staffFinanceList.innerHTML = "";

  if (state.finance.operations.length === 0) {
    staffFinanceList.innerHTML = `<div class="empty-state">Финансовых операций пока нет</div>`;
    return;
  }

  state.finance.operations.forEach((operation) => {
    const item = document.createElement("article");
    item.className = "operation";
    item.innerHTML = `
      <div>
        <strong>${operation.title}</strong>
        <p>${operation.operation_type_display} · ${operation.created_at_display}</p>
      </div>
      <b class="${operation.amount > 0 ? "positive" : ""}">${operation.amount > 0 ? "+" : ""}${money(operation.amount)} ₽</b>
    `;
    staffFinanceList.append(item);
  });
}

function renderAll() {
  renderServices();
  renderAppointments();
  renderFinance();
}

serviceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const service = await apiFetch("/api/manage/services/", { method: "POST", body: new FormData(serviceForm) });
  state.services.push(service);
  serviceForm.reset();
  renderServices();
});

staffAppointmentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const appointment = await apiFetch("/api/manage/appointments/", { method: "POST", body: new FormData(staffAppointmentForm) });
  state.appointments.push(appointment);
  staffAppointmentForm.reset();
  renderAppointments();
});

if (payoutForm) {
  payoutForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const operation = await apiFetch("/api/manage/payouts/", { method: "POST", body: new FormData(payoutForm) });
    state.finance.operations.unshift(operation);
    state.finance.balance += operation.amount;
    payoutForm.reset();
    renderFinance();
  });
}

loadManage();
