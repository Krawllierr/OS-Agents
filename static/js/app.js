// Funções globais para edição e exclusão de projetos
function editProject(id) {
    console.log('Edit project', id);
    // Implementar lógica de edição
}

function deleteProject(id) {
    console.log('Delete project', id);
    // Implementar lógica de exclusão
}

document.addEventListener('DOMContentLoaded', () => {
    const projectList = document.getElementById('projects');
    const newProjectForm = document.getElementById('newProjectForm');
    const errorMessage = document.getElementById('errorMessage');

    async function login(username, password) {
        const response = await fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
    
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            // Redirecionar ou atualizar a UI conforme necessário
        } else {
            showError('Login failed');
        }
    }

    async function fetchProjects() {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(projectData),
            });
            if (response.ok) {
                const projects = await response.json();
                displayProjects(projects);
            } else {
                throw new Error('Failed to fetch projects');
            }
        } catch (error) {
            showError(error.message);
        }
    }
    

    function displayProjects(projects) {
        projectList.innerHTML = '';
        projects.forEach(project => {
            const projectElement = document.createElement('div');
            projectElement.classList.add('project-card');
            projectElement.innerHTML = `
                <h3>${project.name}</h3>
                <p>${project.description}</p>
                <p>Deadline: ${new Date(project.deadline).toLocaleString()}</p>
                <p>Status: ${project.status}</p>
                <p>Current Phase: ${project.current_phase}</p>
                <button onclick="editProject(${project.id})">Edit</button>
                <button onclick="deleteProject(${project.id})">Delete</button>
            `;
            projectList.appendChild(projectElement);
        });
    }

    newProjectForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(newProjectForm);
        const projectData = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData),
            });

            if (response.ok) {
                const newProject = await response.json();
                showSuccess('Project created successfully');
                newProjectForm.reset();
                fetchProjects();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create project');
            }
        } catch (error) {
            showError(error.message);
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.color = 'red';
        errorMessage.style.display = 'block';
    }

    function showSuccess(message) {
        errorMessage.textContent = message;
        errorMessage.style.color = 'green';
        errorMessage.style.display = 'block';
    }

    // Inicializar a lista de projetos
    fetchProjects();
});