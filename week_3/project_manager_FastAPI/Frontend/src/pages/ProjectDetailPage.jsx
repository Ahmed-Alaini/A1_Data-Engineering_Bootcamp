import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, createTask, getProject, getTasks, getUsers } from "../api/client.js";
import Modal from "../components/Modal.jsx";

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const id = Number(projectId);

  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [saving, setSaving] = useState(false);

  const [showCreateTaskModal, setShowCreateTaskModal] = useState(false);
  const [taskDraft, setTaskDraft] = useState({
    title: "",
    description: "",
    assignee_id: "",
    completed: false
  });

  const userMap = useMemo(() => {
    const map = new Map();
    (users || []).forEach((user) => map.set(user.id, user));
    return map;
  }, [users]);

  async function refresh() {
    setLoading(true);
    setError("");
    setNotFound(false);
    try {
      const projectData = await getProject(id);
      const [tasksResult, usersResult] = await Promise.allSettled([
        getTasks({ project_id: id }),
        getUsers()
      ]);

      setProject(projectData);
      if (tasksResult.status === "fulfilled") {
        setTasks(tasksResult.value || []);
      } else {
        setTasks([]);
        setError(normalizeError(tasksResult.reason));
      }

      if (usersResult.status === "fulfilled") {
        setUsers(usersResult.value || []);
      } else {
        setUsers([]);
        setError((prev) =>
          prev ? `${prev} | ${normalizeError(usersResult.reason)}` : normalizeError(usersResult.reason)
        );
      }
    } catch (event) {
      if (event instanceof ApiError && event.status === 404) {
        setNotFound(true);
        setProject(null);
      } else {
        setError(normalizeError(event));
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (Number.isFinite(id)) refresh();
  }, [id]);

  function openCreateTaskModal() {
    setTaskDraft({
      title: "",
      description: "",
      assignee_id: "",
      completed: false
    });
    setShowCreateTaskModal(true);
  }

  function closeCreateTaskModal() {
    setShowCreateTaskModal(false);
  }

  async function onCreateTask() {
    if (!taskDraft.title.trim()) {
      setError("عنوان المهمة مطلوب.");
      return;
    }

    const assigneeId = taskDraft.assignee_id ? Number(taskDraft.assignee_id) : null;

    setSaving(true);
    setError("");
    try {
      await createTask({
        title: taskDraft.title.trim(),
        description: taskDraft.description.trim() || null,
        completed: taskDraft.completed,
        project_id: id,
        assignee_id: Number.isFinite(assigneeId) ? assigneeId : null
      });
      closeCreateTaskModal();
      await refresh();
    } catch (event) {
      setError(normalizeError(event));
    } finally {
      setSaving(false);
    }
  }

  function onFormSubmit(event) {
    event.preventDefault();
    onCreateTask();
  }

  return (
    <section>
      <div className="pageHeader">
        <h1 className="pageTitle">تفاصيل المشروع</h1>
        <Link className="btn" to="/projects">
          رجوع
        </Link>
      </div>

      {error ? <div className="alert">{error}</div> : null}
      {loading ? (
        <div className="muted">جارٍ التحميل...</div>
      ) : notFound ? (
        <div className="muted">المشروع غير موجود.</div>
      ) : project ? (
        <>
          <div className="card">
            <div className="kv">
              <div className="k">المعرّف</div>
              <div className="v">{project.id}</div>
              <div className="k">اسم المشروع</div>
              <div className="v">{project.name}</div>
              <div className="k">المالك</div>
              <div className="v">
                {userMap.get(project.owner_id) ? (
                  <Link to={`/users/${project.owner_id}`}>{userMap.get(project.owner_id).username}</Link>
                ) : (
                  project.owner_id
                )}
              </div>
              <div className="k">الوصف</div>
              <div className="v">{project.description || "-"}</div>
            </div>
          </div>

          <div className="pageHeader sectionHeader">
            <h2 className="sectionTitle">المهام</h2>
            <button className="btn primary" type="button" onClick={openCreateTaskModal}>
              إضافة مهمة
            </button>
          </div>

          <Modal open={showCreateTaskModal} title="إضافة مهمة" onClose={closeCreateTaskModal}>
            <form className="formStack" onSubmit={onFormSubmit}>
              <div className="formField">
                <label className="formLabel">عنوان المهمة</label>
                <input
                  className="input"
                  placeholder="أدخل عنوان المهمة"
                  value={taskDraft.title}
                  onChange={(event) => setTaskDraft((prev) => ({ ...prev, title: event.target.value }))}
                />
              </div>

              <div className="formField">
                <label className="formLabel">الوصف</label>
                <textarea
                  className="input textarea"
                  placeholder="أدخل وصف المهمة"
                  value={taskDraft.description}
                  onChange={(event) => setTaskDraft((prev) => ({ ...prev, description: event.target.value }))}
                />
              </div>

              <div className="formField">
                <label className="formLabel">المستخدم المُسند إليه</label>
                <select
                  className="input"
                  value={taskDraft.assignee_id}
                  onChange={(event) => setTaskDraft((prev) => ({ ...prev, assignee_id: event.target.value }))}
                >
                  <option value="">غير مسندة</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.username} ({user.id})
                    </option>
                  ))}
                </select>
              </div>

              <label className="checkboxLine">
                <input
                  type="checkbox"
                  checked={taskDraft.completed}
                  onChange={(event) => setTaskDraft((prev) => ({ ...prev, completed: event.target.checked }))}
                />
                مهمة مكتملة
              </label>

              <div className="formActions">
                <button className="btn" type="button" onClick={closeCreateTaskModal}>
                  إلغاء
                </button>
                <button className="btn primary" type="submit" disabled={saving}>
                  إنشاء مهمة
                </button>
              </div>
            </form>
          </Modal>

          <div className="card">
            <table className="table">
              <thead>
                <tr>
                  <th>المعرّف</th>
                  <th>العنوان</th>
                  <th>المُسند إليه</th>
                  <th>مكتملة</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.id}>
                    <td>{task.id}</td>
                    <td>{task.title}</td>
                    <td>
                      {task.assignee_id ? (
                        <Link to={`/users/${task.assignee_id}`}>
                          {userMap.get(task.assignee_id)?.username || `مستخدم ${task.assignee_id}`}
                        </Link>
                      ) : (
                        <span className="muted">غير مسندة</span>
                      )}
                    </td>
                    <td>{task.completed ? "نعم" : "لا"}</td>
                  </tr>
                ))}
                {tasks.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="muted center">
                      لا توجد مهام في هذا المشروع.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </section>
  );
}

function normalizeError(event) {
  if (event instanceof ApiError) return `${event.status}: ${event.message}`;
  return event?.message || "حدث خطأ غير معروف";
}
