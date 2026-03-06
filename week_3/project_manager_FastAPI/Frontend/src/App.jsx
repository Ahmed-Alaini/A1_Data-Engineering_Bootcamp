import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import ProjectsListPage from "./pages/ProjectsListPage.jsx";
import ProjectDetailPage from "./pages/ProjectDetailPage.jsx";
import UsersListPage from "./pages/UsersListPage.jsx";
import UserDetailPage from "./pages/UserDetailPage.jsx";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/users" replace />} />
        <Route path="/users" element={<UsersListPage />} />
        <Route path="/users/:userId" element={<UserDetailPage />} />
        <Route path="/projects" element={<ProjectsListPage />} />
        <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
        <Route path="*" element={<Navigate to="/users" replace />} />
      </Routes>
    </Layout>
  );
}

