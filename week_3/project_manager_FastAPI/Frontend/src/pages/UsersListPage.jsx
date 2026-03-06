import { useEffect, useMemo, useState } from "react";
import { ApiError, createUser, deleteUser, getUsers, updateUser } from "../api/client.js";
import Modal from "../components/Modal.jsx";

export default function UsersListPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const [modalMode, setModalMode] = useState(null);
  const [activeUser, setActiveUser] = useState(null);
  const [draft, setDraft] = useState({ username: "", email: "" });

  const rows = useMemo(() => users || [], [users]);
  const modalOpen = modalMode !== null;

  async function refresh() {
    setLoading(true);
    setError("");
    try {
      const data = await getUsers();
      setUsers(data || []);
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
    setActiveUser(null);
    setDraft({ username: "", email: "" });
  }

  function openEditModal(user) {
    setModalMode("edit");
    setActiveUser(user);
    setDraft({ username: user.username || "", email: user.email || "" });
  }

  function closeModal() {
    setModalMode(null);
    setActiveUser(null);
    setDraft({ username: "", email: "" });
  }

  async function submitModal() {
    if (!draft.username.trim() || !draft.email.trim()) {
      setError("اسم المستخدم والبريد الإلكتروني مطلوبان.");
      return;
    }

    setSaving(true);
    setError("");
    try {
      if (modalMode === "create") {
        await createUser({
          username: draft.username.trim(),
          email: draft.email.trim()
        });
      } else if (modalMode === "edit" && activeUser) {
        const payload = {};
        if (draft.username.trim() !== activeUser.username) payload.username = draft.username.trim();
        if (draft.email.trim() !== activeUser.email) payload.email = draft.email.trim();
        await updateUser(activeUser.id, payload);
      }
      closeModal();
      await refresh();
    } catch (event) {
      setError(normalizeError(event));
    } finally {
      setSaving(false);
    }
  }

  async function onDelete(user) {
    const ok = window.confirm(`هل تريد حذف المستخدم: ${user.username}؟`);
    if (!ok) return;
    setError("");
    try {
      await deleteUser(user.id);
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
        <h1 className="pageTitle">المستخدمون</h1>
        <button className="btn primary" type="button" onClick={openCreateModal}>
          إضافة مستخدم
        </button>
      </div>

      {error ? <div className="alert">{error}</div> : null}

      <Modal
        open={modalOpen}
        title={modalMode === "edit" ? "تعديل المستخدم" : "إضافة مستخدم"}
        onClose={closeModal}
      >
        <form className="formStack" onSubmit={onFormSubmit}>
          <div className="formField">
            <label className="formLabel">اسم المستخدم</label>
            <input
              className="input"
              placeholder="أدخل اسم المستخدم"
              value={draft.username}
              onChange={(event) => setDraft((prev) => ({ ...prev, username: event.target.value }))}
            />
          </div>

          <div className="formField">
            <label className="formLabel">البريد الإلكتروني</label>
            <input
              className="input"
              placeholder="name@example.com"
              value={draft.email}
              onChange={(event) => setDraft((prev) => ({ ...prev, email: event.target.value }))}
            />
          </div>

          <div className="formActions">
            <button className="btn" type="button" onClick={closeModal}>
              إلغاء
            </button>
            <button className="btn primary" type="submit" disabled={saving}>
              {modalMode === "edit" ? "حفظ التعديلات" : "إنشاء مستخدم"}
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
                <th>اسم المستخدم</th>
                <th>البريد الإلكتروني</th>
                <th className="actionsCol">الإجراءات</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((user) => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.username}</td>
                  <td>{user.email}</td>
                  <td className="actions">
                    <button className="btn" type="button" onClick={() => openEditModal(user)}>
                      تعديل
                    </button>
                    <button className="btn danger" type="button" onClick={() => onDelete(user)}>
                      حذف
                    </button>
                  </td>
                </tr>
              ))}
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={4} className="muted center">
                    لا يوجد مستخدمون.
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
