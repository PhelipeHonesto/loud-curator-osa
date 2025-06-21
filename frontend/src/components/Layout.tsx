import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Layout = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="app-container">
      <nav className="main-nav">
        <div className="nav-logo">
          <img src="/logo.jpeg" alt="Orange Sunshine Aviation Logo" />
          <span>Orange Sunshine Aviation</span>
        </div>
        <ul>
          <li><Link to="/">Feed</Link></li>
          <li><Link to="/saved">Saved</Link></li>
          <li><Link to="/drafts">Drafts</Link></li>
          <li><Link to="/settings">Settings</Link></li>
        </ul>
        <div className="nav-user">
          <span className="username">Welcome, {user?.username}</span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </nav>
      <main className="content-area">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
