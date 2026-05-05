const roleLabels = {
    "ROLE_MANAGER_CONFIG": "Support",
    "ROLE_MANAGER_FINANCE": "Financial",
    "ROLE_MANAGER_HR": "Human Resources",
    "ROLE_MANAGER_IT": "IT Support",
    "ROLE_MANAGER_MARKETING": "Marketing",
    "ROLE_CUSTOMER_MANAGER_SERVICE": "Customer Service",
    "ROLE_MANAGER_ADMINISTRATIVE": "Administrative"
};

const DEFAULT_AVATAR = "/static/assets/images/defult-admin.png";

const dropdownSVG = `
    <svg width="24" height="6" viewBox="0 0 24 6" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12.0012 0.359985C11.6543 0.359985 11.3109 0.428302 10.9904 0.561035C10.67 0.693767 10.3788 0.888317 10.1335 1.13358C9.88829 1.37883 9.69374 1.67 9.56101 1.99044C9.42828 2.31089 9.35996 2.65434 9.35996 3.00119C9.35996 3.34803 9.42828 3.69148 9.56101 4.01193C9.69374 4.33237 9.88829 4.62354 10.1335 4.8688C10.3788 5.11405 10.67 5.3086 10.9904 5.44134C11.3109 5.57407 11.6543 5.64239 12.0012 5.64239C12.7017 5.64223 13.3734 5.36381 13.8686 4.86837C14.3638 4.37294 14.6419 3.70108 14.6418 3.00059C14.6416 2.3001 14.3632 1.62836 13.8677 1.13315C13.3723 0.637942 12.7004 0.359826 12 0.359985H12.0012ZM3.60116 0.359985C3.25431 0.359985 2.91086 0.428302 2.59042 0.561035C2.26997 0.693767 1.97881 0.888317 1.73355 1.13358C1.48829 1.37883 1.29374 1.67 1.16101 1.99044C1.02828 2.31089 0.959961 2.65434 0.959961 3.00119C0.959961 3.34803 1.02828 3.69148 1.16101 4.01193C1.29374 4.33237 1.48829 4.62354 1.73355 4.8688C1.97881 5.11405 2.26997 5.3086 2.59042 5.44134C2.91086 5.57407 3.25431 5.64239 3.60116 5.64239C4.30165 5.64223 4.97339 5.36381 5.4686 4.86837C5.9638 4.37294 6.24192 3.70108 6.24176 3.00059C6.2416 2.3001 5.96318 1.62836 5.46775 1.13315C4.97231 0.637942 4.30045 0.359826 3.59996 0.359985H3.60116ZM20.4012 0.359985C20.0543 0.359985 19.7109 0.428302 19.3904 0.561035C19.07 0.693767 18.7788 0.888317 18.5336 1.13358C18.2883 1.37883 18.0937 1.67 17.961 1.99044C17.8283 2.31089 17.76 2.65434 17.76 3.00119C17.76 3.34803 17.8283 3.69148 17.961 4.01193C18.0937 4.33237 18.2883 4.62354 18.5336 4.8688C18.7788 5.11405 19.07 5.3086 19.3904 5.44134C19.7109 5.57407 20.0543 5.64239 20.4012 5.64239C21.1017 5.64223 21.7734 5.36381 22.2686 4.86837C22.7638 4.37294 23.0419 3.70108 23.0418 3.00059C23.0416 2.3001 22.7632 1.62836 22.2677 1.13315C21.7723 0.637942 21.1005 0.359826 20.4 0.359985H20.4012Z" fill="#A098AE"/>
    </svg>`;

// ─── Build Card ───────────────────────────────────────────────────────────────
function buildManagerCard(manager) {
    const roles = JSON.parse(manager.roles);
    const roleText = roles.map(r => roleLabels[r] || r).join(", ");
    const id = manager.id || "";
    const avatar = id ? `/api/get_profile_img/${id}` : DEFAULT_AVATAR;

    return `
        <div class="col-xl-3 col-lg-4 col-sm-6">
            <div class="card contact_list text-center">
                <div class="card-body">
                    <div class="user-content">
                        <div class="user-info">
                            <div class="user-img">
                                <img src="${avatar}" alt="" class="avatar avatar-xl"
                                     onerror="this.onerror=null; this.src='${DEFAULT_AVATAR}'">
                            </div>
                            <div class="user-details">
                                <h4 class="user-name mb-0">${manager.full_name}</h4>
                                <p class="long-list">${roleText}</p>
                            </div>
                        </div>
                        <div class="dropdown">
                            <a href="javascript:void(0);" class="btn sharp btn-light"
                               data-bs-toggle="dropdown" aria-expanded="false">
                                ${dropdownSVG}
                            </a>
                            <div class="dropdown-menu dropdown-menu-end">
                                <a data-id="${id}" class="dropdown-item delete-manager" style="cursor:pointer;">Delete</a>
                                <a href="/dashboard/view-manager/${id}" class="dropdown-item">Edit</a>
                                <a href="/dashboard/reset-manager-password/${id}" class="dropdown-item">Reset Password</a>
                            </div>
                        </div>
                    </div>
                    <div class="d-flex justify-content-center mt-3">
                        <button type="button" class="btn btn-dark btn-sm w-50" disabled>
                            <i class="fa-solid fa-user me-2"></i>Profile
                        </button>
                    </div>
                </div>
            </div>
        </div>`;
}

// ─── Load Cards ───────────────────────────────────────────────────────────────
async function loadManagerCards() {
    const container = document.getElementById("managers-row");

    try {
        const res = await fetch("/api/get-manager-info");
        const data = await res.json();

        console.log("API Response:", data);

        if (!res.ok) {
            container.innerHTML = `<p class="text-danger">Failed to load managers.</p>`;
            return;
        }

        container.innerHTML = data.Data.map(buildManagerCard).join("");

    } catch (err) {
        console.error(err);
        container.innerHTML = `<p class="text-danger">Error loading managers.</p>`;
    }
}

// ─── Dropdown Toggle ──────────────────────────────────────────────────────────
document.addEventListener('click', function (e) {
    const toggle = e.target.closest('[data-bs-toggle="dropdown"]');

    if (toggle) {
        e.preventDefault();
        const menu = toggle.nextElementSibling;
        document.querySelectorAll('.dropdown-menu.show').forEach(function (m) {
            if (m !== menu) m.classList.remove('show');
        });
        menu.classList.toggle('show');
    } else if (!e.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu.show').forEach(function (m) {
            m.classList.remove('show');
        });
    }
});

// ─── Delete Manager ───────────────────────────────────────────────────────────
document.addEventListener('click', function (e) {
    const btn = e.target.closest('.delete-manager');
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    const managerId = btn.getAttribute('data-id');

    Swal.fire({
        title: 'Are you sure?',
        html: `This Manager will be deleted permanently.<br>You will not be able to undo this action.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/delete-user/${managerId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.Message === 'Manager Deleted successfully') {
                    Swal.fire({
                        title: 'Deleted!',
                        text: 'The manager has been deleted.',
                        icon: 'success',
                        confirmButtonColor: '#3085d6'
                    }).then(() => {
                        loadManagerCards(); // ✅ reload cards without full page refresh
                    });
                } else {
                    Swal.fire({
                        title: 'Error!',
                        text: data.Message,
                        icon: 'error',
                        confirmButtonColor: '#d33'
                    });
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                Swal.fire({
                    title: 'Error!',
                    text: 'Something went wrong, please try again.',
                    icon: 'error',
                    confirmButtonColor: '#d33'
                });
            });
        }
    });
});

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", loadManagerCards);