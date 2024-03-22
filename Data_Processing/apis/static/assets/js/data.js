
// PATIENTJOURNEY
// Responsivle ofr presenting user personal data
export async function update_column() {
  try {
   // alert(`http://127.0.0.1:5000/patient/?sub_id=${subId}`)
    const response = await fetch(`http://127.0.0.1:8000/patient/?sub_id=${subId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
  
  const data = await response.json();
  console.log(data);
  const table = document.getElementById('table_id_3');
  const tbody = table.querySelector('tbody');

  tbody.innerHTML = '';


  data.forEach(row => {
    const tr = document.createElement('tr');

    const tdSubjectId = document.createElement('td');
    tdSubjectId.textContent = row.subject_id;
    tr.appendChild(tdSubjectId);

    const tdAnchorAge = document.createElement('td');
    tdAnchorAge.textContent = row.anchor_age;
    tr.appendChild(tdAnchorAge);

    const tdGender = document.createElement('td');
    tdGender.textContent = row.gender;
    tr.appendChild(tdGender);

    const tdDodUpdated = document.createElement('td');
    tdDodUpdated.textContent = row.dod_updated;
    tr.appendChild(tdDodUpdated);

    tbody.appendChild(tr);
});
  } catch (error) {
    console.error('Error:', error);
  }
  
}



