async function find_string() {
    let word = document.getElementById("input-substring");
    const source = await fetch('http://127.0.0.1:5000/autocomplete?word=' + word.value)
    const data = await source.json()
    let strContainer = document.getElementById("choice");
    strContainer.innerHTML=""
    for (let i=0; i<data.length; i++) {
        let string = document.createElement("H3");
        string.textContent += data[i];
        strContainer.appendChild(string);
    }
}