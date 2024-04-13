document.addEventListener('DOMContentLoaded', function () {

    const isActiveCheckbox = document.getElementById('isActiveFilter');

    function fetchUsers() {
        const isActive = isActiveCheckbox.checked;

        fetch(`/accounts/list?is_active=${isActive}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                const magistratesTab = document.querySelector('.magistrates-list');
                const parentsTab = document.querySelector('.parents-list');

                magistratesTab.innerHTML = '';
                parentsTab.innerHTML = '';

                //Magistrate
                data.magistrates.forEach(magistrate => {
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-user-id', magistrate.id); // ID
                    tr.innerHTML = `<td><img src="${magistrate.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td><td>${magistrate.last_name}</td><td>${magistrate.first_name}</td><td>${magistrate.email}</td><td>${magistrate.role}</td><td>${magistrate.parents_count}</td>`;
                    magistratesTab.appendChild(tr);
                });

                //Parent
                data.parents.forEach(parent => {
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-user-id', parent.id); //ID
                    tr.innerHTML = `<td><img src="${parent.profile_image_url}" alt="Profile Image" width="30" height="30" class="rounded-circle"></td><td>${parent.last_name}</td><td>${parent.first_name}</td><td>${parent.email}</td><td>${parent.magistrates_assigned.join('<br>')}</td>`;
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
    isActiveCheckbox.addEventListener('change', fetchUsers); // active filtering

    setInterval(fetchUsers, 10000);
});
