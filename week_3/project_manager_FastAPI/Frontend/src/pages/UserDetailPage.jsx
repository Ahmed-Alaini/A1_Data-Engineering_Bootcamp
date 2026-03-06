import { Link, useParams } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { ApiError, getProjects, getTasks, getUser } from "../api/client.js";

export default function UserDetailPage() {
  const { userId } = useParams();
  const id = Number(userId);

  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const projectMap = useMemo(() => {
    const m = new Map();
    (projects || []).forEach((p) => m.set(p.id, p));
    return m;
  }, [projects]);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const [u, t, p] = await Promise.all([getUser(id), getTasks({ assignee_id: id }), getProjects()]);
        setUser(u);
        setTasks(t || []);
        setProjects(p || []);
      } catch (e) {
        setError(normalizeError(e));
      } finally {
        setLoading(false);
      }
    }
    if (Number.isFinite(id)) load();
  }, [id]);

  return (
    <section>
      <div className="pageHeader">
        <h1 className="pageTitle">تفاصيل المستخدم</h1>
        <Link className="btn" to="/users">
          رجوع
        </Link>
      </div>

      {error ? <div className="alert">{error}</div> : null}
      {loading ? (
        <div className="muted">جارٍ التحميل...</div>
      ) : user ? (
        <>
          <div className="card">
            <div className="kv">
              <div className="k">المعرّف</div>
              <div className="v">{user.id}</div>
              <div className="k">اسم المستخدم</div>
              <div className="v">{user.username}</div>
              <div className="k">البريد الإلكتروني</div>
              <div className="v">{user.email}</div>
            </div>
          </div>

          <h2 className="sectionTitle">المهام المسندة</h2>
          <div className="card">
            <table className="table">
              <thead>
                <tr>
                  <th>المعرّف</th>
                  <th>العنوان</th>
                  <th>المشروع</th>
                  <th>مكتملة</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((t) => (
                  <tr key={t.id}>
                    <td>{t.id}</td>
                    <td>{t.title}</td>
                    <td>
                      {projectMap.get(t.project_id) ? (
                        <Link to={`/projects/${t.project_id}`}>{projectMap.get(t.project_id).name}</Link>
                      ) : (
                        t.project_id
                      )}
                    </td>
                    <td>{t.completed ? "نعم" : "لا"}</td>
                  </tr>
                ))}
                {tasks.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="muted center">
                      لا توجد مهام.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <div className="muted">المستخدم غير موجود.</div>
      )}
    </section>
  );
}

function normalizeError(e) {
  if (e instanceof ApiError) return `${e.status}: ${e.message}`;
  return e?.message || "حدث خطأ غير معروف";
}
