import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  ApiError,
  createProject,
  deleteProject,
  getProjects,
  getUsers,
  updateProject
} from "../api/client.js";
import Modal from "../components/Modal.jsx";

export default function ProjectsListPage() {
  const [projects, setProjects] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const [modalMode, setModalMode] = useState(null);
  const [activeProject, setActiveProject] = useState(null);
  const [draft, setDraft] = useState({ name: "", description: "", owner_id: "" });

  const userMap = useMemo(() => {
    const map = new Map();
    (users || []).forEach((user) => map.set(user.id, user));
    return map;
  }, [users]);

  const rows = useMemo(() => projects || [], [projects]);
  const modalOpen = modalMode !== null;

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const [projectData, userData] = await Promise.all([getProjects(), getUsers()]);
      setProjects(projectData || []);
      setUsers(userData || []);
    } catch (event) {
      setError(normalizeError(event));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  function openCreateModal() {
    setModalMode("create");
    setActiveProject(null);
    setDraft({ name: "", description: "", owner_id: "" });
  }

  function openEditModal(project) {
    setModalMode("edit");
    setActiveProject(project);
    setDraft({
      name: project.name || "",
      description: project.description || "",
      owner_id: String(project.owner_id ?? "")
    });
  }

  function closeModal() {
    setModalMode(null);
    setActiveProject(null);
    setDraft({ name: "", description: "", owner_id: "" });
  }

  async function submitModal() {
    const ownerIdNum = Number(draft.owner_id);
    if (!draft.name.trim() || !Number.isFinite(ownerIdNum)) {
      setError("اسم المشروع ومالك المشروع مطلوبان.");
      return;
    }

    setSaving(true);
    setError("");
    try {
      if (modalMode === "create") {
        await createProject({
          name: draft.name.trim(),
          description: draft.description.trim() || null,
          owner_id: ownerIdNum
        });
      } else if (modalMode === "edit" && activeProject) {
        const payload = {};
        if (draft.name.trim() !== activeProject.name) payload.name = draft.name.trim();
        if ((draft.description.trim() || null) !== (activeProject.description || null)) {
          payload.description = draft.description.trim() || null;
        }
        if (ownerIdNum !== activeProject.owner_id) payload.owner_id = ownerIdNum;
        await updateProject(activeProject.id, payload);
      }
      closeModal();
      await refresh();
    } catch (event) {
      setError(normalizeError(event));
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(project) {
    const ok = window.confirm(`هل تريد حذف المشروع: ${project.name}؟`);
    if (!ok) return;
    setError("");
    try {
      await deleteProject(project.id);
      await refresh();
    } catch (event) {
      setError(normalizeError(event));
    }
  }

  function onFormSubmit(event) {
    event.preventDefault();
    submitModal();
  }

  return (
    <section>
      <div className="pageHeader">
        <h1 className="pageTitle">المشاريع</h1>
        <button className="btn primary" type="button" onClick={openCreateModal}>
          إضافة مشروع
        </button>
      </div>

      {error ? <div className="alert">{error}</div> : null}

      <Modal
        open={modalOpen}
        title={modalMode === "edit" ? "تعديل المشروع" : "إضافة مشروع"}
        onClose={closeModal}
      >
        <form className="formStack" onSubmit={onFormSubmit}>
          <div className="formField">
            <label className="formLabel">اسم المشروع</label>
            <input
              className="input"
              placeholder="أدخل اسم المشروع"
              value={draft.name}
              onChange={(event) => setDraft((prev) => ({ ...prev, name: event.target.value }))}
            />
          </div>

          <div className="formField">
            <label className="formLabel">الوصف</label>
            <textarea
              className="input textarea"
              placeholder="اكتب وصفًا مختصرًا للمشروع"
              value={draft.description}
              onChange={(event) => setDraft((prev) => ({ ...prev, description: event.target.value }))}
            />
          </div>

          <div className="formField">
            <label className="formLabel">مالك المشروع</label>
            <select
              className="input"
              value={draft.owner_id}
              onChange={(event) => setDraft((prev) => ({ ...prev, owner_id: event.target.value }))}
            >
              <option value="">اختر المالك</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.username} ({user.id})
                </option>
              ))}
            </select>
          </div>

          <div className="formActions">
            <button className="btn" type="button" onClick={closeModal}>
              إلغاء
            </button>
            <button className="btn primary" type="submit" disabled={saving}>
              {modalMode === "edit" ? "حفظ التعديلات" : "إنشاء مشروع"}
            </button>
          </div>
        </form>
      </Modal>

      {loading ? (
        <div className="muted">جارٍ التحميل...</div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>المعرّف</th>
                <th>اسم المشروع</th>
                <th>المالك</th>
                <th className="actionsCol">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((project) => (
                <tr key={project.id}>
                  <td>{project.id}</td>
                  <td>
                    <Link to={`/projects/${project.id}`}>{project.name}</Link>
                  </td>
                  <td>{userMap.get(project.owner_id)?.username || project.owner_id}</td>
                  <td className="actions">
                    <button className="btn" type="button" onClick={() => openEditModal(project)}>
                      تعديل
                    </button>
                    <button className="btn danger" type="button" onClick={() => onDelete(project)}>
                      حذف
                    </button>
                  </td>
                </tr>
              ))}
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={4} className="muted center">
                    لا توجد مشاريع.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function normalizeError(event) {
  if (event instanceof ApiError) return `${event.status}: ${event.message}`;
  return event?.message || "حدث خطأ غير معروف";
}
