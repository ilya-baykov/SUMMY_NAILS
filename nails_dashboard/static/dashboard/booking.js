const bookingForm = document.querySelector("#bookingForm");
const bookingService = document.querySelector("#bookingService");
const bookingResult = document.querySelector("#bookingResult");

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(";").shift() : "";
}

async function loadServices() {
  const response = await fetch("/api/public-booking/");
  const data = await response.json();
  bookingService.innerHTML = data.services
    .map((service) => `<option value="${service.id}">${service.title} · ${service.price} ₽ · ${service.duration_minutes} мин</option>`)
    .join("");
}

bookingForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const response = await fetch("/api/public-booking/", {
    method: "POST",
    headers: { "X-CSRFToken": getCookie("csrftoken") },
    body: new FormData(bookingForm),
  });

  if (!response.ok) {
    bookingResult.textContent = "Не удалось создать запись";
    return;
  }

  const appointment = await response.json();
  bookingForm.reset();
  bookingResult.textContent = `Запись создана: ${appointment.date_display} в ${appointment.time_display}`;
});

loadServices();
