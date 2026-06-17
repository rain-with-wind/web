/* ===================================
   学生信息管理系统 - 前端交互逻辑
   =================================== */

// 后端 API 地址（Docker 部署时用 backend 服务名，本地开发用 localhost）
const API_BASE = "http://localhost:8000/api";

let currentPage = 1;
let currentKeyword = "";
let deleteTargetId = null;

// ============================
// 初始化
// ============================
document.addEventListener("DOMContentLoaded", () => {
    loadStudents();
    bindEvents();
});

function bindEvents() {
    document.getElementById("searchBtn").addEventListener("click", onSearch);
    document.getElementById("searchInput").addEventListener("keydown", (e) => {
        if (e.key === "Enter") onSearch();
    });
    document.getElementById("addBtn").addEventListener("click", openAddModal);
    document.getElementById("modalClose").addEventListener("click", closeModal);
    document.getElementById("cancelBtn").addEventListener("click", closeModal);
    document.getElementById("modalOverlay").addEventListener("click", (e) => {
        if (e.target === e.currentTarget) closeModal();
    });
    document.getElementById("studentForm").addEventListener("submit", onSubmitForm);
    document.getElementById("confirmCancel").addEventListener("click", closeConfirm);
    document.getElementById("confirmDelete").addEventListener("click", doDelete);
    document.getElementById("confirmOverlay").addEventListener("click", (e) => {
        if (e.target === e.currentTarget) closeConfirm();
    });
}

// ============================
// 加载学生列表
// ============================
async function loadStudents() {
    const tbody = document.getElementById("tableBody");
    tbody.innerHTML = '<tr class="empty-row"><td colspan="10">加载中...</td></tr>';

    try {
        const params = new URLSearchParams({
            page: currentPage,
            page_size: 20,
            keyword: currentKeyword,
        });
        const res = await fetch(`${API_BASE}/students?${params}`);
        if (!res.ok) throw new Error("请求失败");

        const result = await res.json();
        renderTable(result.data);
        renderPagination(result.total, result.page, result.page_size);
    } catch (err) {
        tbody.innerHTML = `<tr class="empty-row"><td colspan="10">加载失败: ${err.message}</td></tr>`;
    }
}

function renderTable(students) {
    const tbody = document.getElementById("tableBody");

    if (students.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="10">暂无数据</td></tr>';
        return;
    }

    tbody.innerHTML = students
        .map(
            (s) => `
        <tr>
            <td>${s.id}</td>
            <td>${escapeHtml(s.name)}</td>
            <td>${escapeHtml(s.gender)}</td>
            <td>${s.age}</td>
            <td>${escapeHtml(s.major)}</td>
            <td>${escapeHtml(s.class_name)}</td>
            <td>${escapeHtml(s.phone)}</td>
            <td>${escapeHtml(s.email)}</td>
            <td>${s.created_at}</td>
            <td>
                <button class="btn-edit" onclick="openEditModal(${s.id})">编辑</button>
                <button class="btn-del" onclick="openConfirm(${s.id}, '${escapeHtml(s.name)}')">删除</button>
            </td>
        </tr>`
        )
        .join("");
}

function renderPagination(total, page, pageSize) {
    const totalPages = Math.ceil(total / pageSize);
    const pagination = document.getElementById("pagination");

    if (totalPages <= 1) {
        pagination.innerHTML = total > 0 ? `<span>共 ${total} 条记录</span>` : "";
        return;
    }

    let html = "";
    html += `<button ${page <= 1 ? "disabled" : ""} onclick="goToPage(${page - 1})">上一页</button>`;

    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= page - 2 && i <= page + 2)) {
            html += `<button class="${i === page ? "active" : ""}" onclick="goToPage(${i})">${i}</button>`;
        } else if (i === page - 3 || i === page + 3) {
            html += "<span>...</span>";
        }
    }

    html += `<button ${page >= totalPages ? "disabled" : ""} onclick="goToPage(${page + 1})">下一页</button>`;
    html += `<span>共 ${total} 条</span>`;

    pagination.innerHTML = html;
}

function goToPage(page) {
    currentPage = page;
    loadStudents();
}

// ============================
// 搜索
// ============================
function onSearch() {
    currentKeyword = document.getElementById("searchInput").value.trim();
    currentPage = 1;
    loadStudents();
}

// ============================
// 新增学生
// ============================
function openAddModal() {
    document.getElementById("modalTitle").textContent = "新增学生";
    document.getElementById("studentForm").reset();
    document.getElementById("studentId").value = "";
    document.getElementById("modalOverlay").classList.add("active");
}

async function openEditModal(id) {
    try {
        const res = await fetch(`${API_BASE}/students/${id}`);
        if (!res.ok) throw new Error("学生不存在");

        const s = await res.json();
        document.getElementById("modalTitle").textContent = "编辑学生";
        document.getElementById("studentId").value = s.id;
        document.getElementById("name").value = s.name;
        document.getElementById("gender").value = s.gender;
        document.getElementById("age").value = s.age;
        document.getElementById("major").value = s.major;
        document.getElementById("className").value = s.class_name;
        document.getElementById("phone").value = s.phone;
        document.getElementById("email").value = s.email;
        document.getElementById("modalOverlay").classList.add("active");
    } catch (err) {
        alert("获取学生信息失败: " + err.message);
    }
}

function closeModal() {
    document.getElementById("modalOverlay").classList.remove("active");
}

async function onSubmitForm(e) {
    e.preventDefault();

    const id = document.getElementById("studentId").value;
    const data = {
        name: document.getElementById("name").value.trim(),
        gender: document.getElementById("gender").value,
        age: parseInt(document.getElementById("age").value) || 20,
        major: document.getElementById("major").value.trim(),
        class_name: document.getElementById("className").value.trim(),
        phone: document.getElementById("phone").value.trim(),
        email: document.getElementById("email").value.trim(),
    };

    if (!data.name) {
        alert("姓名不能为空");
        return;
    }

    try {
        const url = id ? `${API_BASE}/students/${id}` : `${API_BASE}/students`;
        const method = id ? "PUT" : "POST";
        const res = await fetch(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "操作失败");
        }

        closeModal();
        loadStudents();
    } catch (err) {
        alert("操作失败: " + err.message);
    }
}

// ============================
// 删除学生
// ============================
function openConfirm(id, name) {
    deleteTargetId = id;
    document.getElementById("deleteName").textContent = name;
    document.getElementById("confirmOverlay").classList.add("active");
}

function closeConfirm() {
    deleteTargetId = null;
    document.getElementById("confirmOverlay").classList.remove("active");
}

async function doDelete() {
    if (!deleteTargetId) return;

    try {
        const res = await fetch(`${API_BASE}/students/${deleteTargetId}`, {
            method: "DELETE",
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "删除失败");
        }

        closeConfirm();
        loadStudents();
    } catch (err) {
        alert("删除失败: " + err.message);
    }
}

// ============================
// 工具函数
// ============================
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
}
