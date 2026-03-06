import Sidebar from "./Sidebar.jsx";

export default function Layout({ children }) {
  return (
    <div className="appShell">
      <Sidebar />
      <main className="main">{children}</main>
    </div>
  );
}

