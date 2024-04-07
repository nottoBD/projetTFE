document.addEventListener('DOMContentLoaded', function () {
    function fetchUsers() {
        fetch('/accounts/list', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                const magistratsTab = document.querySelector('.magistrats-list');
                const parentsTab = document.querySelector('.parents-list');

                magistratsTab.innerHTML = '';
                parentsTab.innerHTML = '';

                //Magistrat
                data.magistrats.forEach(magistrat => {
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-user-id', magistrat.id); // ID
                    tr.innerHTML = `<td><img src="${magistrat.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td><td>${magistrat.last_name}</td><td>${magistrat.first_name}</td><td>${magistrat.email}</td><td>${magistrat.role}</td><td>${magistrat.parents_count}</td>`;
                    magistratsTab.appendChild(tr);
                });

                //Parent
                data.parents.forEach(parent => {
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-user-id', parent.id); //ID
                    tr.innerHTML = `<td><img src="${parent.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td><td>${parent.last_name}</td><td>${parent.first_name}</td><td>${parent.email}</td><td>${parent.assigned_magistrats.join('<br>')}</td>`;
                    parentsTab.appendChild(tr);
                });
            })
            .catch(error => console.error('Fetch error:', error));
    }

    let clickTimeout;

    document.querySelector('.container-fluid').addEventListener('click', function(event) {
        let targetRow = event.target.closest('tr[data-user-id]');
        if (targetRow) {
            clearTimeout(clickTimeout);
            clickTimeout = setTimeout(function() {
                if (!event.ctrlKey) {
                    // highlight
                    document.querySelectorAll('tr[data-user-id]').forEach(row => {
                        row.classList.remove('highlight');
                    });
                }
                targetRow.classList.toggle('highlight');
            }, 200); //double click
        }
    });

    document.querySelector('.container-fluid').addEventListener('dblclick', function(event) {
        clearTimeout(clickTimeout);
        let targetRow = event.target.closest('tr[data-user-id]');
        if (targetRow) {
            let userId = targetRow.getAttribute('data-user-id');
            window.location.href = `/accounts/update/${userId}/`;
        }
    });

    fetchUsers(); // initial
    setInterval(fetchUsers, 10000);
});
