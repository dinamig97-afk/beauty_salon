const times = [
    "10:00","11:00","12:00","13:00",
    "14:00","15:00","16:00","17:00"
];

document.getElementById("date").addEventListener("change", async function() {
    const date = this.value;

    const res = await fetch(`/slots?date=${date}`);
    const busy = await res.json();

    const select = document.getElementById("time");
    select.innerHTML = "";

    times.forEach(t => {
        if (!busy.includes(t)) {
            select.innerHTML += `<option>${t}</option>`;
        }
    });
});
