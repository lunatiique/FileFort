import React from "react";
import { Menu, Image } from "semantic-ui-react";
import { Link } from 'react-router-dom';
import './components.css';
import { useAuth } from './UserAuthentification';

const Header = () => {
  const { user } = useAuth();

  return (
    <>
      <Menu className="sticky-header">
        <Link to="/">
          <Image src="logo512.png" alt="logo" className="iconImg" />
        </Link>
        {user ? <><Link to="/cipher/encode">
          <a className="item">Encode</a>
        </Link>
        <Link to="/user/uploadFile">
          <a className="item">Upload File</a>
        </Link>
        <Link to="/user/downloadFile">
          <a className="item">Download File</a>
        </Link></> : null}
        
      </Menu>
      <Menu className="sticky-header-right">
        <Menu.Menu position="right">
          {user ? <Link to="/user/logout" className="item">Logout</Link> : 
          <>
            <Link to="/user/register" className="item">
              Register
            </Link>
            <Link to="/user/login" className="item">
              Login
            </Link>
          </>}
          
        </Menu.Menu>
      </Menu>
    </>
  );
};

export default Header;
