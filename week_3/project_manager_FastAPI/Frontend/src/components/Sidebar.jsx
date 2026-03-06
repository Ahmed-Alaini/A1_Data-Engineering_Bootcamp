import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <nav className="nav">
        <NavLink to="/users" className={({ isActive }) => (isActive ? "navItem active" : "navItem")}>
          المستخدمون
        </NavLink>
        <NavLink
          to="/projects"
          className={({ isActive }) => (isActive ? "navItem projectItem active" : "navItem projectItem")}
        >
          المشاريع
        </NavLink>
      </nav>
    </aside>
  );
}

